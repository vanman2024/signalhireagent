from collections import Counter, defaultdict
from typing import Any


def analyze_search_parameters(
    contacts: list[dict[str, Any]], search_metadata: dict[str, Any] = None
) -> dict[str, Any]:
    """Track which search parameters yield the most unique contacts (FR-015)."""
    analysis = {
        "total_contacts": len(contacts),
        "unique_companies": len(
            set(c.get('company', '') for c in contacts if c.get('company'))
        ),
        "unique_locations": len(
            set(c.get('location', '') for c in contacts if c.get('location'))
        ),
        "job_title_diversity": len(
            set(c.get('job_title', '') for c in contacts if c.get('job_title'))
        ),
    }

    # Add search metadata if provided
    if search_metadata:
        analysis["search_metadata"] = search_metadata

    return analysis


def analyze_geographic_coverage(contacts: list[dict[str, Any]]) -> dict[str, Any]:
    """Report geographic coverage and suggest areas for additional searches (FR-016)."""
    locations = [c.get('location', '').strip() for c in contacts if c.get('location')]

    # Parse location data
    location_counts = Counter(locations)
    city_counts = defaultdict(int)
    state_counts = defaultdict(int)
    country_counts = defaultdict(int)

    for location in locations:
        if not location:
            continue

        # Simple parsing - assumes format like "City, State, Country" or variations
        parts = [part.strip() for part in location.split(',')]

        if len(parts) >= 3:
            city, state, country = parts[0], parts[1], parts[2]
            city_counts[f"{city}, {state}"] += 1
            state_counts[state] += 1
            country_counts[country] += 1
        elif len(parts) == 2:
            city, state = parts[0], parts[1]
            city_counts[f"{city}, {state}"] += 1
            state_counts[state] += 1
        elif len(parts) == 1:
            state_counts[parts[0]] += 1

    return {
        "total_locations": len(location_counts),
        "top_cities": dict(Counter(city_counts).most_common(10)),
        "top_states": dict(Counter(state_counts).most_common(10)),
        "top_countries": dict(Counter(country_counts).most_common(5)),
        "geographic_diversity_score": len(state_counts) / max(len(contacts), 1) * 100,
        "suggestions": generate_geographic_suggestions(
            dict(state_counts), dict(city_counts)
        ),
    }


def generate_geographic_suggestions(state_counts: dict, city_counts: dict) -> list[str]:
    """Generate suggestions for additional geographic searches."""
    suggestions = []

    # Suggest underrepresented major markets
    major_markets = [
        "California",
        "Texas",
        "Florida",
        "New York",
        "Illinois",
        "Pennsylvania",
    ]
    for market in major_markets:
        if state_counts.get(market, 0) < 10:
            suggestions.append(f"Consider additional searches in {market}")

    # Suggest expanding successful cities
    top_cities = list(city_counts.keys())[:3]
    for city in top_cities:
        suggestions.append(f"Expand search radius around {city}")

    return suggestions


def identify_search_overlap(
    contact_sets: list[list[dict[str, Any]]], set_names: list[str] = None
) -> dict[str, Any]:
    """Identify search overlap and recommend optimization strategies (FR-017)."""
    if not contact_sets or len(contact_sets) < 2:
        return {"error": "Need at least 2 contact sets to analyze overlap"}

    if not set_names:
        set_names = [f"Set {i+1}" for i in range(len(contact_sets))]

    # Create sets of UIDs for overlap analysis
    uid_sets = []
    linkedin_sets = []

    for contacts in contact_sets:
        uids = set(c.get('uid') for c in contacts if c.get('uid'))
        linkedin_urls = set(
            c.get('linkedin_url') for c in contacts if c.get('linkedin_url')
        )
        uid_sets.append(uids)
        linkedin_sets.append(linkedin_urls)

    # Calculate overlaps
    overlap_analysis = {
        "set_sizes": [len(s) for s in contact_sets],
        "set_names": set_names,
        "uid_overlaps": {},
        "linkedin_overlaps": {},
        "recommendations": [],
    }

    # Pairwise overlaps
    for i in range(len(uid_sets)):
        for j in range(i + 1, len(uid_sets)):
            uid_overlap = len(uid_sets[i] & uid_sets[j])
            linkedin_overlap = len(linkedin_sets[i] & linkedin_sets[j])

            pair_name = f"{set_names[i]} ∩ {set_names[j]}"
            overlap_analysis["uid_overlaps"][pair_name] = uid_overlap
            overlap_analysis["linkedin_overlaps"][pair_name] = linkedin_overlap

            # Generate recommendations
            overlap_percentage = (
                uid_overlap / min(len(uid_sets[i]), len(uid_sets[j]))
            ) * 100
            if overlap_percentage > 50:
                overlap_analysis["recommendations"].append(
                    f"High overlap ({overlap_percentage:.1f}%) between {set_names[i]} and {set_names[j]} - consider refining search terms"
                )
            elif overlap_percentage < 10:
                overlap_analysis["recommendations"].append(
                    f"Low overlap ({overlap_percentage:.1f}%) between {set_names[i]} and {set_names[j]} - good search diversity"
                )

    return overlap_analysis


def create_heavy_equipment_search_templates() -> dict[str, dict[str, str]]:
    """Create Boolean search templates for Heavy Equipment Mechanics (FR-014)."""
    return {
        "heavy_equipment_mechanic_basic": {
            "title": "Heavy Equipment Mechanic",
            "keywords": "diesel OR hydraulic OR CAT OR Caterpillar OR Komatsu OR excavator",
            "description": "Basic heavy equipment mechanic search",
        },
        "heavy_equipment_mechanic_exclude_operators": {
            "title": "(Heavy Equipment Mechanic) NOT (Operator OR Driver)",
            "keywords": "(mechanic OR technician OR repair OR maintenance) NOT (operator OR driver)",
            "description": "Heavy equipment mechanics excluding operators and drivers",
        },
        "diesel_technician_focused": {
            "title": "(Heavy Equipment Technician) OR (Heavy Equipment Mechanic) OR (Heavy Duty Mechanic) OR (Diesel Technician) OR (Equipment Mechanic)",
            "keywords": "(technician OR mechanic OR maintenance OR repair) NOT (operator OR driver OR supervisor)",
            "description": "Complete heavy equipment technicians and mechanics (excludes operators)",
        },
        "construction_equipment_specialist": {
            "title": "(Construction Equipment) AND (Mechanic OR Technician OR Specialist)",
            "keywords": "bulldozer OR excavator OR loader OR grader OR crane",
            "description": "Construction equipment specialists",
        },
        # Red Seal Trade Templates - Scalable System
        "automotive_service_technician": {
            "title": "(Automotive Service Technician) OR (Auto Mechanic) OR (Vehicle Technician) OR (Car Mechanic)",
            "keywords": "(automotive OR vehicle OR car OR truck OR brake OR engine) NOT (driver OR operator)",
            "description": "Automotive service technicians and mechanics (Red Seal)",
        },
        "electrician": {
            "title": "(Electrician) OR (Electrical Technician) OR (Electrical Worker)",
            "keywords": "(electrical OR wiring OR circuit OR voltage OR installation) NOT (operator OR helper)",
            "description": "Electricians and electrical technicians (Red Seal)",
        },
        "plumber": {
            "title": "(Plumber) OR (Plumbing Technician) OR (Pipefitter)",
            "keywords": "(plumbing OR pipe OR water OR sewer OR gas) NOT (helper OR laborer)",
            "description": "Plumbers and plumbing technicians (Red Seal)",
        },
        "welder": {
            "title": "(Welder) OR (Welding Technician) OR (Fabricator)",
            "keywords": "(welding OR fabrication OR TIG OR MIG OR arc) NOT (helper OR laborer)",
            "description": "Welders and welding technicians (Red Seal)",
        },
        "millwright": {
            "title": "(Millwright) OR (Industrial Mechanic) OR (Maintenance Mechanic)",
            "keywords": "(millwright OR industrial OR maintenance OR machinery) NOT (operator OR laborer)",
            "description": "Millwrights and industrial mechanics (Red Seal)",
        },
        "hvac_technician": {
            "title": "(HVAC Technician) OR (Refrigeration Mechanic) OR (Climate Control Technician)",
            "keywords": "(HVAC OR refrigeration OR heating OR cooling OR ventilation) NOT (helper OR installer)",
            "description": "HVAC and refrigeration technicians (Red Seal)",
        },
        "carpenter": {
            "title": "(Carpenter) OR (Construction Carpenter) OR (Framer)",
            "keywords": "(carpenter OR framing OR construction OR wood) NOT (helper OR laborer)",
            "description": "Carpenters and construction specialists (Red Seal)"
        },
        "crane_operator": {
            "title": "(Crane Operator) OR (Mobile Crane Operator) OR (Tower Crane Operator)",
            "keywords": "crane OR operator OR rigging OR lifting",
            "description": "Crane operators (Red Seal)",
        },
        "instrumentation_technician": {
            "title": "(Instrumentation Technician) OR (Instrument Mechanic) OR (Control Systems Technician)",
            "keywords": "(instrumentation OR control OR calibration OR measurement) NOT (operator OR helper)",
            "description": "Instrumentation and control technicians (Red Seal)"
        },
        "machinist": {
            "title": "(Machinist) OR (CNC Machinist) OR (Tool and Die Maker)",
            "keywords": "(machinist OR CNC OR lathe OR mill OR precision) NOT (operator OR helper)",
            "description": "Machinists and precision workers (Red Seal)"
        },
    }
