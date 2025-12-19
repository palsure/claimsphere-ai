# API Documentation

## Base URL
```
http://localhost:8000
```

## Endpoints

### Health Check
**GET** `/health`

Check if the API is running.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00"
}
```

### Upload Claim Document
**POST** `/api/claims/upload`

Upload a claim document for processing.

**Parameters:**
- `file` (multipart/form-data): PDF, JPG, or PNG file
- `process_with_ai` (query parameter, optional): Boolean, default `true`

**Response:**
```json
{
  "claim": {
    "id": "uuid",
    "claim_number": "CLM-20240101-ABC12345",
    "claimant_name": "John Doe",
    "claim_type": "medical",
    "date_of_incident": "2024-01-01T12:00:00",
    "date_submitted": "2024-01-02T10:00:00",
    "total_amount": 5000.00,
    "approved_amount": null,
    "currency": "USD",
    "status": "pending",
    "policy_number": "POL-123456",
    "items": [
      {
        "description": "Medical procedure",
        "quantity": 1,
        "unit_price": 5000.00,
        "amount": 5000.00
      }
    ],
    "description": "Medical claim for procedure",
    "validation_errors": [],
    "is_duplicate": false,
    "language": "en"
  },
  "ocr_text": "Extracted text from document...",
  "duplicates_found": 0,
  "anomalies": [],
  "validation_errors": [],
  "processing_info": {
    "language_detected": "en",
    "text_lines_extracted": 20
  }
}
```

### Get Claims
**GET** `/api/claims`

Retrieve list of claims with optional filters.

**Query Parameters:**
- `claim_type` (optional): Filter by claim type (medical, insurance, travel, property, business, other)
- `status` (optional): Filter by status (pending, under_review, approved, rejected, requires_info, processed)
- `date_from` (optional): Start date (YYYY-MM-DD)
- `date_to` (optional): End date (YYYY-MM-DD)
- `limit` (optional): Maximum results (default: 100)

**Response:**
```json
{
  "claims": [
    {
      "id": "uuid",
      "claim_number": "CLM-20240101-ABC12345",
      "claimant_name": "John Doe",
      "claim_type": "medical",
      "status": "pending",
      ...
    }
  ],
  "total": 1,
  "filters": {
    "claim_type": null,
    "status": null,
    "date_from": null,
    "date_to": null
  }
}
```

### Get Single Claim
**GET** `/api/claims/{claim_id}`

Get details of a specific claim.

**Response:**
```json
{
  "id": "uuid",
  "claim_number": "CLM-20240101-ABC12345",
  "claimant_name": "John Doe",
  ...
}
```

### Update Claim Status
**PUT** `/api/claims/{claim_id}/status`

Update claim status (approve, reject, etc.).

**Request Body:**
```json
{
  "status": "approved",
  "reviewer_notes": "Approved after review",
  "approved_amount": 4500.00
}
```

**Response:**
```json
{
  "message": "Claim status updated",
  "claim": {
    ...
  }
}
```

### Delete Claim
**DELETE** `/api/claims/{claim_id}`

Delete a claim.

**Response:**
```json
{
  "message": "Claim deleted",
  "id": "uuid"
}
```

### Get Analytics
**GET** `/api/claims/analytics`

Get claim analytics and insights.

**Query Parameters:**
- `date_from` (optional): Start date (YYYY-MM-DD)
- `date_to` (optional): End date (YYYY-MM-DD)

**Response:**
```json
{
  "total_claims": 100,
  "total_amount": 500000.00,
  "approved_amount": 450000.00,
  "pending_amount": 50000.00,
  "status_breakdown": {
    "pending": 10,
    "approved": 70,
    "rejected": 15,
    "under_review": 5
  },
  "type_breakdown": {
    "medical": 300000.00,
    "insurance": 150000.00,
    "travel": 50000.00
  },
  "monthly_trends": [
    {
      "month": "2024-01",
      "count": 50,
      "total": 250000.00
    }
  ],
  "average_processing_time": 2.5,
  "approval_rate": 70.0,
  "top_claimants": [
    {
      "claimant": "John Doe",
      "count": 5,
      "total": 25000.00
    }
  ]
}
```

### Natural Language Query
**POST** `/api/claims/query`

Ask natural language questions about claims.

**Request Body:**
```json
{
  "query": "What's the total amount of pending claims?",
  "date_from": "2024-01-01T00:00:00",
  "date_to": "2024-01-31T23:59:59",
  "claim_type": null,
  "status": null
}
```

**Response:**
```json
{
  "query": "What's the total amount of pending claims?",
  "answer": "The total amount of pending claims is $50,000.00...",
  "claims_analyzed": 25
}
```

### Re-categorize Claim
**POST** `/api/claims/{claim_id}/categorize`

Re-categorize a claim using ERNIE.

**Response:**
```json
{
  "claim_id": "uuid",
  "new_type": "medical",
  "claim": {
    ...
  }
}
```

### Validate Claim
**POST** `/api/claims/{claim_id}/validate`

Validate a claim and return validation results.

**Response:**
```json
{
  "claim_id": "uuid",
  "validation_errors": [],
  "anomalies": [],
  "ai_validation": {
    "is_valid": true,
    "validation_errors": [],
    "recommendations": [],
    "risk_level": "low",
    "requires_manual_review": false
  },
  "is_valid": true
}
```

## Claim Types

- `medical`
- `insurance`
- `travel`
- `property`
- `business`
- `other`

## Claim Statuses

- `pending`
- `under_review`
- `approved`
- `rejected`
- `requires_info`
- `processed`

## Error Responses

All endpoints may return errors in the following format:

```json
{
  "detail": "Error message"
}
```

**Status Codes:**
- `400`: Bad Request
- `404`: Not Found
- `500`: Internal Server Error
