# ClaimSphere AI - Automated Claim Processing Agent

AI-powered insurance claim processing system with role-based access control, automated OCR extraction, intelligent validation, and natural language queries.

## Technology Stack

### Backend
- FastAPI (Python 3.10+)
- PostgreSQL / SQLite with SQLAlchemy ORM
- JWT authentication with python-jose
- **CAMEL-AI Framework** - Multi-agent system with OLLAMA (phi3:mini) and ERNIE 5.0 Thinking
  - ChatAgent for natural language queries with reasoning
  - Role-playing agents for claim review and approval
  - Specialized agents for extraction, validation, fraud detection
- **OLLAMA** - Local open-source LLM (phi3:mini) for fast, free AI processing
- Baidu ERNIE 4.5 API for AI processing (fallback)
- PaddleOCR for document processing

### Frontend
- Next.js 14 (React + TypeScript)
- CSS Modules
- React Context API
- Fetch API

### DevOps
- Deployment: Render (Backend), Vercel (Frontend)
- Docker containerization
- Git-based CI/CD
- Health checks and audit logging

## Features

### Role-Based Access Control
Two-tier security model with granular permissions:
- **USER**: Submit claims, view own submissions, upload documents, track status
- **AGENT**: Review all claims, approve/deny/pend decisions, manage users and rules, access analytics

### Intelligent Document Processing
Multi-layered AI extraction pipeline with **CAMEL-AI Multi-Agent System**:
- 3-step claim wizard (Upload → Processing → Review)
- **OCR Agent** - Document processing with PaddleOCR 3.x
- **Extraction Agent** - AI field extraction powered by OLLAMA/ERNIE 5.0 Thinking (via CAMEL-AI ChatAgent)
- **Validation Agent** - Smart validation with reasoning traces (CAMEL-AI ChatAgent)
- **Fraud Detection Agent** - Risk assessment with explainable AI (CAMEL-AI ChatAgent)
- **Duplicate Detection Agent** - Prevents duplicate submissions
- **Query Agent** - Natural language queries with reasoning (OLLAMA phi3:mini)
- **Review Agent** - Role-playing agent for claim review (OLLAMA phi3:mini)
- **Approval Agent** - Role-playing agent for claim approval (OLLAMA phi3:mini)
- **Role-Playing Coordinator** - Orchestrates multi-agent discussions
- Multi-format support (PDF, PNG, JPG)

### Smart Automation
- Auto-approval engine with configurable thresholds
- Duplicate detection to prevent fraud
- Automated workflow progression
- Comprehensive audit trail

### Natural Language Queries (AI Assistant)
- **Query Agent** - Ask questions about claims in plain English using CAMEL-AI ChatAgent
- Powered by OLLAMA (phi3:mini) for fast, local processing
- RBAC-enforced data access
- **Concise, relevant answers** - Short, focused responses with key facts
- Context-aware responses with source citations
- **Reasoning traces** - See how the AI arrived at answers
- Cited claims and fields used displayed clearly
- Quick query buttons for instant processing

### Analytics & Reporting
- Real-time dashboard with key metrics
- Role-specific views
- Trend analysis and performance tracking

## Architecture

> **📖 For detailed architecture documentation, see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)**

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

    subgraph "AI & Processing Layer - CAMEL-AI Multi-Agent System"
        AgentCoord[Agent Coordinator<br/>Orchestrates Agents]
        OCRAgent[OCR Agent<br/>PaddleOCR]
        ExtractAgent[Extraction Agent<br/>CAMEL-AI ChatAgent]
        ValidAgent[Validation Agent<br/>CAMEL-AI ChatAgent]
        FraudAgent[Fraud Detection Agent<br/>CAMEL-AI ChatAgent]
        QueryAgent[Query Agent<br/>CAMEL-AI ChatAgent]
        ReviewAgent[Review Agent<br/>CAMEL-AI Role-Playing]
        ApproveAgent[Approval Agent<br/>CAMEL-AI Role-Playing]
        FallbackAI[ERNIE Service<br/>Fallback API]
    end

    subgraph "Data Layer"
        DB[(PostgreSQL/SQLite<br/>Database)]
        Cache[Session Cache]
    end

    subgraph "External Services"
        QianfanAPI[Qianfan Platform<br/>ERNIE 5.0 Thinking]
        BaiduAPI[Baidu AI Studio<br/>ERNIE 4.5 API<br/>Fallback]
    end

    UI -->|HTTP/HTTPS| API
    Auth -.->|JWT Token| API
    API --> MW
    MW --> ClaimSvc
    MW --> AuthSvc
    
    ClaimSvc --> AgentCoord
    ClaimSvc --> ValidationSvc
    ClaimSvc --> AutoApprovalSvc
    ClaimSvc --> AuditSvc
    
    AgentCoord --> OCRAgent
    AgentCoord --> ExtractAgent
    AgentCoord --> ValidAgent
    AgentCoord --> FraudAgent
    AgentCoord --> QueryAgent
    AgentCoord --> ReviewAgent
    AgentCoord --> ApproveAgent
    
    ExtractAgent --> FallbackAI
    ValidAgent --> FallbackAI
    QueryAgent --> FallbackAI
    
    AuthSvc --> DB
    ClaimSvc --> DB
    ValidationSvc --> DB
    AutoApprovalSvc --> DB
    AuditSvc --> DB
    
    FallbackAI --> BaiduAPI
    OCRAgent -.->|Optional| DB
    
    AuthSvc -.-> Cache
    
    ExtractAgent --> QianfanAPI
    ValidAgent --> QianfanAPI
    FraudAgent --> QianfanAPI
    QueryAgent --> QianfanAPI
    ReviewAgent --> QianfanAPI
    ApproveAgent --> QianfanAPI

    style UI fill:#e1f5ff
    style API fill:#fff3e0
    style AgentCoord fill:#e8f5e9
    style ExtractAgent fill:#c8e6c9
    style QueryAgent fill:#c8e6c9
    style ReviewAgent fill:#c8e6c9
    style ApproveAgent fill:#c8e6c9
    style DB fill:#fce4ec
    style QianfanAPI fill:#4caf50
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
    Frontend->>API: POST /api/claims/upload
    API->>DB: Create claim record (DRAFT)
    
    alt OCR Enabled
        API->>AgentCoord: Process document
    AgentCoord->>OCRAgent: Extract text from document
        OCRAgent-->>AgentCoord: Raw text + quality score
    else OCR Disabled
        API->>API: Skip OCR, use minimal text
    end
    
    API->>AgentCoord: Process claim with multi-agent system
    AgentCoord->>ExtractAgent: Extract fields (CAMEL-AI ChatAgent)
    ExtractAgent->>QianfanAPI: ERNIE 5.0 Thinking API
    QianfanAPI-->>ExtractAgent: Structured data + reasoning
    ExtractAgent-->>AgentCoord: Extracted fields
    AgentCoord->>ValidAgent: Validate claim (CAMEL-AI ChatAgent)
    ValidAgent->>QianfanAPI: ERNIE 5.0 Thinking API
    QianfanAPI-->>ValidAgent: Validation results + reasoning
    ValidAgent-->>AgentCoord: Validation results
    AgentCoord->>FraudAgent: Assess fraud risk (CAMEL-AI ChatAgent)
    FraudAgent->>QianfanAPI: ERNIE 5.0 Thinking API
    QianfanAPI-->>FraudAgent: Risk assessment + reasoning
    FraudAgent-->>AgentCoord: Fraud risk score
    AgentCoord-->>API: Complete processing results
    API->>DB: Save extracted fields (status: EXTRACTED)
    
    API->>DB: Check for duplicate claims
    DB-->>API: Duplicate matches (if any)
    
    API->>ValidationSvc: Validate against rules
    ValidationSvc->>DB: Query plan rules
    ValidationSvc-->>API: Validation results
    API->>DB: Save validation results (status: VALIDATED)
    
    API->>AutoApproval: Check auto-approval criteria
    AutoApproval->>DB: Query plan thresholds
    AutoApproval-->>API: Decision (AUTO_APPROVED or PENDING_REVIEW)
    API->>DB: Update claim status
    
    API-->>Frontend: Claim processed with extracted fields
    Frontend-->>User: Show extracted fields & status
    
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
│   ├── agents/                 # CAMEL-AI Multi-Agent System
│   │   ├── base_agent.py      # Base agent class
│   │   ├── ocr_agent.py        # OCR Agent (PaddleOCR)
│   │   ├── extraction_agent.py # Extraction Agent (CAMEL-AI ChatAgent)
│   │   ├── validation_agent.py # Validation Agent (CAMEL-AI ChatAgent)
│   │   ├── fraud_detection_agent.py # Fraud Agent (CAMEL-AI ChatAgent)
│   │   ├── duplicate_agent.py  # Duplicate Detection Agent
│   │   ├── query_agent.py      # Query Agent (CAMEL-AI ChatAgent)
│   │   ├── review_agent.py     # Review Agent (CAMEL-AI Role-Playing)
│   │   ├── approval_agent.py  # Approval Agent (CAMEL-AI Role-Playing)
│   │   ├── role_playing_coordinator.py # Role-Playing Coordinator
│   │   ├── orchestrator.py    # Agent Orchestrator
│   │   └── workflows.py        # Multi-agent workflows
│   ├── services/               # Business logic
│   │   ├── claim_service.py   # Claim processing & OCR
│   │   ├── validation_service.py
│   │   ├── auto_approval_service.py
│   │   ├── audit_service.py
│   │   └── agent_coordinator.py # CAMEL-AI Agent Coordinator
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
│   ├── ARCHITECTURE.md        # System architecture & CAMEL-AI design
│   ├── CAMEL_AI_SETUP.md      # CAMEL-AI setup guide
│   ├── CAMEL_AI_USAGE_AND_TESTING.md # CAMEL-AI usage guide
│   ├── ROLE_PLAYING_GUIDE.md  # Role-playing agents guide
│   ├── ROLE_PLAYING_UI_INTEGRATION.md # UI integration guide
│   ├── RENDER_DEPLOYMENT.md   # Render-specific guide
│   └── VERCEL_DEPLOYMENT.md   # Vercel-specific guide
│
└── tests/                      # Test suite
```

## Quick Start

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
# Edit .env with your API keys:
# - OLLAMA_BASE_URL=http://localhost:11434 (default, uses local OLLAMA)
# - USE_OLLAMA=true (enable OLLAMA, default: true)
# - QIANFAN_API_KEY (optional, for ERNIE 5.0 Thinking fallback)
# - BAIDU_API_KEY and BAIDU_SECRET_KEY (optional, for ERNIE 4.5 fallback)

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

## Data Models

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

## Configuration

### Environment Variables

```bash
# OLLAMA Configuration (Primary - Local, Free, Fast)
OLLAMA_BASE_URL=http://localhost:11434  # or http://ollama:11434 for Docker
USE_OLLAMA=true  # Enable OLLAMA (default: true)
USE_OLLAMA_FOR_QUERIES=true  # Use OLLAMA for queries (default: true)

# CAMEL-AI / Qianfan Platform (Optional - for ERNIE 5.0 Thinking fallback)
QIANFAN_API_KEY=your-qianfan-api-key

# Baidu AI Studio API (Optional - for ERNIE 4.5 fallback)
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

## API Authentication

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

## API Endpoints

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

## Duplicate Detection

The system detects potential duplicate claims using:

1. **File Hash Matching** (100% score): Exact same file uploaded
2. **Content Similarity**: Matching amount, date, provider, category, procedure codes

When duplicates are detected:
- User sees a warning with the duplicate score
- Agent can review duplicate matches in the claim details
- Claims are still processed but flagged for review

## Deployment

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
See [docs/RENDER_DEPLOYMENT.md](docs/RENDER_DEPLOYMENT.md) for complete instructions.

Quick setup:
- Use `render.yaml` blueprint for automated deployment
- Free tier available (512MB RAM, OCR disabled)
- Requires: `BAIDU_API_KEY`, `JWT_SECRET_KEY`, `FRONTEND_URL`
- Deployment time: 5-10 minutes

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

## Development

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

**CAMEL-AI / ERNIE API failing?**
- Verify your `QIANFAN_API_KEY` in `.env` (primary for CAMEL-AI)
- Verify your `BAIDU_API_KEY` and `BAIDU_SECRET_KEY` for fallback
- Check CAMEL-AI setup: See [docs/CAMEL_AI_SETUP.md](docs/CAMEL_AI_SETUP.md)
- The system falls back to direct ERNIE API if CAMEL-AI fails
- Check logs for specific error messages

**Frontend not connecting?**
- Ensure `NEXT_PUBLIC_API_URL=http://localhost:8000` in `frontend/.env.local`
- Check backend CORS settings include your frontend port

## 📝 License

MIT License - See LICENSE file for details.

## Troubleshooting

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

## CAMEL-AI Multi-Agent System

ClaimSphere AI uses the **CAMEL-AI framework** to build a sophisticated multi-agent system for intelligent claim processing.

### Agent Architecture

The system includes specialized agents, each with a specific role:

1. **OCR Agent** - Extracts text from documents using PaddleOCR
2. **Extraction Agent** - Uses CAMEL-AI ChatAgent with ERNIE 5.0 Thinking to extract structured claim data
3. **Validation Agent** - Validates claims using CAMEL-AI ChatAgent with reasoning traces
4. **Fraud Detection Agent** - Assesses fraud risk using CAMEL-AI ChatAgent
5. **Duplicate Detection Agent** - Identifies duplicate claims
6. **Query Agent** - Answers natural language questions using CAMEL-AI ChatAgent
7. **Review Agent** - Role-playing agent that acts as a Senior Claims Reviewer
8. **Approval Agent** - Role-playing agent that makes approval decisions

### CAMEL-AI ChatAgent Integration

AI-powered agents use CAMEL-AI's `ChatAgent` class with OLLAMA (primary) or ERNIE 5.0 Thinking (fallback):

```python
from camel.agents import ChatAgent
from camel.models import OllamaModel
from camel.messages import BaseMessage

# Create OLLAMA model (phi3:mini - fast, local, free)
model = OllamaModel(
    model_type='phi3:mini',
    model_config_dict={
        'temperature': 0.2,
        'max_tokens': 256
    },
    url='http://localhost:11434/v1',
    timeout=90.0
)

# Create ChatAgent
system_message = BaseMessage.make_system_message(
    role_name="Assistant",
    content="Your system message"
)
agent = ChatAgent(
    system_message=system_message,
    model=model,
    step_timeout=95.0
)

# Process query
response = agent.step(user_message)
```

### Role-Playing Agents

The system includes role-playing agents that simulate human-like interactions:

- **Review Agent**: Acts as a Senior Claims Reviewer with 15 years of experience
- **Approval Agent**: Acts as a Claims Approver with decision-making authority
- **Role-Playing Coordinator**: Orchestrates conversations between Review and Approval agents

See [docs/ROLE_PLAYING_GUIDE.md](docs/ROLE_PLAYING_GUIDE.md) for detailed information.

### Setup and Configuration

1. **Install CAMEL-AI**:
   ```bash
   pip install 'camel-ai[all]'
   ```

2. **Setup OLLAMA** (Recommended - Free, Local):
   - Install OLLAMA: See [OLLAMA_SETUP.md](OLLAMA_SETUP.md)
   - Pull model: `ollama pull phi3:mini`
   - Configure: `OLLAMA_BASE_URL=http://localhost:11434` and `USE_OLLAMA=true`

3. **Get Qianfan API Key** (Optional - Fallback):
   - Visit: https://console.bce.baidu.com/qianfan/overview
   - Create an API key
   - Add to `.env`: `QIANFAN_API_KEY=your-key`

4. **Configure Environment**:
   ```bash
   DISABLE_MODEL_SOURCE_CHECK=True  # Skip connectivity checks
   USE_OLLAMA=true  # Enable OLLAMA (default)
   OLLAMA_BASE_URL=http://localhost:11434
   QIANFAN_API_KEY=your-key  # Optional fallback
   ```

For detailed setup instructions, see [docs/CAMEL_AI_SETUP.md](docs/CAMEL_AI_SETUP.md).

### Benefits of CAMEL-AI Integration

- **OLLAMA Support**: Fast, local, free AI processing with phi3:mini
- **Reasoning Traces**: Access to AI reasoning process for transparency
- **Multi-Agent Coordination**: Agents work together seamlessly
- **Role-Playing**: Simulates realistic human-like claim review processes
- **Concise Responses**: Query agent provides short, focused answers
- **Extensibility**: Easy to add new specialized agents
- **Fallback Support**: Gracefully falls back to ERNIE API if OLLAMA unavailable

## 🙏 Acknowledgments

- [CAMEL-AI](https://www.camel-ai.org) - Multi-agent framework for building intelligent systems
- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) - Document OCR processing
- [Baidu ERNIE](https://aistudio.baidu.com) - AI-powered field extraction via ERNIE 4.5 & 5.0 Thinking
- [FastAPI](https://fastapi.tiangolo.com/) - Python web framework
- [Next.js](https://nextjs.org/) - React framework
- [Render](https://render.com/) - Backend hosting
- [Vercel](https://vercel.com/) - Frontend deployment
