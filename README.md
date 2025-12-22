# ClaimSphere AI - Automated Claim Processing Agent

AI-powered insurance claim processing system with role-based access control, automated OCR extraction, intelligent validation, and natural language queries.

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.10+)
- **Database**: PostgreSQL / SQLite with SQLAlchemy ORM
- **Authentication**: JWT (JSON Web Tokens) with python-jose
- **AI Processing**: Baidu ERNIE 4.5 API
- **OCR**: PaddleOCR (optional)
- **Validation**: Custom rule engine with configurable thresholds

### Frontend
- **Framework**: Next.js 14 (React)
- **Language**: TypeScript
- **Styling**: CSS Modules
- **State Management**: React Context API
- **HTTP Client**: Fetch API

### DevOps
- **Deployment**: Render (Backend), Vercel (Frontend)
- **Containerization**: Docker
- **CI/CD**: Git-based automatic deployments
- **Monitoring**: Built-in health checks and audit logging

## 🌟 Features

### 🔐 Role-Based Access Control (RBAC)
**Two-tier security model** with granular permissions:
- **USER (Claimant)**: Submit new claims, view own submissions, upload documents, correct AI-extracted fields, track claim status, respond to agent requests
- **AGENT (Full Access)**: Review all claims, approve/deny/pend decisions, request additional info, view duplicate matches, access review queue with priority sorting, manage users/plans/rules, view comprehensive analytics, audit log access

### 🤖 Intelligent Document Processing
**Multi-layered AI-powered extraction pipeline**:
- **📤 3-Step Claim Wizard**: Upload → Processing → Review workflow
- **🔍 OCR Processing**: PaddleOCR 3.x for text extraction from images and PDFs (optional, configurable for memory optimization)
- **🤖 AI Field Extraction**: Powered by ERNIE 4.5 API for intelligent structured data extraction with confidence scoring and regex fallback
- **✅ Smart Validation**: Configurable rule engine with plan-specific thresholds, coverage limits, and business logic validation
- **Multi-format Support**: Handles PDFs, images (PNG, JPG), medical bills, EOBs, and prescription receipts

### ⚡ Smart Automation
**Reduce manual work with intelligent automation**:
- **Auto-Approval Engine**: Configurable thresholds for safe automated claim approval based on amount, confidence score, OCR quality, and risk assessment
- **🔄 Duplicate Detection**: Advanced similarity matching to identify potential duplicate claims and prevent fraud (100% = exact file match)
- **Automated Workflow**: Claims automatically progress through validation, extraction, and approval stages
- **Comprehensive Audit Trail**: Complete activity logging for compliance, accountability, and debugging

### 💬 Natural Language Queries
**Ask questions about claims in plain English**:
- Conversational interface for claim information retrieval
- RBAC-enforced: Users only see data they have permission to access (Users query their own claims, Agents query all)
- Context-aware responses with source citations (claim IDs and fields)
- Powered by ERNIE 4.5 for accurate natural language understanding

### 📊 Analytics & Reporting
**Data-driven insights for all roles**:
- Real-time dashboard with key metrics (total claims, approval rates, processing times)
- Role-specific views: Personal stats for users, team metrics for agents, system-wide analytics for admins
- Trend analysis and performance tracking
- Status tracking with polling and timeline view

## 🏗️ Architecture

### System Architecture Diagram

```mermaid
graph TB
    subgraph "Client Layer"
        UI[Next.js Frontend<br/>React Components]
        Auth[Auth Context<br/>JWT Token Management]
    end

    subgraph "API Gateway Layer"
        API[FastAPI Backend<br/>RESTful API]
        MW[Middleware<br/>CORS, Auth, Logging]
    end

    subgraph "Service Layer"
        ClaimSvc[Claim Service<br/>Workflow Management]
        AuthSvc[Auth Service<br/>JWT & RBAC]
        ValidationSvc[Validation Service<br/>Rule Engine]
        AutoApprovalSvc[Auto-Approval Service<br/>Smart Decisions]
        AuditSvc[Audit Service<br/>Activity Logging]
    end

    subgraph "AI & Processing Layer"
        OCR[OCR Processor<br/>PaddleOCR]
        AI[ClaimSphere AI Service<br/>ERNIE 4.5 API]
        NLQ[Natural Language<br/>Query Processor]
    end

    subgraph "Data Layer"
        DB[(PostgreSQL/SQLite<br/>Database)]
        Cache[Session Cache]
    end

    subgraph "External Services"
        BaiduAPI[Baidu AI Studio<br/>ERNIE API]
    end

    UI -->|HTTP/HTTPS| API
    Auth -.->|JWT Token| API
    API --> MW
    MW --> ClaimSvc
    MW --> AuthSvc
    
    ClaimSvc --> ValidationSvc
    ClaimSvc --> AutoApprovalSvc
    ClaimSvc --> OCR
    ClaimSvc --> AI
    ClaimSvc --> AuditSvc
    
    AuthSvc --> DB
    ClaimSvc --> DB
    ValidationSvc --> DB
    AutoApprovalSvc --> DB
    AuditSvc --> DB
    NLQ --> DB
    
    AI --> BaiduAPI
    OCR -.->|Optional| DB
    
    AuthSvc -.-> Cache
    
    API --> NLQ

    style UI fill:#e1f5ff
    style API fill:#fff3e0
    style OCR fill:#f3e5f5
    style AI fill:#e8f5e9
    style DB fill:#fce4ec
    style BaiduAPI fill:#fff9c4
```

### Data Flow Diagram

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant OCR
    participant AI
    participant DB
    participant ValidationSvc
    participant AutoApproval

    User->>Frontend: Upload claim document
    Frontend->>API: POST /api/claims/{id}/upload
    API->>OCR: Extract text from document
    OCR-->>API: Raw text + layout
    API->>AI: Extract claim fields (ERNIE)
    AI-->>API: Structured data + confidence
    API->>DB: Save extracted fields
    API->>ValidationSvc: Validate against rules
    ValidationSvc->>DB: Query plan rules
    ValidationSvc-->>API: Validation results
    API->>AutoApproval: Check auto-approval criteria
    AutoApproval-->>API: Decision or flag for review
    API->>DB: Update claim status
    API-->>Frontend: Claim processed
    Frontend-->>User: Show extracted fields
    
    Note over User,AutoApproval: RBAC enforced at every step
```

### Project Structure

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
│           └── api.ts          # API client with token refresh
│
├── docs/                       # Documentation
│   ├── API.md                 # API documentation
│   ├── DEPLOYMENT.md          # Deployment guides
│   ├── RENDER_DEPLOYMENT.md   # Render-specific guide
│   └── VERCEL_DEPLOYMENT.md   # Vercel-specific guide
│
└── tests/                      # Test suite
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

### Entity Relationship Diagram

```mermaid
erDiagram
    User ||--o{ Claim : "submits"
    User ||--o{ MemberPolicy : "has"
    User ||--o{ Decision : "makes"
    User }|--|| Role : "has"
    
    InsuranceCompany ||--o{ Plan : "offers"
    Plan ||--o{ MemberPolicy : "covers"
    Plan ||--o{ ValidationRule : "defines"
    
    Claim ||--o{ ClaimDocument : "contains"
    Claim ||--o{ ExtractedField : "has"
    Claim ||--o{ ValidationResult : "validates"
    Claim ||--o{ Decision : "receives"
    Claim ||--o{ AuditLog : "logs"
    Claim ||--o{ DuplicateMatch : "matches"
    
    ClaimDocument ||--o{ ExtractedField : "extracts"
    
    User {
        int id PK
        string email
        string password_hash
        string full_name
        int role_id FK
        datetime created_at
    }
    
    Role {
        int id PK
        string name
        json permissions
    }
    
    Claim {
        int id PK
        int user_id FK
        int plan_id FK
        string status
        decimal amount
        datetime created_at
        datetime updated_at
    }
    
    Plan {
        int id PK
        int company_id FK
        string name
        decimal auto_approve_cap
        float min_confidence
    }
    
    ExtractedField {
        int id PK
        int claim_id FK
        string field_name
        string value
        float confidence
        boolean verified
    }
    
    Decision {
        int id PK
        int claim_id FK
        int agent_id FK
        string decision_type
        string reason
        datetime decided_at
    }
```

### Core Entities

- **User**: System users with roles (USER, AGENT)
- **Role**: USER or AGENT with different permissions
- **InsuranceCompany**: Insurance providers
- **Plan**: Insurance plans with auto-approval settings
- **MemberPolicy**: User-plan associations
- **Claim**: Insurance claims with workflow states

### Claim Workflow

```mermaid
stateDiagram-v2
    [*] --> DRAFT: Create Claim
    DRAFT --> SUBMITTED: Submit Claim
    SUBMITTED --> EXTRACTED: Upload Document
    EXTRACTED --> VALIDATED: AI Extraction Complete
    
    VALIDATED --> AUTO_APPROVED: Meets Auto-Approval Criteria
    VALIDATED --> PENDING_REVIEW: Needs Manual Review
    
    PENDING_REVIEW --> APPROVED: Agent/Admin Approves
    PENDING_REVIEW --> DENIED: Agent/Admin Denies
    PENDING_REVIEW --> PENDED: More Info Needed
    
    PENDED --> PENDING_REVIEW: Info Provided
    
    AUTO_APPROVED --> CLOSED: Auto-Close
    APPROVED --> CLOSED: Manual Close
    DENIED --> CLOSED: Manual Close
    
    CLOSED --> [*]
    
    note right of AUTO_APPROVED
        Auto-approval based on:
        - Amount threshold
        - OCR quality
        - Confidence score
        - Duplicate check
        - Fraud risk
    end note
    
    note right of PENDING_REVIEW
        Agent review queue
        Prioritized by:
        - Submission date
        - Amount
        - Risk score
    end note
```

**Workflow States:**
- `DRAFT`: Initial claim creation
- `SUBMITTED`: Claim submitted by user
- `EXTRACTED`: Fields extracted by AI
- `VALIDATED`: Passed validation rules
- `AUTO_APPROVED`: Automatically approved by system
- `PENDING_REVIEW`: Awaiting agent decision
- `APPROVED`: Manually approved
- `DENIED`: Rejected with reason
- `PENDED`: Additional information required (user can respond)
- `CLOSED`: Final state

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
HOST=0.0.0.0
FRONTEND_URL=http://localhost:3000

# OCR Configuration (Optional)
DISABLE_OCR=false                    # Set to 'true' to disable OCR (saves memory)
PADDLEOCR_USE_LITE_MODEL=true        # Use lightweight models
OMP_NUM_THREADS=1                    # OpenMP threads for memory optimization
MKL_NUM_THREADS=1                    # MKL threads for memory optimization
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

## 🚢 Deployment

### Deployment Architecture

```mermaid
graph LR
    subgraph "User Devices"
        Browser[Web Browser]
        Mobile[Mobile Browser]
    end
    
    subgraph "Vercel Edge Network"
        CDN[CDN/Edge Cache]
        Frontend[Next.js Frontend<br/>Static + SSR]
    end
    
    subgraph "Render Cloud"
        Backend[FastAPI Backend<br/>Web Service]
        DB[(PostgreSQL<br/>Database)]
    end
    
    subgraph "External APIs"
        BaiduAPI[Baidu AI Studio<br/>ERNIE 4.5]
    end
    
    Browser --> CDN
    Mobile --> CDN
    CDN --> Frontend
    Frontend -->|HTTPS/REST| Backend
    Backend --> DB
    Backend -->|AI Requests| BaiduAPI
    
    style Frontend fill:#61dafb
    style Backend fill:#009688
    style DB fill:#336791
    style BaiduAPI fill:#ffd700
```

### Production Deployment

ClaimSphere AI can be deployed to various cloud platforms:

#### Render (Backend)
**Comprehensive deployment guide**: [docs/RENDER_DEPLOYMENT.md](docs/RENDER_DEPLOYMENT.md)

**Quick Setup:**
- Automated deployment via `render.yaml` blueprint
- Free tier available (512MB RAM, OCR disabled)
- Starter plan ($7/month) for OCR support
- PostgreSQL database optional (recommended for production)
- Automatic HTTPS and health checks

**Required Environment Variables:**
- `BAIDU_API_KEY`: Your Baidu AI Studio API key
- `JWT_SECRET_KEY`: Generate with `openssl rand -hex 32`
- `FRONTEND_URL`: Your Vercel frontend URL

**Deployment Time:** 5-10 minutes for initial deployment

#### Vercel (Frontend)
- See [docs/VERCEL_DEPLOYMENT.md](docs/VERCEL_DEPLOYMENT.md) for detailed instructions
- Automatic deployments from Git
- Edge network for global performance
- Set Root Directory to `frontend` in project settings
- Environment variables via dashboard
- Instant rollbacks

#### Docker (Self-Hosted)
```bash
# Build and run with Docker Compose
docker-compose up -d
```

### Environment-Specific Configuration

**Development**
- SQLite database
- OCR enabled
- Debug mode on

**Production**
- PostgreSQL database
- OCR optional (can be disabled to save memory)
- Debug mode off
- HTTPS enabled
- CORS configured for production domain

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

## 🔧 Troubleshooting

### Common Issues

**Backend won't start**
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check if required environment variables are set in `.env`
- Verify database connection if using PostgreSQL

**OCR errors or memory issues**
- Set `DISABLE_OCR=true` in environment variables to disable OCR
- Use `PADDLEOCR_USE_LITE_MODEL=true` for lighter models
- Reduce worker threads with `OMP_NUM_THREADS=1` and `MKL_NUM_THREADS=1`

**Frontend can't connect to backend**
- Verify `NEXT_PUBLIC_API_URL` in `frontend/.env.local`
- Check CORS settings in backend (`FRONTEND_URL` environment variable)
- Ensure backend is running on the configured port

**Authentication issues**
- Verify `JWT_SECRET_KEY` is set and consistent
- Check token expiration settings
- Clear browser cookies/localStorage and login again

## 🙏 Acknowledgments

- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) - Document OCR processing
- [Baidu ERNIE](https://aistudio.baidu.com) - AI-powered field extraction via ERNIE 4.5
- [FastAPI](https://fastapi.tiangolo.com/) - High-performance Python web framework
- [Next.js](https://nextjs.org/) - React framework for production
- [PyMuPDF](https://pymupdf.readthedocs.io/) - PDF processing
- [Render](https://render.com/) - Cloud platform for backend hosting
- [Vercel](https://vercel.com/) - Platform for frontend deployment
