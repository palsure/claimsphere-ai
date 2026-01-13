# ClaimSphere AI Architecture

## Overview

ClaimSphere AI is built on a **multi-agent architecture** powered by the CAMEL-AI framework, enabling intelligent, explainable, and scalable claim processing.

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                            │
│  Next.js Frontend (React + TypeScript)                          │
│  - Claim Upload & Wizard                                         │
│  - Natural Language Query Interface                              │
│  - Role-Playing Review Interface                                 │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        │ HTTP/REST API
                        │
┌───────────────────────▼─────────────────────────────────────────┐
│                      API Gateway Layer                           │
│  FastAPI Backend                                                 │
│  - Authentication & Authorization (JWT + RBAC)                  │
│  - Request Routing & Validation                                  │
│  - CORS & Middleware                                             │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        │ Service Calls
                        │
┌───────────────────────▼─────────────────────────────────────────┐
│                   Service Layer                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Claim Service                                            │  │
│  │  - Workflow Management                                     │  │
│  │  - Status Transitions                                      │  │
│  │  - Decision Processing                                     │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Agent Coordinator                                        │  │
│  │  - Agent Lifecycle Management                             │  │
│  │  - Agent Initialization                                    │  │
│  │  - Fallback Handling                                       │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Validation Service                                       │  │
│  │  - Rule Engine                                            │  │
│  │  - Policy Enforcement                                     │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Auto-Approval Service                                    │  │
│  │  - Threshold Evaluation                                   │  │
│  │  - Risk Assessment                                        │  │
│  └──────────────────────────────────────────────────────────┘  │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        │ Agent Orchestration
                        │
┌───────────────────────▼─────────────────────────────────────────┐
│            CAMEL-AI Multi-Agent System                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Agent Orchestrator                                      │  │
│  │  - Workflow Coordination                                 │  │
│  │  - Agent Sequencing                                      │  │
│  │  - Error Handling                                        │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  OCR Agent   │  │ Extraction   │  │ Validation  │          │
│  │  (PaddleOCR) │  │   Agent      │  │   Agent     │          │
│  │              │  │ (ChatAgent)  │  │ (ChatAgent) │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Fraud Detect │  │   Query      │  │   Review    │          │
│  │   Agent      │  │   Agent      │  │   Agent     │          │
│  │ (ChatAgent)  │  │ (ChatAgent)  │  │ (Role-Play) │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐                            │
│  │  Approval    │  │  Duplicate   │                            │
│  │   Agent      │  │   Agent      │                            │
│  │ (Role-Play)  │  │              │                            │
│  └──────────────┘  └──────────────┘                            │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        │ API Calls
                        │
┌───────────────────────▼─────────────────────────────────────────┐
│                    External Services                             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  OLLAMA (Primary)                                         │  │
│  │  - Local LLM Server (phi3:mini)                           │  │
│  │  - Free, Fast, Privacy-Preserving                         │  │
│  │  - OpenAI-compatible API                                  │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Qianfan Platform (Fallback)                              │  │
│  │  - ERNIE 5.0 Thinking API                                 │  │
│  │  - Reasoning Traces                                       │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Baidu AI Studio (Fallback)                              │  │
│  │  - ERNIE 4.5 API                                         │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## CAMEL-AI Agent Architecture

### Agent Types

#### 1. **Base Agent** (`base_agent.py`)
- Common functionality for all agents
- Model initialization (ERNIE 5.0 Thinking)
- Message handling
- Error handling and logging

#### 2. **Specialized Agents**

##### OCR Agent
- **Technology**: PaddleOCR 3.x
- **Purpose**: Extract text from documents
- **Input**: Document bytes (PDF, images)
- **Output**: Text, layout, quality score

##### Extraction Agent
- **Technology**: CAMEL-AI ChatAgent + ERNIE 5.0 Thinking
- **Purpose**: Extract structured claim data from OCR text
- **Input**: OCR text, layout information
- **Output**: Structured JSON (claimant_name, provider_name, date, amount, etc.)
- **Features**: Reasoning traces, confidence scores

##### Validation Agent
- **Technology**: CAMEL-AI ChatAgent + ERNIE 5.0 Thinking
- **Purpose**: Validate claim data against rules
- **Input**: Extracted claim data
- **Output**: Validation results (is_valid, errors, recommendations, risk_level)
- **Features**: Explainable validation decisions

##### Fraud Detection Agent
- **Technology**: CAMEL-AI ChatAgent + ERNIE 5.0 Thinking
- **Purpose**: Assess fraud risk
- **Input**: Claim data + historical claims
- **Output**: Fraud risk score (0-1.0) + reasons
- **Features**: Pattern analysis, anomaly detection

##### Duplicate Detection Agent
- **Technology**: Rule-based similarity + optional AI
- **Purpose**: Detect duplicate claims
- **Input**: New claim + existing claims
- **Output**: Duplicate matches with similarity scores

##### Query Agent
- **Technology**: CAMEL-AI ChatAgent + OLLAMA (phi3:mini)
- **Purpose**: Answer natural language questions with concise, relevant answers
- **Input**: User query + claims context (limited to 8 recent claims)
- **Output**: Short, focused answer + cited claims + fields used + reasoning
- **Features**: RBAC-enforced, context-aware, reasoning traces, concise responses (max 150 chars main answer)
- **Optimization**: Ultra-compact prompts, minimal token usage, 90s timeout

##### Review Agent (Role-Playing)
- **Technology**: CAMEL-AI ChatAgent + OLLAMA (phi3:mini)
- **Purpose**: Act as Senior Claims Reviewer
- **Persona**: 15 years of experience, thorough and detail-oriented
- **Input**: Claim data (truncated for efficiency)
- **Output**: Review assessment with recommendations, reasoning, confidence scores, key findings, concerns

##### Approval Agent (Role-Playing)
- **Technology**: CAMEL-AI ChatAgent + OLLAMA (phi3:mini)
- **Purpose**: Make final approval decisions
- **Persona**: Claims Approver with decision authority
- **Input**: Claim data + review results (truncated for efficiency)
- **Output**: Decision (approve/deny/pend) with reasoning, policy references, conditions

### Agent Coordination

#### Agent Coordinator (`agent_coordinator.py`)
- Manages agent lifecycle
- Initializes agents on demand
- Provides unified interface for agent access
- Handles fallback scenarios

#### Orchestrator (`orchestrator.py`)
- Coordinates multi-agent workflows
- Manages agent sequencing
- Handles error recovery
- Provides workflow abstraction

#### Role-Playing Coordinator (`role_playing_coordinator.py`)
- Orchestrates conversations between Review and Approval agents
- Manages multi-turn discussions
- Tracks discussion history
- Generates final decisions

## Data Flow

### Claim Processing Workflow

```
1. User Uploads Document
   ↓
2. OCR Agent
   - Extracts text from document
   - Returns: text, layout, quality_score
   ↓
3. Extraction Agent (CAMEL-AI ChatAgent)
   - Analyzes OCR text
   - Extracts structured fields
   - Returns: claim_data + reasoning
   ↓
4. Validation Agent (CAMEL-AI ChatAgent)
   - Validates claim data
   - Checks against rules
   - Returns: validation_result + reasoning
   ↓
5. Fraud Detection Agent (CAMEL-AI ChatAgent)
   - Assesses fraud risk
   - Analyzes patterns
   - Returns: fraud_risk_score + reasons
   ↓
6. Duplicate Detection Agent
   - Compares with existing claims
   - Calculates similarity
   - Returns: duplicate_matches
   ↓
7. Auto-Approval Service
   - Evaluates thresholds
   - Makes decision
   - Returns: status (AUTO_APPROVED or PENDING_REVIEW)
```

### Natural Language Query Flow

```
1. User Submits Query
   ↓
2. Query Agent (CAMEL-AI ChatAgent)
   - Receives query + claims context
   - Analyzes with ERNIE 5.0 Thinking
   - Generates answer with reasoning
   - Extracts citations
   ↓
3. Response
   - Natural language answer
   - Cited claim numbers
   - Fields used
   - Reasoning trace
```

### Role-Playing Review Flow

```
1. Claim Submitted for Review
   ↓
2. Review Agent (CAMEL-AI Role-Playing)
   - Acts as Senior Claims Reviewer
   - Reviews claim data
   - Provides assessment
   ↓
3. Approval Agent (CAMEL-AI Role-Playing)
   - Acts as Claims Approver
   - Reviews reviewer's assessment
   - Makes decision
   ↓
4. Optional Discussion
   - Multi-turn conversation
   - Agents discuss concerns
   - Reach consensus
   ↓
5. Final Decision
   - Approve / Deny / Pend
   - With reasoning and conditions
```

## Technology Stack

### Backend Framework
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: ORM for database operations
- **PostgreSQL/SQLite**: Database storage

### AI Framework
- **CAMEL-AI**: Multi-agent framework
  - ChatAgent for conversational agents
  - ModelFactory for model creation
  - BaseMessage for message handling
- **ERNIE 5.0 Thinking**: Reasoning-capable LLM
- **PaddleOCR**: Document OCR processing

### Authentication & Security
- **JWT**: Token-based authentication
- **RBAC**: Role-based access control
- **python-jose**: JWT implementation

### Frontend
- **Next.js 14**: React framework
- **TypeScript**: Type safety
- **CSS Modules**: Scoped styling

## Agent Communication Patterns

### 1. Sequential Processing
Agents process in sequence, each building on previous results:
```
OCR → Extraction → Validation → Fraud Detection
```

### 2. Parallel Processing
Some agents can run in parallel:
```
Validation + Fraud Detection (parallel)
```

### 3. Role-Playing Conversations
Agents engage in multi-turn discussions:
```
Review Agent ↔ Approval Agent
  (discussion)
  ↓
Final Decision
```

## Error Handling & Fallbacks

### Fallback Strategy

1. **CAMEL-AI Unavailable**
   - Falls back to direct ERNIE API
   - Uses `ErnieService` for basic functionality

2. **Agent Failure**
   - Logs error
   - Returns partial results
   - Continues with available data

3. **API Errors**
   - Retries with exponential backoff
   - Falls back to rule-based processing
   - Provides user-friendly error messages

## Performance Considerations

### Agent Initialization
- Agents are lazy-loaded
- Initialized on first use
- Cached for subsequent requests

### Token Management
- Context limited to recent 20 claims
- Text truncation for long documents
- Efficient prompt engineering

### Memory Management
- OCR processor can be disabled
- Lightweight models available
- Garbage collection after processing

## Security & Privacy

### RBAC Enforcement
- User: Own claims only
- Agent: Assigned + pending claims
- Admin: All claims

### Data Isolation
- Claims filtered by user role
- Query context scoped to accessible data
- Audit logging for all actions

### API Security
- JWT authentication required
- Token refresh mechanism
- CORS protection

## Scalability

### Horizontal Scaling
- Stateless agents
- Database-backed state
- Load balancer compatible

### Vertical Scaling
- Agent pooling
- Connection reuse
- Efficient resource usage

## Monitoring & Observability

### Logging
- Agent actions logged
- Reasoning traces captured
- Error tracking

### Metrics
- Agent performance
- API response times
- Error rates

## Future Enhancements

### Planned Improvements
1. **Agent Specialization**: More specialized agents for specific claim types
2. **Learning Agents**: Agents that learn from decisions
3. **Multi-Model Support**: Support for additional LLMs
4. **Agent Marketplace**: Pluggable agent architecture
5. **Distributed Agents**: Agents across multiple nodes

## References

- [CAMEL-AI Documentation](https://www.camel-ai.org)
- [ERNIE 5.0 Thinking](https://cloud.baidu.com/product/wenxinworkshop)
- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)
- [FastAPI](https://fastapi.tiangolo.com/)
