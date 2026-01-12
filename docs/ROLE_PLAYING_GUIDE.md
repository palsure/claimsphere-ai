# Role-Playing Agents for Claim Review and Approval

## Overview

This project uses **CAMEL-AI's role-playing framework** to simulate realistic claim review and approval processes. Instead of a single agent making decisions, we have multiple agents with distinct roles that can discuss and debate claims before making decisions.

## Architecture

### Agents

1. **Review Agent** (`ReviewAgent`)
   - **Role**: Senior Claims Reviewer (15 years experience)
   - **Responsibilities**:
     - Thoroughly review claim documents and extracted data
     - Identify inconsistencies, missing information, or red flags
     - Check compliance with policies and regulations
     - Provide detailed assessments and recommendations
   - **Output**: Review assessment with findings, concerns, and recommendations

2. **Approval Agent** (`ApprovalAgent`)
   - **Role**: Claims Approver (decision authority)
   - **Responsibilities**:
     - Review the reviewer's assessment
     - Consider company policies and risk tolerance
     - Make final decisions: APPROVE, DENY, or PEND
     - Set approved amounts
   - **Output**: Final decision with reasoning and policy references

3. **Role-Playing Coordinator** (`RolePlayingCoordinator`)
   - **Role**: Facilitates conversations between agents
   - **Responsibilities**:
     - Orchestrates the review and approval workflow
     - Enables multi-turn discussions between agents
     - Manages the conversation flow
   - **Output**: Complete workflow result with review, discussion, and decision

## How It Works

### Basic Workflow (No Discussion)

```
1. Review Agent reviews the claim
   ↓
2. Approval Agent reviews the assessment and makes decision
   ↓
3. Final decision returned
```

### Advanced Workflow (With Discussion)

```
1. Review Agent reviews the claim
   ↓
2. Approval Agent asks questions about the review
   ↓
3. Review Agent responds with clarifications
   ↓
4. Approval Agent makes final decision based on discussion
   ↓
5. Complete result with discussion log
```

## API Usage

### Endpoint: Role-Playing Review

**POST** `/api/claims/{claim_id}/role-playing-review`

Review a claim using role-playing agents without making a decision.

**Request Body:**
```json
{
  "enable_discussion": false,  // Optional: Enable multi-turn discussion
  "max_turns": 2              // Optional: Maximum discussion turns
}
```

**Response:**
```json
{
  "claim_id": "claim-123",
  "review": {
    "overall_assessment": "approve",
    "confidence_level": 0.85,
    "key_findings": ["Claim is complete and valid"],
    "concerns": [],
    "recommendations": ["Approve for full amount"],
    "reasoning": "Detailed reasoning..."
  },
  "discussion": {
    "turns": 2,
    "log": [
      {
        "turn": 1,
        "speaker": "Approver",
        "message": "Question about the claim..."
      },
      {
        "turn": 2,
        "speaker": "Reviewer",
        "message": "Response to the question..."
      }
    ]
  },
  "decision": {
    "decision": "approve",
    "approved_amount": 270.00,
    "confidence": 0.9,
    "reasoning": "Decision reasoning...",
    "policy_references": ["Policy XYZ"],
    "conditions": []
  },
  "reasoning_traces": {
    "review": "Review agent's reasoning...",
    "approval": "Approval agent's reasoning..."
  }
}
```

### Endpoint: Role-Playing Approve

**POST** `/api/claims/{claim_id}/role-playing-approve`

Review and automatically approve/deny a claim using role-playing agents.

**Request Body:**
```json
{
  "enable_discussion": true,
  "max_turns": 3
}
```

**Response:**
```json
{
  "message": "Claim reviewed and decision made using role-playing agents",
  "decision_id": "decision-456",
  "decision": "approved",
  "review": { ... },
  "reasoning": "Decision reasoning..."
}
```

## Example Usage

### Python Example

```python
import requests

# Review a claim with discussion enabled
response = requests.post(
    "http://localhost:8000/api/claims/claim-123/role-playing-review",
    headers={"Authorization": "Bearer YOUR_TOKEN"},
    json={
        "enable_discussion": True,
        "max_turns": 2
    }
)

result = response.json()
print(f"Review Assessment: {result['review']['overall_assessment']}")
print(f"Final Decision: {result['decision']['decision']}")
print(f"Reasoning: {result['decision']['reasoning']}")

# If discussion was enabled
if result.get('discussion'):
    print(f"\nDiscussion ({result['discussion']['turns']} turns):")
    for turn in result['discussion']['log']:
        print(f"  {turn['speaker']}: {turn['message']}")
```

### cURL Example

```bash
# Review without discussion
curl -X POST "http://localhost:8000/api/claims/claim-123/role-playing-review" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "enable_discussion": false
  }'

# Review with discussion and auto-approve
curl -X POST "http://localhost:8000/api/claims/claim-123/role-playing-approve" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "enable_discussion": true,
    "max_turns": 3
  }'
```

## Benefits of Role-Playing

1. **More Realistic**: Simulates how real human reviewers and approvers interact
2. **Better Decisions**: Discussion allows agents to clarify concerns before deciding
3. **Transparency**: Full reasoning traces show how decisions were made
4. **Debate**: Agents can challenge each other's assessments
5. **Learning**: Can identify patterns in how agents reason about claims

## Configuration

### Enable Discussion

Set `enable_discussion: true` to allow agents to discuss claims:

```python
coordinator = RolePlayingCoordinator()
result = coordinator.process(
    claim_data,
    enable_discussion=True,  # Enable discussion
    max_turns=3              # Allow up to 3 turns of discussion
)
```

### Adjust Agent Personalities

Modify the system messages in:
- `backend/agents/review_agent.py` - Review Agent persona
- `backend/agents/approval_agent.py` - Approval Agent persona

### Temperature Settings

- **Review Agent**: `temperature=0.3` (balanced, thorough)
- **Approval Agent**: `temperature=0.2` (more consistent decisions)
- **Discussion**: `temperature=0.4` (more creative questions)

## Testing

### Test Role-Playing Review

```python
from backend.agents.role_playing_coordinator import RolePlayingCoordinator

# Sample claim data
claim_data = {
    "claimant_name": "John Doe",
    "provider_name": "City Hospital",
    "date_of_incident": "2024-01-15",
    "total_amount": 270.00,
    "currency": "USD",
    "claim_type": "medical"
}

# Initialize coordinator
coordinator = RolePlayingCoordinator()

# Review with discussion
result = coordinator.process(
    claim_data,
    enable_discussion=True,
    max_turns=2
)

print(f"Review: {result['review']}")
print(f"Decision: {result['final_decision']}")
if result.get('steps'):
    for step in result['steps']:
        if step.get('step') == 'discussion':
            print(f"Discussion: {step.get('log', [])}")
```

## Integration with Existing Workflow

The role-playing system can be integrated into the existing claim processing workflow:

1. **After Extraction**: Use role-playing for complex claims
2. **Before Manual Review**: Use role-playing to pre-screen claims
3. **For High-Value Claims**: Always use role-playing for claims above a threshold
4. **For Disputed Claims**: Use role-playing when claims are disputed

## Future Enhancements

1. **Multi-Agent Panels**: Add more agents (Auditor, Policy Expert, etc.)
2. **Voting System**: Multiple approvers vote on decisions
3. **Learning from Decisions**: Agents learn from past decisions
4. **Custom Personas**: Allow configuration of agent personalities
5. **Real-time Discussion**: Stream discussion as it happens

## Troubleshooting

### Issue: Discussion not working

- **Check**: `QIANFAN_API_KEY` is set
- **Check**: CAMEL-AI is installed: `pip show camel-ai`
- **Check**: `enable_discussion=True` in request

### Issue: Agents not reasoning

- **Check**: Using ERNIE 5.0 Thinking model (supports reasoning)
- **Check**: API key has access to ERNIE 5.0 Thinking
- **Check**: Logs for model initialization errors

### Issue: Decisions inconsistent

- **Adjust**: Temperature settings in agent initialization
- **Adjust**: System messages to be more specific
- **Add**: More context in claim data

## Summary

Role-playing agents provide a more sophisticated and transparent way to review and approve claims. By simulating realistic interactions between reviewers and approvers, we get better decisions with full reasoning traces.
