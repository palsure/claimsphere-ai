#!/usr/bin/env python3
"""
Quick test script to verify CAMEL-AI is working in ClaimSphere AI
"""
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_camel_import():
    """Test if CAMEL-AI can be imported"""
    print("=" * 60)
    print("Test 1: CAMEL-AI Import")
    print("=" * 60)
    try:
        from camel.agents import ChatAgent
        from camel.configs import QianfanConfig
        from camel.models import ModelFactory
        from camel.types import ModelPlatformType, ModelType
        print("✅ CAMEL-AI imported successfully")
        return True
    except ImportError as e:
        print(f"❌ CAMEL-AI import failed: {e}")
        print("   Install with: pip install 'camel-ai[all]'")
        return False

def test_api_key():
    """Test if API key is set"""
    print("\n" + "=" * 60)
    print("Test 2: API Key Configuration")
    print("=" * 60)
    api_key = os.getenv("QIANFAN_API_KEY")
    if api_key:
        # Mask the key for display
        masked = api_key[:10] + "..." + api_key[-5:] if len(api_key) > 15 else "***"
        print(f"✅ QIANFAN_API_KEY is set: {masked}")
        return True
    else:
        print("❌ QIANFAN_API_KEY is not set")
        print("   Set it in .env file: QIANFAN_API_KEY=ak-your-key")
        return False

def test_agent_initialization():
    """Test if agents can be initialized"""
    print("\n" + "=" * 60)
    print("Test 3: Agent Initialization")
    print("=" * 60)
    try:
        from backend.services.agent_coordinator import get_agent_coordinator
        
        coordinator = get_agent_coordinator()
        coordinator.initialize()
        
        print("✅ Agent Coordinator initialized")
        print(f"   Available agents: {', '.join(coordinator.agents.keys())}")
        return True
    except Exception as e:
        print(f"❌ Agent initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_extraction_agent():
    """Test extraction agent with sample text"""
    print("\n" + "=" * 60)
    print("Test 4: Extraction Agent")
    print("=" * 60)
    try:
        from backend.services.agent_coordinator import get_agent_coordinator
        
        coordinator = get_agent_coordinator()
        coordinator.initialize()
        
        sample_text = """
        MEDICAL BILL
        Patient: John Doe
        Date: 2024-01-15
        Provider: City Hospital
        Amount: $270.00
        Policy: POL-123456
        """
        
        print("Testing with sample OCR text...")
        result = coordinator.extract_claim_info(sample_text)
        
        if result.get('success'):
            print("✅ Extraction successful")
            print(f"   Method: {result.get('method', 'Unknown')}")
            data = result.get('data', {})
            if data:
                print("   Extracted fields:")
                for key, value in list(data.items())[:5]:  # Show first 5
                    print(f"     - {key}: {value}")
            return True
        else:
            print(f"❌ Extraction failed: {result.get('error', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"❌ Extraction test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("CAMEL-AI Testing for ClaimSphere AI")
    print("=" * 60)
    
    results = []
    
    # Test 1: Import
    results.append(("Import", test_camel_import()))
    
    # Test 2: API Key
    results.append(("API Key", test_api_key()))
    
    # Test 3: Agent Init (only if import and API key are OK)
    if results[0][1] and results[1][1]:
        results.append(("Agent Init", test_agent_initialization()))
        
        # Test 4: Extraction (only if agent init is OK)
        if results[2][1]:
            results.append(("Extraction", test_extraction_agent()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(r[1] for r in results)
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ All tests passed! CAMEL-AI is working correctly.")
    else:
        print("❌ Some tests failed. Check the errors above.")
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
