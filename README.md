# ClaimSphere AI

AI-powered insurance claim processing system with role-based access control, automated OCR extraction, intelligent validation, and natural language queries.

## 🌟 Features

### Role-Based Access Control (RBAC)
- **USER (Claimant)**: Submit claims, view own claims, correct extracted fields, respond to agent requests
- **AGENT (Full Access)**: Review all claims, approve/deny/pend decisions, request additional info, manage users/plans/rules, view analytics

### Intelligent Claim Processing
- **📤 3-Step Claim Wizard**: Upload → Processing → Review workflow
- **🔍 OCR Processing**: PaddleOCR 3.x for document text extraction (PDF + images)
- **🤖 AI Extraction**: ERNIE 4.5 for intelligent field extraction with regex fallback
- **✅ Validation Engine**: Configurable rules per plan
- **⚡ Auto-Approval**: Safe automated approval with configurable thresholds
- **🔄 Duplicate Detection**: File hash + content-based similarity detection (100% = exact file match)

### Claim Workflow Features
- **Agent Request Info**: Agents can request additional documents/information
- **User Response**: Users can upload documents and respond to agent requests
- **Status Tracking**: Real-time claim status with polling
- **Timeline View**: Complete audit trail of all claim activities
- **Decision Notes**: Agents can add notes and reason codes to decisions

### Natural Language Queries
- Ask questions about claims in natural language
- RBAC-enforced: Users only query their own claims, Agents query all
- Responses cite claim IDs and fields used

## 🏗️ Architecture

```
claimsphere-ai/
├── backend/                    # FastAPI Python backend
│   ├── api/                    # API routes
│   │   ├── auth.py            # Authentication endpoints
│   │   ├── claims.py          # Claim CRUD, workflow & decisions
│   │   ├── users.py           # User management (Agent only)
│   │   ├── plans.py           # Plan & policy management (Agent only)
│   │   ├── validation.py      # Validation rules (Agent only)
│   │   ├── query.py           # NL query endpoint
│   │   └── admin.py           # Analytics & dashboard (Agent only)
│   ├── auth/                   # JWT authentication & RBAC
│   ├── database/               # SQLAlchemy models & config
│   ├── services/               # Business logic
│   │   ├── claim_service.py   # Claim processing & OCR
│   │   ├── validation_service.py
│   │   ├── auto_approval_service.py
│   │   └── audit_service.py
│   ├── ocr_processor.py        # PaddleOCR 3.x integration
│   ├── ernie_service.py        # ERNIE API + regex fallback
│   └── app.py                  # FastAPI application
│
├── frontend/                   # Next.js React frontend
│   └── src/
│       ├── pages/
│       │   ├── index.tsx       # Dashboard with stats & quick actions
│       │   ├── claims.tsx      # Claims list with upload
│       │   ├── claims/new.tsx  # 3-step claim wizard
│       │   ├── claims/[id].tsx # Claim details & response
│       │   ├── dashboard/queue.tsx  # Agent review queue
│       │   ├── login.tsx
│       │   └── signup.tsx
│       ├── components/
│       │   ├── ClaimWizard.tsx # 3-step upload wizard
│       │   ├── ClaimList.tsx   # Claims list with actions
│       │   ├── ClaimUpload.tsx # Document upload
│       │   ├── Navigation.tsx  # Role-based navigation
│       │   └── Footer.tsx
│       ├── contexts/
│       │   └── AuthContext.tsx # Auth state & RBAC helpers
│       └── utils/
│           └── api.ts          # Axios API client with token refresh
│
└── docs/                       # Documentation
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- SQLite (development) or PostgreSQL (production)

### Backend Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp env.template .env
# Edit .env with your Baidu API key

# Run the backend (auto-initializes database & seeds demo users)
DISABLE_MODEL_SOURCE_CHECK=True python -m uvicorn backend.app:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Run the frontend
npm run dev
```

### Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Demo Credentials

| Role  | Email               | Password    | Access                                    |
|-------|---------------------|-------------|-------------------------------------------|
| User  | user@example.com    | password123 | Submit claims, view own claims, respond   |
| Agent | agent@example.com   | password123 | Full access: review, decide, manage all   |

## 📋 Data Models

### Core Entities

- **User**: System users with roles (USER, AGENT)
- **Role**: USER or AGENT with different permissions
- **InsuranceCompany**: Insurance providers
- **Plan**: Insurance plans with auto-approval settings
- **MemberPolicy**: User-plan associations
- **Claim**: Insurance claims with workflow states

### Claim Workflow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLAIM LIFECYCLE                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  DRAFT → SUBMITTED → EXTRACTED → VALIDATED                                 │
│                                      │                                      │
│                           ┌──────────┴──────────┐                          │
│                           ↓                     ↓                          │
│                     AUTO_APPROVED        PENDING_REVIEW                    │
│                           │                     │                          │
│                           ↓           ┌────────┼────────┐                  │
│                        CLOSED         ↓        ↓        ↓                  │
│                                   APPROVED  DENIED   PENDED                │
│                                       │        │        │                  │
│                                       ↓        ↓        ↓                  │
│                                    CLOSED   CLOSED   (User responds)       │
│                                                         │                  │
│                                                         ↓                  │
│                                                   PENDING_REVIEW           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Supporting Entities

- **ClaimDocument**: Uploaded documents (PDF, images) with OCR results
- **ExtractedField**: AI-extracted fields with confidence scores & corrections
- **ValidationResult**: Rule validation outcomes
- **Decision**: Approval/denial/pend decisions with reason codes & notes
- **AuditLog**: Complete audit trail of all actions
- **DuplicateMatch**: Potential duplicate claims with similarity scores

## ⚙️ Configuration

### Environment Variables

```bash
# Baidu AI Studio API (for ERNIE extraction)
BAIDU_API_KEY=your-api-key

# Database
DATABASE_URL=sqlite:///./claimsphere.db
# DATABASE_URL=postgresql://user:pass@localhost:5432/claimsphere

# JWT Authentication
JWT_SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# Application
DEBUG=True
PORT=8000
FRONTEND_URL=http://localhost:3000
```

### Auto-Approval Thresholds (per Plan)

- `auto_approve_amount_cap`: Maximum amount for auto-approval
- `min_ocr_quality_score`: Minimum OCR quality (0-1)
- `min_confidence_score`: Minimum extraction confidence (0-1)
- `max_duplicate_score`: Maximum allowed duplicate similarity
- `max_fraud_risk_score`: Maximum allowed fraud risk

## 🔒 API Authentication

All API endpoints (except `/api/auth/login` and `/api/auth/register`) require JWT authentication.

```bash
# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'

# Use the access_token in subsequent requests
curl http://localhost:8000/api/claims \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 📊 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login & get tokens |
| POST | `/api/auth/refresh` | Refresh access token |
| GET | `/api/auth/me` | Get current user |

### Claims (User)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/claims/upload` | Upload document & create claim |
| POST | `/api/claims/draft` | Create draft claim |
| GET | `/api/claims` | List own claims |
| GET | `/api/claims/{id}` | Get claim details |
| GET | `/api/claims/{id}/status` | Get claim status (for polling) |
| GET | `/api/claims/{id}/timeline` | Get claim activity timeline |
| POST | `/api/claims/{id}/submit` | Submit claim for review |
| POST | `/api/claims/{id}/upload` | Upload additional document |
| PUT | `/api/claims/{id}/fields` | Update extracted fields |
| POST | `/api/claims/{id}/respond` | Respond to agent info request |
| DELETE | `/api/claims/{id}` | Delete claim (soft delete) |

### Claims (Agent)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/claims/all` | List all claims |
| GET | `/api/claims/queue/pending` | Get review queue |
| POST | `/api/claims/{id}/decide` | Make decision (approve/deny/pend) |
| POST | `/api/claims/{id}/request-info` | Request additional info |
| GET | `/api/claims/{id}/duplicates` | Get duplicate matches |
| GET | `/api/claims/analytics` | Get claim analytics |

### Management (Agent)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/api/users` | User management |
| GET/POST | `/api/plans` | Plan management |
| GET/POST | `/api/validation/rules` | Validation rules |
| GET | `/api/admin/dashboard-stats` | Dashboard statistics |
| GET | `/api/admin/audit-logs` | Audit logs |

### Natural Language Query
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/query` | Ask questions about claims |

## 🔄 Duplicate Detection

The system detects potential duplicate claims using:

1. **File Hash Matching** (100% score): Exact same file uploaded
2. **Content Similarity**: Matching amount, date, provider, category, procedure codes

When duplicates are detected:
- User sees a warning with the duplicate score
- Agent can review duplicate matches in the claim details
- Claims are still processed but flagged for review

## 🧪 Development

### Run Tests
```bash
pytest tests/
```

### Database Management

```bash
# Clear all claims (for testing)
sqlite3 claimsphere.db "DELETE FROM duplicate_matches; DELETE FROM validation_results; DELETE FROM extracted_fields; DELETE FROM claim_documents; DELETE FROM decisions; DELETE FROM claims;"

# View claim data
sqlite3 claimsphere.db "SELECT claim_number, status, duplicate_score FROM claims;"
```

### Troubleshooting

**OCR not working?**
- Ensure PaddleOCR is installed: `pip install paddleocr`
- For PDF support, install PyMuPDF: `pip install pymupdf`
- Check logs for OCR initialization errors

**ERNIE API failing?**
- Verify your `BAIDU_API_KEY` in `.env`
- The system falls back to regex extraction if ERNIE fails

**Frontend not connecting?**
- Ensure `NEXT_PUBLIC_API_URL=http://localhost:8000` in `frontend/.env.local`
- Check backend CORS settings include your frontend port

## 📝 License

MIT License - See LICENSE file for details.

## 🙏 Acknowledgments

- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) for document OCR
- [ERNIE](https://aistudio.baidu.com) for AI-powered extraction
- [FastAPI](https://fastapi.tiangolo.com/) for the backend framework
- [Next.js](https://nextjs.org/) for the frontend framework
- [PyMuPDF](https://pymupdf.readthedocs.io/) for PDF processing
