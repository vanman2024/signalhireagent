"""
CSV export service for processing and exporting SignalHire data.

This service handles CSV data processing, validation, and export functionality
using pandas for efficient data manipulation and formatting.
"""

import csv
from contextlib import suppress
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

# NOTE: This implementation uses pandas for better performance and features
try:
    import pandas as pd

    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

from src.models.prospect import Prospect


@dataclass
class ExportConfig:
    """Configuration for CSV export operations."""

    output_path: str
    include_headers: bool = True
    delimiter: str = ","
    encoding: str = "utf-8"
    include_timestamp: bool = True
    add_timestamp_to_filename: bool = True
    timestamp_format: str = "%Y%m%d_%H%M%S"
    max_rows: int | None = None
    chunk_size: int = 1000


@dataclass
class ExportResult:
    """Result from a CSV export operation."""

    file_path: str
    total_rows: int
    total_columns: int
    file_size_bytes: int
    export_duration_seconds: float
    success: bool
    error_message: str | None = None


class CSVExportError(Exception):
    """Custom exception for CSV export errors."""


class CSVExporter:
    """
    CSV export service for SignalHire data processing.
    Handles conversion of prospect data, contact information, and operation
    results into properly formatted CSV files for analysis and CRM import.
    """

    def __init__(self, config: ExportConfig | None = None):
        self.config = config or ExportConfig(output_path="export.csv")
        self._column_mappings = self._init_column_mappings()
        self._data_validators = self._init_data_validators()

    def _generate_timestamped_filename(
        self, base_path: str, timestamp: datetime | None = None
    ) -> str:
        """
        Generate a filename with timestamp if configured.
        Args:
            base_path: Original file path
            timestamp: Optional timestamp to use (defaults to current time)
        Returns:
            Path with timestamp inserted before file extension if enabled
        """
        if not self.config.add_timestamp_to_filename:
            return base_path

        timestamp = timestamp or datetime.now()
        timestamp_str = timestamp.strftime(self.config.timestamp_format)

        path = Path(base_path)
        name_without_ext = path.stem
        extension = path.suffix

        timestamped_name = f"{name_without_ext}_{timestamp_str}{extension}"
        return str(path.parent / timestamped_name)

    def _init_column_mappings(self) -> dict[str, str]:
        """Initialize column name mappings for consistent output."""
        return {
            # Prospect fields
            "uid": "ID",
            "full_name": "Full Name",
            "first_name": "First Name",
            "last_name": "Last Name",
            "current_title": "Job Title",
            "current_company": "Company",
            "company_size": "Company Size",
            "industry": "Industry",
            "location": "Location",
            "linkedin_url": "LinkedIn URL",
            "profile_url": "Profile URL",
            # Legacy fields for backward compatibility
            "name": "Full Name",
            "title": "Job Title",
            "company": "Company",
            # Contact fields
            "primary_email": "Email",
            "all_emails": "All Emails",
            "primary_phone": "Phone",
            "all_phones": "All Phones",
            "email": "Email",
            "phone": "Phone",
            "linkedin": "LinkedIn",
            # Experience fields
            "total_experience_years": "Years of Experience",
            # Education fields
            "education_level": "Education Level",
            "university": "University",
            "degree": "Degree",
            "field_of_study": "Field of Study",
            # Metadata fields
            "reveal_timestamp": "Revealed Date",
            "credits_used": "Credits Used",
            "data_quality_score": "Data Quality",
        }

    def _init_data_validators(self) -> dict[str, callable]:
        """Initialize data validation functions."""
        return {
            "email": self._validate_email,
            "phone": self._validate_phone,
            "url": self._validate_url,
            "date": self._validate_date,
        }

    def export_to_csv(self, prospects: list[Prospect], output_path: Path):
        """
        Legacy method for backward compatibility.
        Exports a list of Prospect objects to a CSV file.

        Args:
            prospects: A list of Prospect objects.
            output_path: The path to the output CSV file.
        """
        if not prospects:
            return

        prospect_dicts = [self._prospect_to_dict(p) for p in prospects]

        df = pd.DataFrame(prospect_dicts)

        # Define the order of columns in the CSV file
        column_order = [
            "name",
            "title",
            "company",
            "location",
            "email",
            "phone",
            "linkedin",
        ]
        df = df.reindex(columns=column_order)

        df.to_csv(output_path, index=False)

    def export_prospects(
        self,
        prospects: list[dict[str, Any]],
        contacts: dict[str, dict[str, Any]] | None = None,
        experiences: dict[str, list[dict[str, Any]]] | None = None,
        education: dict[str, list[dict[str, Any]]] | None = None,
    ) -> ExportResult:
        """
        Export prospect data to CSV with optional contact and experience data.
        Args:
            prospects: List of prospect dictionaries
            contacts: Optional contact info mapped by prospect_id
            experiences: Optional experience data mapped by prospect_id
            education: Optional education data mapped by prospect_id
        Returns:
            ExportResult with export statistics
        """
        start_time = datetime.now()

        try:
            if HAS_PANDAS:
                return self._export_prospects_pandas(
                    prospects, contacts, experiences, education, start_time
                )
            return self._export_prospects_native(
                prospects, contacts, experiences, education, start_time
            )

        except (OSError, csv.Error) as e:
            duration = (datetime.now() - start_time).total_seconds()
            return ExportResult(
                file_path=self.config.output_path,
                total_rows=0,
                total_columns=0,
                file_size_bytes=0,
                export_duration_seconds=duration,
                success=False,
                error_message=str(e),
            )

    def export_operation_results(
        self, operations: list[dict[str, Any]]
    ) -> ExportResult:
        """
        Export operation results and statistics to CSV.
        Args:
            operations: List of operation dictionaries (SearchOp, RevealOp, etc.)
        Returns:
            ExportResult with export statistics
        """
        start_time = datetime.now()

        try:
            if HAS_PANDAS:
                return self._export_operations_pandas(operations, start_time)
            return self._export_operations_native(operations, start_time)

        except (OSError, csv.Error) as e:
            duration = (datetime.now() - start_time).total_seconds()
            return ExportResult(
                file_path=self.config.output_path,
                total_rows=0,
                total_columns=0,
                file_size_bytes=0,
                export_duration_seconds=duration,
                success=False,
                error_message=str(e),
            )

    def export_signalhire_csv(
        self,
        signalhire_csv_path: str,
        enhanced_data: dict[str, dict[str, Any]] | None = None,
    ) -> ExportResult:
        """
        Process and enhance a CSV file exported from SignalHire's web interface.
        Args:
            signalhire_csv_path: Path to the original SignalHire CSV export
            enhanced_data: Additional data to merge (keyed by prospect identifier)
        Returns:
            ExportResult with processing statistics
        """
        start_time = datetime.now()

        try:
            if HAS_PANDAS:
                return self._export_signalhire_csv_pandas(
                    signalhire_csv_path, enhanced_data, start_time
                )
            return self._export_signalhire_csv_native(
                signalhire_csv_path, enhanced_data, start_time
            )

        except (OSError, csv.Error) as e:
            duration = (datetime.now() - start_time).total_seconds()
            return ExportResult(
                file_path=self.config.output_path,
                total_rows=0,
                total_columns=0,
                file_size_bytes=0,
                export_duration_seconds=duration,
                success=False,
                error_message=str(e),
            )

    def _export_prospects_pandas(
        self,
        prospects: list[dict[str, Any]],
        contacts: dict[str, dict[str, Any]] | None,
        experiences: dict[str, list[dict[str, Any]]] | None,
        education: dict[str, list[dict[str, Any]]] | None,
        start_time: datetime,
    ) -> ExportResult:
        """Export prospects using pandas DataFrame."""
        # Convert to DataFrame
        df = self._create_prospects_dataframe(
            prospects, contacts, experiences, education
        )

        # Apply column mappings
        df = self._apply_column_mappings(df)

        # Add metadata columns if configured
        if self.config.include_timestamp:
            df['Export Date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Limit rows if specified
        if self.config.max_rows:
            df = df.head(self.config.max_rows)

        # Export to CSV
        return self._write_dataframe_to_csv(df, start_time)

    def _export_operations_pandas(
        self, operations: list[dict[str, Any]], start_time: datetime
    ) -> ExportResult:
        """Export operations using pandas DataFrame."""
        # Convert operations to DataFrame
        df = pd.DataFrame(operations)

        # Add computed fields
        if 'created_at' in df.columns and 'completed_at' in df.columns:
            with suppress(Exception):  # Handle invalid date formats gracefully
                df['duration_minutes'] = pd.to_datetime(
                    df['completed_at']
                ) - pd.to_datetime(df['created_at'])
                df['duration_minutes'] = df['duration_minutes'].dt.total_seconds() / 60

        # Format timestamp columns
        timestamp_columns = ['created_at', 'started_at', 'completed_at']
        for col in timestamp_columns:
            if col in df.columns:
                with suppress(Exception):  # Handle invalid timestamps gracefully
                    df[col] = pd.to_datetime(df[col]).dt.strftime('%Y-%m-%d %H:%M:%S')

        # Export to CSV
        return self._write_dataframe_to_csv(df, start_time)

    def _export_signalhire_csv_pandas(
        self,
        signalhire_csv_path: str,
        enhanced_data: dict[str, dict[str, Any]] | None,
        start_time: datetime,
    ) -> ExportResult:
        """Process SignalHire CSV using pandas."""
        # Read the SignalHire CSV
        df = pd.read_csv(signalhire_csv_path, encoding='utf-8')

        # Apply column mappings
        df = self._apply_column_mappings(df)

        # Merge enhanced data if provided
        if enhanced_data:
            df = self._merge_enhanced_data(df, enhanced_data)

        # Export processed data
        return self._write_dataframe_to_csv(df, start_time)

    def _create_prospects_dataframe(
        self,
        prospects: list[dict[str, Any]],
        contacts: dict[str, dict[str, Any]] | None,
        experiences: dict[str, list[dict[str, Any]]] | None,
        education: dict[str, list[dict[str, Any]]] | None,
    ) -> pd.DataFrame:
        """Create a comprehensive DataFrame from prospect data."""
        rows = []

        for prospect in prospects:
            row = prospect.copy()
            prospect_id = prospect.get('uid', prospect.get('id', ''))

            # Add contact information
            if contacts and prospect_id in contacts:
                contact_info = contacts[prospect_id]
                row.update(self._flatten_contact_info(contact_info))

            # Add experience information
            if experiences and prospect_id in experiences:
                experience_list = experiences[prospect_id]
                row.update(self._flatten_experience_info(experience_list))

            # Add education information
            if education and prospect_id in education:
                education_list = education[prospect_id]
                row.update(self._flatten_education_info(education_list))

            rows.append(row)

        return pd.DataFrame(rows)

    def _flatten_contact_info(self, contact_info: dict[str, Any]) -> dict[str, Any]:
        """Flatten contact information for CSV export."""
        flattened = {}

        contacts = contact_info.get('contacts', [])
        if contacts:
            # Extract primary contacts
            for contact in contacts:
                if contact.get('primary'):
                    contact_type = contact.get('type', '')
                    if contact_type == 'email':
                        flattened['primary_email'] = contact.get('value', '')
                    elif contact_type == 'phone':
                        flattened['primary_phone'] = contact.get('value', '')

            # Extract all emails and phones
            emails = [c['value'] for c in contacts if c.get('type') == 'email']
            phones = [c['value'] for c in contacts if c.get('type') == 'phone']
            flattened['all_emails'] = '; '.join(emails) if emails else ''
            flattened['all_phones'] = '; '.join(phones) if phones else ''

        # Add metadata
        if 'credits_used' in contact_info:
            flattened['credits_used'] = contact_info['credits_used']
        if 'reveal_timestamp' in contact_info:
            flattened['reveal_timestamp'] = contact_info['reveal_timestamp']

        return flattened

    def _flatten_experience_info(
        self, experience_list: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Flatten experience information for CSV export."""
        if not experience_list:
            return {}

        # Get current experience (if any)
        current_exp = next((exp for exp in experience_list if exp.get('current')), None)
        if not current_exp and experience_list:
            current_exp = experience_list[0]  # Fallback to first experience

        flattened = {}
        if current_exp:
            flattened['current_company'] = current_exp.get('company', '')
            flattened['current_title'] = current_exp.get('title', '')

        # Calculate total experience years
        total_years = 0
        for exp in experience_list:
            duration = exp.get('duration', '')
            if 'year' in duration.lower():
                # Extract number from duration string like "3+ years" or "2 years"
                import re

                years_match = re.search(r'(\d+)', duration)
                if years_match:
                    total_years += int(years_match.group(1))

        if total_years > 0:
            flattened['total_experience_years'] = total_years

        return flattened

    def _flatten_education_info(
        self, education_list: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Flatten education information for CSV export."""
        if not education_list:
            return {}

        # Get highest education (assume first is highest)
        highest_edu = education_list[0]

        flattened = {}
        flattened['university'] = highest_edu.get('university', '')
        flattened['degree'] = highest_edu.get('degree', '')
        flattened['field_of_study'] = highest_edu.get('field_of_study', '')

        # Determine education level
        degree = highest_edu.get('degree', '').lower()
        if 'phd' in degree or 'doctorate' in degree:
            flattened['education_level'] = 'Doctorate'
        elif 'master' in degree or 'mba' in degree:
            flattened['education_level'] = 'Master'
        elif 'bachelor' in degree:
            flattened['education_level'] = 'Bachelor'
        else:
            flattened['education_level'] = 'Other'

        return flattened

    def _apply_column_mappings(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply column name mappings for consistent output."""
        # Only rename columns that exist in the DataFrame
        mappings = {k: v for k, v in self._column_mappings.items() if k in df.columns}
        return df.rename(columns=mappings)

    def _merge_enhanced_data(
        self, df: pd.DataFrame, enhanced_data: dict[str, dict[str, Any]]
    ) -> pd.DataFrame:
        """Merge additional enhanced data into the DataFrame."""
        # This is a simplified implementation
        # In a full implementation, you'd match on various keys and merge carefully
        return df

    def _write_dataframe_to_csv(
        self, df: pd.DataFrame, start_time: datetime
    ) -> ExportResult:
        """Write DataFrame to CSV and return export result."""
        # Generate timestamped filename if configured
        output_path = Path(
            self._generate_timestamped_filename(self.config.output_path, start_time)
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write to CSV
        df.to_csv(
            output_path,
            index=False,
            encoding=self.config.encoding,
            sep=self.config.delimiter,
        )

        # Get file statistics
        file_size = output_path.stat().st_size
        duration = (datetime.now() - start_time).total_seconds()

        return ExportResult(
            file_path=str(output_path),
            total_rows=len(df),
            total_columns=len(df.columns),
            file_size_bytes=file_size,
            export_duration_seconds=duration,
            success=True,
        )

    # Native CSV implementations (fallback when pandas not available)
    def _export_prospects_native(
        self,
        prospects: list[dict[str, Any]],
        contacts: dict[str, dict[str, Any]] | None,
        experiences: dict[str, list[dict[str, Any]]] | None,
        education: dict[str, list[dict[str, Any]]] | None,
        start_time: datetime,
    ) -> ExportResult:
        """Export prospects using native Python CSV module."""
        # Simplified native implementation
        rows = []
        all_columns = set()

        for prospect in prospects:
            row = prospect.copy()
            prospect_id = prospect.get('uid', prospect.get('id', ''))

            # Add contact information (simplified)
            if contacts and prospect_id in contacts:
                contact_info = contacts[prospect_id]
                row.update(self._flatten_contact_info(contact_info))

            # Apply column mappings
            row = self._apply_row_column_mappings(row)

            rows.append(row)
            all_columns.update(row.keys())

        return self._write_rows_to_csv(rows, list(all_columns), start_time)

    def _export_operations_native(
        self, operations: list[dict[str, Any]], start_time: datetime
    ) -> ExportResult:
        """Export operations using native CSV approach."""
        return self._write_rows_to_csv(
            operations, list(operations[0].keys()) if operations else [], start_time
        )

    def _export_signalhire_csv_native(
        self,
        signalhire_csv_path: str,
        enhanced_data: dict[str, dict[str, Any]] | None,
        start_time: datetime,
    ) -> ExportResult:
        """Process SignalHire CSV using native Python CSV module."""
        rows = []

        # Read the original CSV
        with open(signalhire_csv_path, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)

        # Get all columns
        all_columns = list(rows[0].keys()) if rows else []
        return self._write_rows_to_csv(rows, all_columns, start_time)

    def _apply_row_column_mappings(self, row: dict[str, Any]) -> dict[str, Any]:
        """Apply column mappings to a single row."""
        mapped_row = {}
        for key, value in row.items():
            mapped_key = self._column_mappings.get(key, key)
            mapped_row[mapped_key] = value
        return mapped_row

    def _write_rows_to_csv(
        self, rows: list[dict[str, Any]], columns: list[str], start_time: datetime
    ) -> ExportResult:
        """Write rows to CSV using native CSV module."""
        # Generate timestamped filename if configured
        output_path = Path(
            self._generate_timestamped_filename(self.config.output_path, start_time)
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', newline='', encoding=self.config.encoding) as f:
            if columns:
                writer = csv.DictWriter(
                    f, fieldnames=columns, delimiter=self.config.delimiter
                )
                if self.config.include_headers:
                    writer.writeheader()
                writer.writerows(rows)

        # Get file statistics
        file_size = output_path.stat().st_size if output_path.exists() else 0
        duration = (datetime.now() - start_time).total_seconds()

        return ExportResult(
            file_path=str(output_path),
            total_rows=len(rows),
            total_columns=len(columns),
            file_size_bytes=file_size,
            export_duration_seconds=duration,
            success=True,
        )

    def _prospect_to_dict(self, prospect: Prospect) -> dict:
        """
        Converts a Prospect object to a flat dictionary suitable for a DataFrame.
        """
        contact_info = prospect.contact or {}
        return {
            "name": prospect.name,
            "title": prospect.title,
            "company": prospect.company,
            "location": prospect.location,
            "email": getattr(contact_info, 'email', None),
            "phone": getattr(contact_info, 'phone', None),
            "linkedin": getattr(contact_info, 'linkedin', None),
        }

    # Validation methods
    def _validate_email(self, email: str) -> bool:
        """Validate email format."""
        if not email:
            return False
        return '@' in email and '.' in email.split('@')[-1]

    def _validate_phone(self, phone: str) -> bool:
        """Validate phone format."""
        if not phone:
            return False
        # Simple validation - contains digits
        return any(char.isdigit() for char in phone)

    def _validate_url(self, url: str) -> bool:
        """Validate URL format."""
        if not url:
            return False
        return url.startswith(('http://', 'https://'))

    def _validate_date(self, date_str: str) -> bool:
        """Validate date format."""
        if not date_str:
            return False
        try:
            datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return True
        except (ValueError, TypeError):
            return False


# Utility functions
def create_csv_exporter(output_path: str, **kwargs) -> CSVExporter:
    """Create a CSV exporter with the specified configuration."""
    config = ExportConfig(output_path=output_path, **kwargs)
    return CSVExporter(config)


def create_timestamped_csv_exporter(
    base_filename: str = "export.csv", timestamp_format: str = "%Y%m%d_%H%M%S", **kwargs
) -> CSVExporter:
    """
    Create a CSV exporter with automatic timestamp naming.
    Args:
        base_filename: Base filename (e.g., 'prospects.csv')
        timestamp_format: Timestamp format string (default: YYYYMMDD_HHMMSS)
        **kwargs: Additional ExportConfig parameters
    Returns:
        CSVExporter configured for timestamped filenames
    Examples:
        >>> exporter = create_timestamped_csv_exporter("prospects.csv")
        >>> # Will create files like: prospects_20250911_153045.csv
        >>> exporter = create_timestamped_csv_exporter("search_results.csv", "%Y-%m-%d_%H-%M-%S")
        >>> # Will create files like: search_results_2025-09-11_15-30-45.csv
    """
    config = ExportConfig(
        output_path=base_filename,
        add_timestamp_to_filename=True,
        timestamp_format=timestamp_format,
        **kwargs,
    )
    return CSVExporter(config)


def quick_export_prospects(
    prospects: list[dict[str, Any]],
    output_path: str = "prospects_export.csv",
    include_timestamp: bool = True,
) -> ExportResult:
    """
    Quick export of prospect data to CSV with optional timestamping.
    Args:
        prospects: List of prospect dictionaries to export
        output_path: Output file path (default: prospects_export.csv)
        include_timestamp: Add timestamp to filename (default: True)
    Returns:
        ExportResult with export statistics
    Examples:
        >>> result = quick_export_prospects(prospect_data)
        >>> # Creates: prospects_export_20250911_153045.csv
        >>> result = quick_export_prospects(prospect_data, "my_leads.csv", include_timestamp=False)
        >>> # Creates: my_leads.csv
    """
    if include_timestamp:
        exporter = create_timestamped_csv_exporter(output_path)
    else:
        config = ExportConfig(output_path=output_path, add_timestamp_to_filename=False)
        exporter = CSVExporter(config)

    return exporter.export_prospects(prospects)


def quick_export_contacts(
    contacts_data: dict[str, dict[str, Any]], output_path: str = "contacts_export.csv"
) -> ExportResult:
    """
    Quick export of contact reveal data to timestamped CSV.
    Args:
        contacts_data: Dictionary of contact information keyed by prospect ID
        output_path: Base output file path
    Returns:
        ExportResult with export statistics
    Examples:
        >>> contacts = {"uid1": {"email": "test@example.com", "phone": "+1-555-0123"}}
        >>> result = quick_export_contacts(contacts)
        >>> # Creates: contacts_export_20250911_153045.csv
    """
    # Convert contacts dict to prospects format for export
    prospects = []
    for prospect_id, contact_info in contacts_data.items():
        prospect = {"uid": prospect_id, **contact_info}
        prospects.append(prospect)

    exporter = create_timestamped_csv_exporter(output_path)
    return exporter.export_prospects(prospects, contacts=contacts_data)


def generate_export_filename(
    base_name: str,
    operation_type: str | None = None,
    timestamp: datetime | None = None,
    format_str: str = "%Y%m%d_%H%M%S",
) -> str:
    """
    Generate a timestamped export filename following SignalHire agent conventions.
    Args:
        base_name: Base filename without extension (e.g., 'prospects', 'contacts')
        operation_type: Optional operation type (e.g., 'search', 'reveal', 'export')
        timestamp: Optional specific timestamp (defaults to current time)
        format_str: Timestamp format string
    Returns:
        Formatted filename with timestamp
    Examples:
        >>> generate_export_filename("prospects")
        'prospects_20250911_153045.csv'
        >>> generate_export_filename("leads", "search")
        'leads_search_20250911_153045.csv'
        >>> generate_export_filename("contacts", "reveal", datetime(2025, 9, 11, 15, 30, 45))
        'contacts_reveal_20250911_153045.csv'
    """
    timestamp = timestamp or datetime.now()
    timestamp_str = timestamp.strftime(format_str)

    if operation_type:
        filename = f"{base_name}_{operation_type}_{timestamp_str}.csv"
    else:
        filename = f"{base_name}_{timestamp_str}.csv"

    return filename
