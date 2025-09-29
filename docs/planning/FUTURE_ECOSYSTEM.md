# Future Ecosystem Integration: SignalHire → RedAI Data Pipeline

## Overview
Future project to create a complete data ecosystem connecting SignalHire Agent (candidate discovery) with RedAI Platform (Red Seal exam preparation), using ML/AI for intelligent categorization and market intelligence.

## The Vision
```
SignalHire Agent (Find Tradespeople)
    ↓ [Validate & Categorize]
Airtable Database (Store 1000s of contacts)
    ↓ [Export Training Data]
ML Models (Learn Trade Patterns)
    ↓ [Improve Classification]
RedAI Platform (Market Exam Prep)
    ↓ [Direct Marketing]
Same Candidates Found by SignalHire
```

## Phase 1: ML Training Data Export Service
**Timeline: Future Project (After Core CLI Stabilization)**

### 1.1 Training Data Exporter
```python
# src/services/ml_export_service.py
class RedAITrainingExporter:
    """Export Airtable contacts as ML training data"""

    def export_trade_classifications(self):
        # Job titles → Trade mappings
        # Company types → Trade patterns
        # Skills → Competency mappings

    def export_for_redai(self):
        # RedAI-specific format
        # Include Red Seal codes
        # Map to exam categories
```

### 1.2 CLI Commands
```bash
# Export training data
signalhire-agent ml export-training --format redai --output training_data.json

# Analyze trade patterns
signalhire-agent ml analyze-trades --min-confidence 0.8

# Generate datasets by trade
signalhire-agent ml prepare-dataset --trade "Heavy Equipment Technician"
```

## Phase 2: Intelligent Middleware Layer
**Timeline: After Phase 1**

### 2.1 Direct Anthropic API Integration
```python
# src/middleware/intelligent_agent.py
class IntelligentMiddleware:
    def __init__(self, anthropic_api_key):
        self.client = anthropic.Anthropic(api_key=anthropic_api_key)

    def categorize_contact(self, contact_data):
        # AI-powered trade classification
        # Confidence scoring
        # Red Seal eligibility assessment

    def enhance_search_query(self, user_intent):
        # Natural language → Boolean query
        # Optimize for trade-specific terms
        # Regional variation handling
```

### 2.2 Enhanced CLI Usage
```bash
# Natural language search
signalhire-agent search --use-ai "Find heavy equipment techs in Ontario"

# AI-powered categorization
signalhire-agent categorize --use-ai --confidence-threshold 0.85

# Intelligent workflow
signalhire-agent workflow find-red-seal-candidates --use-ai
```

## Phase 3: ML Model Training Pipeline
**Timeline: After 1000+ contacts collected**

### 3.1 Model Architecture
- **Classification Model**: Job Title → Trade (421A, 310T, etc.)
- **NER Model**: Extract certifications from descriptions
- **Clustering Model**: Discover new trade patterns
- **Ranking Model**: Red Seal eligibility scoring

### 3.2 Training Data Structure
```json
{
  "training_examples": [
    {
      "input": {
        "job_title": "Heavy Equipment Technician",
        "company": "Toromont CAT",
        "skills": ["hydraulics", "diesel", "diagnostics"],
        "location": "Ontario, Canada"
      },
      "output": {
        "trade": "Heavy Equipment Technician",
        "trade_code": "421A",
        "red_seal_eligible": true,
        "confidence": 0.95,
        "competencies": ["B1", "B2", "C1", "C2"]
      }
    }
  ]
}
```

## Phase 4: RedAI Platform Integration
**Timeline: When RedAI platform is ready**

### 4.1 Data Sync Architecture
```
Airtable → Export API → RedAI Database
         ↓
    Training Data
         ↓
    ML Models (Both Systems)
```

### 4.2 Shared Competency Mapping
- SignalHire skills → Red Seal competency codes
- Industry terms → Exam topics
- Regional variations → Standard terminology

### 4.3 Direct Marketing Pipeline
```python
# Automated campaign targeting
candidates = signalhire.get_contacts(trade="421A", status="Revealed")
redai.create_campaign(
    audience=candidates,
    message="Prepare for your Red Seal exam",
    trade_specific=True
)
```

## Phase 5: Feedback Loop & Active Learning
**Timeline: Ongoing after Phase 4**

### 5.1 Performance Metrics
- Classification accuracy by trade
- False positive/negative rates
- Regional accuracy variations
- Skill mapping precision

### 5.2 Active Learning Pipeline
1. Low-confidence classifications → Human review
2. User corrections → Model retraining
3. New patterns → Model updates
4. RedAI exam data → Improve categorization

## Technical Stack

### Current (Keep Separated)
- **SignalHire Agent**: Python CLI, Airtable REST API
- **RedAI Platform**: Next.js, Supabase, TypeScript

### Future Integration Layer
- **ML Pipeline**: Python, scikit-learn/TensorFlow
- **Middleware**: Anthropic API, Python
- **Data Export**: Pandas, JSON/CSV formats
- **Model Serving**: FastAPI, Docker

## Data Privacy & Separation

### Strict Boundaries
- SignalHire data stays in SignalHire Airtable
- RedAI data stays in RedAI Supabase
- Only anonymized training data crosses boundary
- No PII in training datasets

### Export Format (Anonymized)
```json
{
  "id": "hash_12345",  // Not SignalHire ID
  "features": {
    "title_tokens": ["heavy", "equipment", "technician"],
    "skill_categories": ["mechanical", "diagnostic"],
    "region": "ontario",
    "experience_range": "5-10"
  },
  "label": {
    "trade": "421A",
    "confidence": 0.92
  }
}
```

## Success Metrics

### Phase 1-2 (6 months)
- [ ] 1000+ categorized contacts in Airtable
- [ ] Export pipeline operational
- [ ] Basic ML model trained

### Phase 3-4 (12 months)
- [ ] 5000+ training examples
- [ ] 90%+ classification accuracy
- [ ] RedAI integration live

### Phase 5 (Ongoing)
- [ ] 95%+ accuracy on common trades
- [ ] Active learning improving monthly
- [ ] Full ecosystem operational

## Benefits

### For SignalHire Agent
- Better search queries from ML insights
- Improved categorization accuracy
- Validated trade mappings

### For RedAI Platform
- Real industry data for exam prep
- Targeted marketing lists
- Understanding of skill requirements

### For End Users
- Found by SignalHire → Trained by RedAI
- Complete career support ecosystem
- Better job matching

## Next Steps (Keep Separated For Now)

### Immediate (SignalHire)
1. Focus on CLI stability
2. Build validation system
3. Collect data in Airtable

### Immediate (RedAI)
1. Build exam prep platform
2. Create content for trades
3. Establish user base

### Future (Integration)
1. Design data export format
2. Build anonymization pipeline
3. Create ML training infrastructure
4. Implement feedback loops

## Important Notes

**SEPARATION OF CONCERNS**: These systems remain independent until both are stable:
- SignalHire = Candidate Discovery Tool
- RedAI = Exam Preparation Platform
- Future = Intelligent Integration Layer

**NO COUPLING**: Each system must work perfectly standalone before any integration.

**PRIVACY FIRST**: All integrations must respect data privacy and use anonymized training data only.

---

*This document outlines FUTURE work only. Current focus remains on stabilizing individual platforms.*