"""
Configuration Management Commands

Provides CLI commands for managing SignalHire agent configuration:
- Setting and getting configuration values
- Listing all configuration
- Resetting to defaults
- Secure credential storage
"""

import json
import os
from pathlib import Path
from typing import Any, ClassVar

import click

try:
    from pydantic import BaseModel, Field, validator
except ImportError:
    from pydantic import BaseModel, Field, validator

from ..models.exceptions import ConfigurationError


class ConfigValue(BaseModel):
    """Single configuration value with metadata."""

    value: str | int | float | bool
    description: str = ""
    secret: bool = False  # Whether to mask in output
    default: str | int | float | bool | None = None

    class Config:
        """Pydantic config."""

        json_encoders: ClassVar[dict] = {
            # Custom encoders if needed
        }


class AgentConfig(BaseModel):
    """SignalHire agent configuration model."""

    # Authentication
    signalhire_email: str | None = Field(None, description="SignalHire account email")
    signalhire_password: str | None = Field(
        None, description="SignalHire account password"
    )
    api_key: str | None = Field(None, description="SignalHire API key (if available)")

    # Callback Server
    callback_url: str = Field(
        "http://localhost:8000/callback",
        description="Callback URL for async operations",
    )
    callback_port: int = Field(8000, description="Port for callback server")

    # API Settings
    daily_reveal_limit: int = Field(
        5000, description="Daily API reveal limit for tracking"
    )
    api_timeout: float = Field(30.0, description="API request timeout in seconds")
    api_retry_attempts: int = Field(3, description="Number of API retry attempts")
    batch_size: int = Field(10, description="Default batch size for API operations")

    # Rate Limiting
    rate_limit_requests_per_minute: int = Field(
        60, description="API requests per minute limit"
    )
    rate_limit_reveal_per_hour: int = Field(
        100, description="Contact reveals per hour limit"
    )
    rate_limit_warnings: bool = Field(
        True, description="Show warnings at usage thresholds"
    )

    # Export Settings
    default_export_format: str = Field("csv", description="Default export format")
    default_output_dir: str = Field("./exports", description="Default output directory")
    export_timestamps: bool = Field(
        True, description="Add timestamps to export filenames"
    )
    timestamp_format: str = Field(
        "%Y%m%d_%H%M%S", description="Timestamp format for filenames"
    )

    # Logging
    log_level: str = Field("INFO", description="Logging level")
    log_format: str = Field("json", description="Log format (json or text)")

    @validator('log_level')
    def validate_log_level(cls, v: str) -> str:  # noqa: N805
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Invalid log level. Must be one of: {valid_levels}")
        return v.upper()

    @validator('default_export_format')
    def validate_export_format(cls, v: str) -> str:  # noqa: N805
        """Validate export format."""
        valid_formats = ["csv", "json", "xlsx"]
        if v.lower() not in valid_formats:
            raise ValueError(f"Invalid export format. Must be one of: {valid_formats}")
        return v.lower()

    def get_secret_fields(self) -> set[str]:
        """Get list of fields that should be masked in output."""
        return {"signalhire_password", "api_key"}

    def to_display_dict(self) -> dict[str, Any]:
        """Convert to dictionary with secrets masked."""
        data = self.dict()
        secret_fields = self.get_secret_fields()

        for field in secret_fields:
            if field in data and data[field] is not None:
                data[field] = "***masked***"

        return data


class ConfigManager:
    """Manages configuration storage and retrieval."""

    def __init__(self, config_dir: Path | None = None):
        """Initialize config manager.
        Args:
            config_dir: Custom config directory. Defaults to ~/.signalhire-agent/
        """
        if config_dir is None:
            config_dir = Path.home() / ".signalhire-agent"

        self.config_dir = config_dir
        self.config_file = config_dir / "config.json"
        self.ensure_config_dir()

    def ensure_config_dir(self) -> None:
        """Ensure configuration directory exists."""
        self.config_dir.mkdir(exist_ok=True, mode=0o700)  # Secure directory

    def load_config(self) -> AgentConfig:
        """Load configuration from file."""
        if not self.config_file.exists():
            return AgentConfig()  # Return defaults

        try:
            with open(self.config_file) as f:
                data = json.load(f)
            return AgentConfig(**data)
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Failed to load config: {e}") from e
        except Exception as e:
            raise ConfigurationError(f"Failed to load config: {e}") from e

    def save_config(self, config: AgentConfig) -> None:
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config.dict(), f, indent=2)

            # Secure file permissions
            os.chmod(self.config_file, 0o600)
        except OSError as e:
            raise ConfigurationError(f"Failed to save config: {e}") from e

    def get_value(self, key: str) -> Any:
        """Get a configuration value."""
        config = self.load_config()

        if not hasattr(config, key):
            raise ConfigurationError(f"Unknown configuration key: {key}")

        return getattr(config, key)

    def set_value(self, key: str, value: Any) -> None:
        """Set a configuration value."""
        config = self.load_config()

        if not hasattr(config, key):
            raise ConfigurationError(f"Unknown configuration key: {key}")

        # Convert string values to appropriate types
        field_info = config.__fields__.get(key)
        if field_info:
            field_type = field_info.type_

            # Handle boolean conversion
            if field_type is bool:
                if isinstance(value, str):
                    value = value.lower() in ('true', '1', 'yes', 'on')

            # Handle int conversion
            elif field_type is int:
                value = int(value)

            # Handle float conversion
            elif field_type is float:
                value = float(value)

        setattr(config, key, value)

        # Validate the updated config
        try:
            config = AgentConfig(**config.dict())
        except Exception as e:
            raise ConfigurationError(f"Invalid configuration value: {e}") from e

        self.save_config(config)

    def reset_to_defaults(self) -> None:
        """Reset configuration to defaults."""
        default_config = AgentConfig()
        self.save_config(default_config)

    def get_available_keys(self) -> dict[str, str]:
        """Get all available configuration keys with descriptions."""
        config = AgentConfig()
        return {
            field_name: field_info.field_info.description or "No description"
            for field_name, field_info in config.__fields__.items()
        }


# Initialize global config manager
config_manager = ConfigManager()


@click.group()
def config():
    """Manage configuration settings."""


@config.command(name='set')
@click.argument('key')
@click.argument('value')
@click.option('--force', is_flag=True, help="Force set even if validation fails")
def set_value_command(key: str, value: str, force: bool):
    """Set a configuration value.
    KEY: Configuration key to set
    VALUE: Value to set
    """
    try:
        config_manager.set_value(key, value)

        # Show the set value (masked if secret)
        current_config = config_manager.load_config()
        display_value = value

        if key in current_config.get_secret_fields():
            display_value = "***masked***"

        click.echo(f"✅ Set {key} = {display_value}")

    except ConfigurationError as e:
        if force:
            click.echo(f"⚠️  Warning: {e}")
            click.echo("❌ Force mode not implemented for configuration validation")
        else:
            click.echo(f"❌ {e}")
            click.echo("💡 Use --force to override validation (not recommended)")
        raise click.Abort() from e
    except Exception as e:
        click.echo(f"❌ Unexpected error: {e}")
        raise click.Abort() from e


@config.command(name='get')
@click.argument('key')
def get_value_command(key: str):
    """Get a configuration value.
    KEY: Configuration key to get
    """
    try:
        value = config_manager.get_value(key)

        # Mask secrets
        current_config = config_manager.load_config()
        if key in current_config.get_secret_fields() and value is not None:
            value = "***masked***"

        click.echo(f"{key} = {value}")

    except ConfigurationError as e:
        click.echo(f"❌ {e}")

        # Show available keys
        available_keys = config_manager.get_available_keys()
        click.echo("\n📋 Available configuration keys:")
        for k, desc in available_keys.items():
            click.echo(f"  {k}: {desc}")

        raise click.Abort() from e
    except Exception as e:
        click.echo(f"❌ Unexpected error: {e}")
        raise click.Abort() from e


@config.command(name='list')
@click.option(
    '--format',
    'output_format',
    default='table',
    type=click.Choice(['table', 'json', 'yaml']),
    help="Output format",
)
@click.option(
    '--show-secrets', is_flag=True, help="Show secret values (not recommended)"
)
def list_values_command(output_format: str, show_secrets: bool):
    """List all configuration values."""
    try:
        current_config = config_manager.load_config()

        if show_secrets:
            data = current_config.dict()
        else:
            data = current_config.to_display_dict()

        if output_format == 'json':
            click.echo(json.dumps(data, indent=2))
        elif output_format == 'yaml':
            try:
                import yaml

                click.echo(yaml.dump(data, default_flow_style=False))
            except ImportError as e:
                click.echo("❌ PyYAML not installed. Install with: pip install pyyaml")
                raise click.Abort() from e
        else:
            # Table format
            click.echo("📋 SignalHire Agent Configuration")
            click.echo("=" * 50)

            # Group by category
            categories = {
                "Authentication": [
                    "signalhire_email",
                    "signalhire_password",
                    "api_key",
                ],
                "Callback Server": ["callback_url", "callback_port"],
                "API Settings": [
                    "daily_reveal_limit",
                    "api_timeout",
                    "api_retry_attempts",
                    "batch_size",
                ],
                "Rate Limiting": [
                    "rate_limit_requests_per_minute",
                    "rate_limit_reveal_per_hour",
                    "rate_limit_warnings",
                ],
                "Export Settings": [
                    "default_export_format",
                    "default_output_dir",
                    "export_timestamps",
                    "timestamp_format",
                ],
                "Logging": ["log_level", "log_format"],
            }

            for category, keys in categories.items():
                click.echo(f"\n{category}:")
                for key in keys:
                    if key in data:
                        value = data[key]
                        if value is None:
                            value = "Not set"
                        click.echo(f"  {key}: {value}")

    except Exception as e:
        click.echo(f"❌ Failed to list configuration: {e}")
        raise click.Abort() from e


@config.command()
@click.option('--confirm', is_flag=True, help="Skip confirmation prompt")
def reset(confirm: bool):
    """Reset configuration to defaults."""
    if not confirm:
        click.echo("⚠️  This will reset ALL configuration to defaults.")
        click.echo("This action cannot be undone.")

        if not click.confirm("Are you sure you want to continue?"):
            click.echo("❌ Reset cancelled")
            return

    try:
        config_manager.reset_to_defaults()
        click.echo("✅ Configuration reset to defaults")

        # Show current defaults
        default_config = config_manager.load_config()
        display_data = default_config.to_display_dict()

        click.echo("\n📋 Current configuration (defaults):")
        for key, value in display_data.items():
            if value is not None:
                click.echo(f"  {key}: {value}")

    except Exception as e:
        click.echo(f"❌ Failed to reset configuration: {e}")
        raise click.Abort() from e


@config.command()
def validate():
    """Validate current configuration."""
    try:
        current_config = config_manager.load_config()

        # Check for required fields
        missing_required = []
        warnings = []

        # Check authentication
        if (
            not current_config.signalhire_email
            or not current_config.signalhire_password
        ) and not current_config.api_key:
            missing_required.append(
                "Authentication: Either (email + password) or api_key required"
            )

        # Check callback URL format
        if not current_config.callback_url.startswith(('http://', 'https://')):
            warnings.append("Callback URL should start with http:// or https://")

        # Check output directory
        output_dir = Path(current_config.default_output_dir)
        if not output_dir.exists():
            warnings.append(f"Output directory does not exist: {output_dir}")

        # Show results
        if missing_required:
            click.echo("❌ Configuration validation failed:")
            for error in missing_required:
                click.echo(f"  • {error}")
        else:
            click.echo("✅ Configuration validation passed")

        if warnings:
            click.echo("\n⚠️  Warnings:")
            for warning in warnings:
                click.echo(f"  • {warning}")

        if missing_required:
            raise click.Abort()

    except Exception as e:
        click.echo(f"❌ Validation failed: {e}")
        raise click.Abort() from e


@config.command()
def info():
    """Show configuration file location and help."""
    click.echo("📋 SignalHire Agent Configuration")
    click.echo("=" * 40)
    click.echo(f"Config file: {config_manager.config_file}")
    click.echo(f"Config directory: {config_manager.config_dir}")

    # Check if config exists
    if config_manager.config_file.exists():
        click.echo("✅ Configuration file exists")

        # Show file size and last modified
        stat = config_manager.config_file.stat()
        import datetime

        modified = datetime.datetime.fromtimestamp(stat.st_mtime)
        click.echo(f"📅 Last modified: {modified.strftime('%Y-%m-%d %H:%M:%S')}")
        click.echo(f"📊 File size: {stat.st_size} bytes")
    else:
        click.echo("⚠️  Configuration file does not exist (using defaults)")

    click.echo("\n📚 Available commands:")
    click.echo("  signalhire config set KEY VALUE    # Set configuration value")
    click.echo("  signalhire config get KEY          # Get configuration value")
    click.echo("  signalhire config list             # List all configuration")
    click.echo("  signalhire config reset            # Reset to defaults")
    click.echo("  signalhire config validate         # Validate configuration")

    click.echo("\n💡 Examples:")
    click.echo('  signalhire config set signalhire_email "your@email.com"')
    click.echo('  signalhire config set callback_url "https://yourdomain.com/callback"')
    click.echo("  signalhire config list --format json")
