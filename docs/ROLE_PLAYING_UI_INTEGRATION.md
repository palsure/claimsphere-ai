# Role-Playing Agent Review UI Integration

## Overview

The role-playing agent review is now **automatically integrated** into the claim submission flow. When a user submits a claim, CAMEL-AI agents automatically review it and the results are displayed in the UI.

## How It Works

### 1. Automatic Review on Submission

When a user submits a claim via the ClaimWizard:

1. **User submits claim** → `POST /api/claims/{claim_id}/submit`
2. **Backend automatically triggers** role-playing review
3. **Review Agent** reviews the claim
4. **Approval Agent** makes a decision
5. **Results returned** in the submission response
6. **UI displays** the review results

### 2. UI Flow

```
User Submits Claim
    ↓
Backend Processes & Reviews (Automatic)
    ↓
Review Results Returned
    ↓
UI Shows Review Component
    ↓
User Reviews AI Assessment
    ↓
User Clicks "Continue"
    ↓
Navigate to Claim Details
```

## Components

### Backend Changes

**File**: `backend/api/claims.py`

- Modified `submit_claim` endpoint to automatically trigger role-playing review
- Review runs **without discussion** for faster processing
- Results included in response as `role_playing_review`

### Frontend Components

**1. RolePlayingReview Component** (`frontend/src/components/RolePlayingReview.tsx`)
- Displays review assessment
- Shows agent discussion (if enabled)
- Displays final decision
- Shows reasoning traces
- Collapsible sections for better UX

**2. ClaimWizard Integration** (`frontend/src/components/ClaimWizard.tsx`)
- Captures review results after submission
- Shows review component before navigating
- Allows user to review before continuing

### API Methods

**File**: `frontend/src/utils/api.ts`

```typescript
// Automatically called on submission
claimsAPI.submit(claimId) // Returns review in response

// Manual review (optional)
claimsAPI.rolePlayingReview(claimId, enableDiscussion, maxTurns)

// Auto-approve based on review
claimsAPI.rolePlayingApprove(claimId, enableDiscussion, maxTurns)
```

## UI Features

### Review Display

The review component shows:

1. **Review Assessment**
   - Overall assessment (approve/deny/pend)
   - Confidence level with visual bar
   - Key findings
   - Concerns (if any)
   - Recommendations
   - Reasoning

2. **Agent Discussion** (if enabled)
   - Multi-turn conversation log
   - Questions and answers between agents
   - Speaker identification

3. **Final Decision**
   - Decision type (APPROVE/DENY/PEND)
   - Approved amount (if applicable)
   - Decision confidence
   - Detailed reasoning
   - Policy references
   - Conditions (if any)

4. **Reasoning Traces**
   - Step-by-step reasoning from each agent
   - Transparent decision-making process

### Visual Indicators

- **Color-coded badges**: Green (approve), Red (deny), Yellow (pend)
- **Confidence bars**: Visual representation of confidence levels
- **Collapsible sections**: Expand/collapse for detailed view
- **Dark mode support**: Fully styled for dark/light themes

## Configuration

### Enable/Disable Auto-Review

In `backend/api/claims.py`, you can:

1. **Disable auto-review**: Comment out the role-playing review code
2. **Enable discussion**: Change `enable_discussion=False` to `True`
3. **Auto-approve high-confidence**: Uncomment the auto-approval code

### Auto-Approval (Optional)

To enable automatic approval based on agent decision:

```python
# In submit_claim endpoint
decision_data = review_result.get("final_decision", {}).get("decision", {})
if decision_data.get("decision") == "approve" and decision_data.get("confidence", 0) > 0.8:
    # Auto-approve high-confidence approvals
    # ... create decision record ...
```

## User Experience

### Submission Flow

1. User uploads document
2. AI extracts information
3. User reviews and corrects fields
4. User clicks "Submit for Review"
5. **NEW**: AI agents automatically review
6. **NEW**: Review results displayed
7. User reviews AI assessment
8. User clicks "Continue to Claim Details"
9. Navigate to claim details page

### Benefits

- ✅ **Immediate feedback**: Users see AI review instantly
- ✅ **Transparency**: Full reasoning traces visible
- ✅ **Trust**: Users understand how decisions are made
- ✅ **Efficiency**: No need to wait for manual review
- ✅ **Education**: Users learn what makes a good claim

## Testing

### Test the Integration

1. **Start the backend**:
   ```bash
   cd backend
   python -m uvicorn app:app --reload
   ```

2. **Start the frontend**:
   ```bash
   cd frontend
   npm run dev
   ```

3. **Submit a claim**:
   - Go to `/claims/new`
   - Upload a document
   - Review extracted fields
   - Click "Submit for Review"
   - **See the AI review results!**

### Expected Behavior

- After submission, review component appears
- Shows assessment, decision, and reasoning
- User can expand/collapse sections
- Click "Continue" to go to claim details

## Troubleshooting

### Issue: Review not showing

**Check**:
- Backend logs for role-playing review errors
- `QIANFAN_API_KEY` is set correctly
- CAMEL-AI is installed: `pip show camel-ai`
- Response includes `role_playing_review` field

**Solution**:
- Review runs in background, errors don't fail submission
- Check browser console for frontend errors
- Verify API response structure

### Issue: Review takes too long

**Solution**:
- Review runs without discussion by default (faster)
- Can be made async in future versions
- Consider showing loading state

### Issue: Auto-approval not working

**Check**:
- Auto-approval code is commented out by default
- Uncomment and configure threshold
- Check decision confidence levels

## Future Enhancements

1. **Async Review**: Run review in background, show notification when ready
2. **Review History**: Store and display past reviews
3. **Comparison**: Compare multiple reviews for same claim
4. **Customization**: Allow users to enable/disable auto-review
5. **Notifications**: Notify when review is complete
6. **Export**: Export review results as PDF

## Summary

The role-playing agent review is now seamlessly integrated into the claim submission flow. Users get immediate, transparent AI feedback on their claims, improving trust and understanding of the system.
