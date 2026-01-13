#!/usr/bin/env python3
"""
Test script for role-playing claim review and approval
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.agents.role_playing_coordinator import RolePlayingCoordinator

def test_role_playing_review():
    """Test role-playing review without discussion"""
    print("=" * 60)
    print("Test 1: Role-Playing Review (No Discussion)")
    print("=" * 60)
    
    coordinator = RolePlayingCoordinator()
    
    # Sample claim data
    claim_data = {
        "claimant_name": "John Doe",
        "provider_name": "City Hospital",
        "date_of_incident": "2024-01-15",
        "total_amount": 270.00,
        "currency": "USD",
        "claim_type": "medical",
        "policy_number": "POL-123456",
        "description": "Annual checkup and lab tests"
    }
    
    print("\nClaim Data:")
    for key, value in claim_data.items():
        print(f"  {key}: {value}")
    
    print("\nProcessing through role-playing agents...")
    result = coordinator.process(claim_data, enable_discussion=False)
    
    print("\n✅ Results:")
    print(f"Workflow: {result.get('workflow')}")
    
    # Show review
    review = result.get("review", {})
    if review:
        print(f"\n📋 Review Assessment: {review.get('overall_assessment', 'N/A')}")
        print(f"   Confidence: {review.get('confidence_level', 0)}")
        print(f"   Key Findings: {len(review.get('key_findings', []))} items")
        print(f"   Concerns: {len(review.get('concerns', []))} items")
    
    # Show decision
    decision = result.get("final_decision", {})
    if decision:
        print(f"\n✅ Final Decision: {decision.get('decision', 'N/A')}")
        print(f"   Approved Amount: {decision.get('approved_amount', 'N/A')}")
        print(f"   Confidence: {decision.get('confidence', 0)}")
        if decision.get('reasoning'):
            print(f"   Reasoning: {decision['reasoning'][:200]}...")
    
    return result.get("final_decision") is not None

def test_role_playing_with_discussion():
    """Test role-playing review with discussion"""
    print("\n" + "=" * 60)
    print("Test 2: Role-Playing Review (With Discussion)")
    print("=" * 60)
    
    coordinator = RolePlayingCoordinator()
    
    # Sample claim with some concerns
    claim_data = {
        "claimant_name": "Jane Smith",
        "provider_name": "Unknown Clinic",
        "date_of_incident": "2024-12-25",  # Future date - suspicious
        "total_amount": 5000.00,  # High amount
        "currency": "USD",
        "claim_type": "medical",
        "description": "Emergency treatment"
    }
    
    print("\nClaim Data (with potential concerns):")
    for key, value in claim_data.items():
        print(f"  {key}: {value}")
    
    print("\nProcessing with discussion enabled...")
    result = coordinator.process(
        claim_data,
        enable_discussion=True,
        max_turns=2
    )
    
    print("\n✅ Results:")
    
    # Show discussion if available
    for step in result.get("steps", []):
        if step.get("step") == "discussion":
            discussion = step.get("log", [])
            print(f"\n💬 Discussion ({len(discussion)} turns):")
            for turn in discussion:
                print(f"   {turn.get('speaker', 'Unknown')}: {turn.get('message', '')[:150]}...")
            break
    
    # Show final decision
    decision = result.get("final_decision", {})
    if decision:
        print(f"\n✅ Final Decision: {decision.get('decision', 'N/A')}")
        print(f"   Reasoning: {decision.get('reasoning', 'N/A')[:200]}...")
    
    return result.get("final_decision") is not None

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("Role-Playing Agents Testing")
    print("=" * 60)
    
    results = []
    
    # Test 1: Basic review
    try:
        results.append(("Basic Review", test_role_playing_review()))
    except Exception as e:
        print(f"❌ Basic review test failed: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Basic Review", False))
    
    # Test 2: Review with discussion
    try:
        results.append(("Review with Discussion", test_role_playing_with_discussion()))
    except Exception as e:
        print(f"❌ Discussion test failed: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Review with Discussion", False))
    
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
        print("✅ All tests passed! Role-playing agents are working.")
    else:
        print("❌ Some tests failed. Check the errors above.")
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
