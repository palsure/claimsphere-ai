# ClaimSphere AI

AI-powered claim processing system with role-based access control, automated workflows, and natural language queries.

## 🌟 Features

### Role-Based Access Control (RBAC)
- **USER (Claimant)**: Submit claims, view own claims, correct extracted fields
- **AGENT (Adjuster)**: Review assigned claims, approve/deny/pend decisions, view duplicates
- **ADMIN**: Manage users, plans, validation rules, thresholds, view analytics

### Claim Processing
- **OCR Processing**: PaddleOCR for document text extraction
- **AI Extraction**: ERNIE 4.5 for intelligent field extraction
- **Validation Engine**: Configurable rules per plan
- **Auto-Approval**: Safe automated approval with configurable thresholds
- **Duplicate Detection**: Identify potential duplicate claims

### Natural Language Queries
- Ask questions about claims in natural language
- RBAC-enforced: Users only see their own claims
- Responses cite claim IDs and fields used

## 🏗️ Architecture

```
claimsphere-ai/
├── backend/                    # FastAPI Python backend
│   ├── api/                    # API routes
│   │   ├── auth.py            # Authentication endpoints
│   │   ├── claims.py          # Claim CRUD & workflow
│   │   ├── users.py           # User management
│   │   ├── plans.py           # Plan & policy management
│   │   ├── validation.py      # Validation rules
│   │   ├── query.py           # NL query endpoint
│   │   └── admin.py           # Admin analytics
│   ├── auth/                   # JWT authentication
│   ├── database/               # SQLAlchemy models
│   ├── services/               # Business logic
│   │   ├── claim_service.py
│   │   ├── validation_service.py
│   │   ├── auto_approval_service.py
│   │   └── audit_service.py
│   ├── ocr_processor.py        # PaddleOCR integration
│   ├── ernie_service.py        # ERNIE API integration
│   └── app.py                  # FastAPI application
│
├── frontend/                   # Next.js React frontend
│   └── src/
│       ├── pages/
│       │   ├── dashboard/      # Role-based dashboards
│       │   ├── login.tsx
│       │   └── signup.tsx
│       ├── components/
│       └── contexts/
│           └── AuthContext.tsx # Auth state management
│
└── alembic/                    # Database migrations
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL (production) or SQLite (development)

### Backend Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp env.template .env
# Edit .env with your API keys

# Initialize database and seed data
python -m backend.scripts.seed_data

# Run the backend
python -m backend.app
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

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Test Credentials

| Role  | Email               | Password    |
|-------|---------------------|-------------|
| Admin | admin@example.com   | password123 |
| Agent | agent@example.com   | password123 |
| User  | user@example.com    | password123 |

## 📋 Data Models

### Core Entities

- **User**: System users with roles
- **Role**: USER, AGENT, ADMIN with permissions
- **InsuranceCompany**: Insurance providers
- **Plan**: Insurance plans with auto-approval settings
- **MemberPolicy**: User-plan associations
- **Claim**: Insurance claims with workflow states

### Claim Workflow

```
DRAFT → SUBMITTED → EXTRACTED → VALIDATED → AUTO_APPROVED/PENDING_REVIEW → APPROVED/DENIED/PENDED → CLOSED
```

### Supporting Entities

- **ClaimDocument**: Uploaded documents with OCR results
- **ExtractedField**: AI-extracted fields with confidence scores
- **ValidationResult**: Rule validation outcomes
- **Decision**: Approval/denial decisions with reasons
- **AuditLog**: Complete audit trail
- **DuplicateMatch**: Potential duplicate claims

## ⚙️ Configuration

### Environment Variables

```bash
# Baidu AI Studio API
BAIDU_API_KEY=your-api-key
BAIDU_SECRET_KEY=your-secret-key

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
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login
- `POST /api/auth/refresh` - Refresh token
- `GET /api/auth/me` - Get current user

### Claims
- `POST /api/claims` - Create claim
- `GET /api/claims` - List claims (role-filtered)
- `GET /api/claims/{id}` - Get claim details
- `PUT /api/claims/{id}` - Update claim
- `POST /api/claims/{id}/submit` - Submit claim
- `POST /api/claims/{id}/upload` - Upload document
- `POST /api/claims/{id}/correct-field` - Correct extracted field
- `POST /api/claims/{id}/decide` - Make decision (Agent/Admin)
- `GET /api/claims/queue/pending` - Get review queue (Agent/Admin)

### Admin
- `GET /api/admin/analytics` - Claim analytics
- `GET /api/admin/audit-logs` - Audit logs
- `GET /api/admin/dashboard-stats` - Dashboard statistics

### Natural Language Query
- `POST /api/query` - Ask questions about claims

## 🧪 Development

### Run Tests
```bash
pytest tests/
```

### Database Migrations
```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Run migrations
alembic upgrade head
```

## 📝 License

MIT License - See LICENSE file for details.

## 🙏 Acknowledgments

- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) for document OCR
- [ERNIE](https://aistudio.baidu.com) for AI-powered extraction
- [FastAPI](https://fastapi.tiangolo.com/) for the backend framework
- [Next.js](https://nextjs.org/) for the frontend framework
