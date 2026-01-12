# CAMEL-AI Usage and Testing Guide

## What is CAMEL-AI in This Project?

CAMEL-AI is a **multi-agent framework** that powers the intelligent claim processing system in ClaimSphere AI. It enables multiple specialized AI agents to work together using ERNIE 5.0 Thinking models for complex reasoning tasks.

### Key Benefits

1. **Multi-Agent Architecture**: Different agents handle specialized tasks (extraction, validation, fraud detection, etc.)
2. **Reasoning Traces**: ERNIE 5.0 Thinking provides transparent reasoning for AI decisions
3. **Orchestrated Workflows**: Agents coordinate through an orchestrator for complex workflows
4. **Fallback Support**: System gracefully falls back to direct ERNIE API if CAMEL-AI is unavailable

## How CAMEL-AI is Used

### 1. **Extraction Agent** (`backend/agents/extraction_agent.py`)
- **Purpose**: Extracts structured data from OCR text
- **Model**: ERNIE 5.0 Thinking via CAMEL-AI
- **Input**: OCR text from documents
- **Output**: Structured JSON with claim fields (claimant_name, provider_name, date, amount, etc.)
- **Reasoning**: Provides reasoning traces for extraction decisions

### 2. **Validation Agent** (`backend/agents/validation_agent.py`)
- **Purpose**: Validates claim data against rules and policies
- **Model**: ERNIE 5.0 Thinking via CAMEL-AI
- **Input**: Extracted claim data
- **Output**: Validation results with errors, recommendations, risk level
- **Reasoning**: Explains why a claim is valid/invalid

### 3. **Fraud Detection Agent** (`backend/agents/fraud_detection_agent.py`)
- **Purpose**: Assesses fraud risk in claims
- **Model**: ERNIE 5.0 Thinking via CAMEL-AI
- **Input**: Claim data + historical claims
- **Output**: Fraud risk score (0-1.0) with reasons
- **Reasoning**: Explains fraud risk assessment

### 4. **Query Agent** (`backend/agents/query_agent.py`)
- **Purpose**: Answers natural language questions about claims
- **Model**: ERNIE 5.0 Thinking via CAMEL-AI
- **Input**: User query + claims context
- **Output**: Natural language answer with citations
- **Reasoning**: Shows how the answer was derived

### 5. **Analytics Agent** (`backend/agents/analytics_agent.py`)
- **Purpose**: Generates insights and summaries
- **Model**: ERNIE 5.0 Thinking via CAMEL-AI
- **Input**: List of claims
- **Output**: Analytics summary with trends and recommendations
- **Reasoning**: Explains insights

### 6. **Orchestrator Agent** (`backend/agents/orchestrator.py`)
- **Purpose**: Coordinates workflows between agents
- **Function**: Manages the sequence of agent calls for complex tasks
- **Workflows**: 
  - `process_new_claim`: Full pipeline (OCR → Extract → Validate → Fraud Check)
  - `validate_and_approve`: Validation and approval workflow
  - `analyze_patterns`: Pattern analysis workflow

## Architecture Flow

```
User Uploads Document
    ↓
OCR Agent (PaddleOCR) → Extracts text
    ↓
Extraction Agent (CAMEL-AI + ERNIE 5.0) → Extracts structured data
    ↓
Validation Agent (CAMEL-AI + ERNIE 5.0) → Validates claim
    ↓
Fraud Detection Agent (CAMEL-AI + ERNIE 5.0) → Assesses risk
    ↓
Duplicate Agent → Checks for duplicates
    ↓
Final Result with Reasoning Traces
```

## Testing CAMEL-AI

### Prerequisites

1. **Install CAMEL-AI**:
   ```bash
   pip install 'camel-ai[all]'
   ```

2. **Set API Key**:
   ```bash
   # In .env file
   QIANFAN_API_KEY=ak-your-api-key-here
   ```

3. **Verify Installation**:
   ```bash
   python -c "import camel; print(camel.__version__)"
   ```

### Test 1: Verify Agent Initialization

**Script**: `test_agent_init.py`

```python
#!/usr/bin/env python3
"""Test agent initialization"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.agent_coordinator import get_agent_coordinator
from backend.ocr_processor import OCRProcessor

def test_agent_initialization():
    """Test that all agents initialize correctly"""
    print("=" * 60)
    print("Testing Agent Initialization")
    print("=" * 60)
    
    coordinator = get_agent_coordinator()
    ocr_processor = OCRProcessor(lang='en')
    
    try:
        coordinator.initialize(ocr_processor=ocr_processor)
        print("✅ All agents initialized successfully!")
        
        # List all agents
        print("\nAvailable agents:")
        for agent_name in coordinator.agents.keys():
            print(f"  - {agent_name}")
        
        return True
    except Exception as e:
        print(f"❌ Agent initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_agent_initialization()
    sys.exit(0 if success else 1)
```

**Run**:
```bash
cd backend
python test_agent_init.py
```

**Expected Output**:
```
============================================================
Testing Agent Initialization
============================================================
[INFO] Agent Coordinator initialized
[INFO] Extraction Agent initialized with ERNIE 5.0 Thinking
[INFO] Validation Agent initialized with ERNIE 5.0 Thinking
...
✅ All agents initialized successfully!

Available agents:
  - ocr
  - extraction
  - validation
  - fraud
  - duplicate
  - query
  - analytics
```

### Test 2: Test Extraction Agent

**Script**: `test_extraction.py`

```python
#!/usr/bin/env python3
"""Test extraction agent"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.agent_coordinator import get_agent_coordinator

def test_extraction():
    """Test extraction agent with sample OCR text"""
    print("=" * 60)
    print("Testing Extraction Agent")
    print("=" * 60)
    
    coordinator = get_agent_coordinator()
    coordinator.initialize()
    
    # Sample OCR text (simulating extracted text from a medical bill)
    sample_ocr_text = """
    MEDICAL BILL
    
    Patient: John Doe
    Date of Service: 2024-01-15
    Provider: City Hospital
    
    Services:
    - Consultation: $150.00
    - Lab Test: $75.00
    - Medication: $45.00
    
    Total Amount: $270.00
    Insurance Policy: POL-123456
    Diagnosis: Annual checkup
    """
    
    print("\nInput OCR Text:")
    print(sample_ocr_text)
    
    try:
        result = coordinator.extract_claim_info(sample_ocr_text)
        
        print("\n✅ Extraction Result:")
        print(f"Success: {result.get('success', False)}")
        print(f"Method: {result.get('method', 'Unknown')}")
        
        if result.get('success'):
            data = result.get('data', {})
            print("\nExtracted Data:")
            for key, value in data.items():
                print(f"  {key}: {value}")
            
            if result.get('reasoning'):
                print("\nReasoning Trace:")
                print(result['reasoning'])
        
        return result.get('success', False)
    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_extraction()
    sys.exit(0 if success else 1)
```

**Run**:
```bash
cd backend
python test_extraction.py
```

### Test 3: Test Validation Agent

**Script**: `test_validation.py`

```python
#!/usr/bin/env python3
"""Test validation agent"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.agent_coordinator import get_agent_coordinator

def test_validation():
    """Test validation agent"""
    print("=" * 60)
    print("Testing Validation Agent")
    print("=" * 60)
    
    coordinator = get_agent_coordinator()
    coordinator.initialize()
    
    # Sample claim data
    claim_data = {
        "claimant_name": "John Doe",
        "provider_name": "City Hospital",
        "date_of_incident": "2024-01-15",
        "total_amount": 270.00,
        "currency": "USD",
        "claim_type": "medical",
        "policy_number": "POL-123456"
    }
    
    print("\nInput Claim Data:")
    for key, value in claim_data.items():
        print(f"  {key}: {value}")
    
    try:
        result = coordinator.validate_claim(claim_data)
        
        print("\n✅ Validation Result:")
        print(f"Success: {result.get('success', False)}")
        
        if result.get('success'):
            validation = result.get('validation', {})
            print(f"Valid: {validation.get('is_valid', False)}")
            print(f"Risk Level: {validation.get('risk_level', 'unknown')}")
            
            errors = validation.get('validation_errors', [])
            if errors:
                print("\nValidation Errors:")
                for error in errors:
                    print(f"  - {error}")
            
            recommendations = validation.get('recommendations', [])
            if recommendations:
                print("\nRecommendations:")
                for rec in recommendations:
                    print(f"  - {rec}")
            
            if result.get('reasoning'):
                print("\nReasoning Trace:")
                print(result['reasoning'])
        
        return result.get('success', False)
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_validation()
    sys.exit(0 if success else 1)
```

### Test 4: Test Query Agent

**Script**: `test_query.py`

```python
#!/usr/bin/env python3
"""Test query agent"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.agent_coordinator import get_agent_coordinator

def test_query():
    """Test query agent with natural language questions"""
    print("=" * 60)
    print("Testing Query Agent")
    print("=" * 60)
    
    coordinator = get_agent_coordinator()
    coordinator.initialize()
    
    # Sample claims context
    claims_context = [
        {
            "claim_number": "CLM-001",
            "claimant_name": "John Doe",
            "total_amount": 270.00,
            "status": "approved",
            "date_of_incident": "2024-01-15"
        },
        {
            "claim_number": "CLM-002",
            "claimant_name": "Jane Smith",
            "total_amount": 150.00,
            "status": "pending",
            "date_of_incident": "2024-01-20"
        }
    ]
    
    queries = [
        "What is the total amount of all claims?",
        "How many claims are approved?",
        "Who submitted the highest claim?",
    ]
    
    for query in queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print('='*60)
        
        try:
            result = coordinator.answer_query(
                query=query,
                claims_context=claims_context,
                scope_description="all claims"
            )
            
            if result.get('success'):
                print(f"\n✅ Answer: {result.get('answer', 'No answer')}")
                
                if result.get('cited_claims'):
                    print(f"Cited Claims: {', '.join(result['cited_claims'])}")
                
                if result.get('reasoning'):
                    print(f"\nReasoning Trace:\n{result['reasoning']}")
            else:
                print(f"❌ Query failed: {result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"❌ Query failed: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_query()
```

### Test 5: Test Full Workflow

**Script**: `test_workflow.py`

```python
#!/usr/bin/env python3
"""Test full claim processing workflow"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.agent_coordinator import get_agent_coordinator

def test_full_workflow():
    """Test complete claim processing workflow"""
    print("=" * 60)
    print("Testing Full Claim Processing Workflow")
    print("=" * 60)
    
    coordinator = get_agent_coordinator()
    coordinator.initialize()
    
    # Simulate claim document processing
    claim_data = {
        "document": {
            "text": """
            MEDICAL BILL
            
            Patient: John Doe
            Date of Service: 2024-01-15
            Provider: City Hospital
            
            Total Amount: $270.00
            Policy: POL-123456
            """
        },
        "existing_claims": []
    }
    
    try:
        result = coordinator.process_claim(
            claim_data=claim_data,
            workflow="process_new_claim"
        )
        
        print("\n✅ Workflow Result:")
        print(f"Workflow: {result.get('workflow', 'unknown')}")
        
        steps = result.get('steps', [])
        print(f"\nSteps Completed: {len(steps)}")
        
        for step in steps:
            step_name = step.get('step', 'unknown')
            step_result = step.get('result', {})
            success = step_result.get('success', False)
            status = "✅" if success else "❌"
            print(f"  {status} {step_name}")
        
        final_result = result.get('final_result', {})
        if final_result.get('extracted_data'):
            print("\nFinal Extracted Data:")
            for key, value in final_result['extracted_data'].items():
                print(f"  {key}: {value}")
        
        return True
    except Exception as e:
        print(f"❌ Workflow failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_full_workflow()
    sys.exit(0 if success else 1)
```

### Test 6: Test via API Endpoints

**Start the server**:
```bash
cd backend
python -m uvicorn app:app --reload
```

**Test Extraction via API**:
```bash
# Upload a document
curl -X POST "http://localhost:8000/api/claims/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@sample_claim.pdf" \
  -F "process_with_ai=true"
```

**Test Query via API**:
```bash
curl -X POST "http://localhost:8000/api/query" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the total amount of all approved claims?",
    "scope": "all"
  }'
```

## Checking Logs

When agents are working, you'll see logs like:

```
[INFO] Extraction Agent: extraction_started
[INFO] Extraction Agent: Using ERNIE 5.0 Thinking via CAMEL-AI
[INFO] Extraction Agent: extraction_completed
[INFO] Validation Agent: validation_started
[INFO] Validation Agent: Using ERNIE 5.0 Thinking via CAMEL-AI
[INFO] Validation Agent: validation_completed
```

## Troubleshooting

### Issue: "CAMEL-AI not available"
- **Check**: `pip show camel-ai`
- **Fix**: `pip install 'camel-ai[all]'`

### Issue: "QIANFAN_API_KEY not set"
- **Check**: `.env` file has `QIANFAN_API_KEY=ak-...`
- **Fix**: Set the API key in `.env` file

### Issue: Agents using fallback mode
- **Check**: Logs show "Using fallback ERNIE API"
- **Fix**: Verify `QIANFAN_API_KEY` is correct and CAMEL-AI is installed

### Issue: "Failed to initialize agent"
- **Check**: API key validity and network connectivity
- **Fix**: Verify API key at Qianfan console

## Summary

CAMEL-AI enables:
- ✅ Multi-agent collaboration
- ✅ Reasoning traces for transparency
- ✅ ERNIE 5.0 Thinking for complex reasoning
- ✅ Orchestrated workflows
- ✅ Graceful fallback to direct API

Test each component individually, then test the full workflow to ensure everything works together!
