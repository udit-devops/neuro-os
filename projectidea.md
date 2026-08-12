# NeuroOS — Project Context

## 1. Project Identity

NeuroOS is a production-grade, AI-native knowledge workspace platform.

NeuroOS is NOT a Jarvis, voice assistant, or personal desktop assistant.

The core idea is a "Second Brain" for users and teams.

Users have isolated workspaces where they can organize and connect their knowledge, upload documents, search their knowledge semantically, and eventually interact with AI agents and tools.

The long-term vision is:

    User
      ↓
    Workspace
      ↓
    Knowledge Sources
      ↓
    Ingestion Pipeline
      ↓
    Knowledge Base
      ↓
    Retrieval
      ↓
    AI
      ↓
    Agents / Tools / Memory

The platform should eventually support:

- Documents
- PDFs
- Markdown
- Source code
- GitHub repositories
- Google Drive
- Notion
- Other knowledge sources
- AI chat
- RAG
- Conversation history
- Long-term memory
- AI agents
- Tool calling
- Streaming
- Search
- Workflow automation

The project is intended to demonstrate strong:

- Backend engineering
- AI engineering
- System design
- Infrastructure
- Security
- Scalability
- Production architecture

This is a flagship portfolio/resume project, but it should be engineered as if it could evolve into a real SaaS product.

---

# 2. Core Product Problem

Modern knowledge is scattered across:

- PDFs
- Documents
- Notes
- GitHub
- Google Drive
- Notion
- Emails
- Local files
- Conversations

Users often remember that they have seen information somewhere but cannot easily find it.

NeuroOS centralizes and indexes this knowledge so users can ask questions such as:

> "Where did we decide to use Redis?"

> "Summarize the architecture document."

> "Where is JWT authentication implemented in my repository?"

> "What did we decide about the product roadmap?"

The AI should answer using the user's own knowledge and provide source context where appropriate.

---

# 3. Core Product Model

The current fundamental relationship is:

    User
      │
      │ 1:N
      ▼
    Workspace
      │
      │ 1:N
      ▼
    Document

A User can own multiple Workspaces.

A Workspace belongs to one User.

A Workspace can contain many Documents.

Documents must always respect Workspace ownership.

Future entities will include things such as:

- Conversation
- Message
- Memory
- Chunk
- Embedding
- Agent
- Task
- Tool
- KnowledgeSource

These should be introduced only when the corresponding feature requires them.

---

# 4. Technology Stack

## Backend

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy ORM
- Pydantic v2
- JWT authentication
- Redis
- Alembic

## Infrastructure

- Docker
- Docker Compose

## AI — Future / Current Phase

- Embeddings
- Vector database/vector search
- LLM provider
- RAG
- LangGraph
- AI agents
- Tool calling
- MCP where appropriate

## Frontend

- React

The frontend will be implemented separately after the backend AI MVP is complete.

---

# 5. Backend Architecture

Use a clean layered architecture:

    HTTP Request
          ↓
       Router
          ↓
       Service
          ↓
      Repository/ORM
          ↓
      PostgreSQL

Rules:

- Routers must remain thin.
- Business logic belongs in services.
- SQLAlchemy models represent database entities.
- Pydantic schemas represent API input/output.
- Authentication/authorization should be enforced consistently.
- Do not put business logic directly into route handlers.
- Do not put HTTP-specific logic inside services.
- Do not tightly couple AI providers to application logic.
- Prefer clear interfaces and replaceable components where external providers are involved.

Follow the existing project conventions rather than creating a completely different architecture.

---

# 6. Current Project Status

## Phase 1 — Authentication

Status: COMPLETE with minor technical debt.

Completed:

- FastAPI setup
- PostgreSQL
- SQLAlchemy
- User model
- User CRUD
- Password hashing
- JWT authentication
- OAuth2
- Protected routes
- `get_current_user`
- `/users/me`

Known technical debt:

- `GET /users` should eventually require authentication.
- `DELETE /users/{id}` should eventually require authentication.
- User field validation can be strengthened.
- Password strength validation can be improved.
- CORS and centralized logging should be finalized before production deployment.

Do not block current AI development unnecessarily on these items.

---

# 7. Phase 2 — Workspaces

Status: COMPLETE.

Implemented:

- Workspace model
- Workspace CRUD
- Ownership enforcement
- Validation
- Pagination
- Cascade deletion
- Alembic migration
- Workspace/user relationship

Important design:

`Workspace.owner_id` references `users.id`.

Workspace ownership is enforced at the service layer.

---

# 8. Phase 3 — Documents

Status: COMPLETE.

Implemented:

- Document model
- Document metadata CRUD
- Workspace/document relationship
- Nested routes
- Ownership isolation
- Composite indexes
- Cascade deletion
- Validation

At this stage Documents represent document metadata.

Actual document ingestion and AI processing belongs to Phase 4.

---

# 9. Infrastructure Already Implemented

Redis is already available.

A custom Redis-backed sliding-window rate limiter has been implemented for authentication-sensitive endpoints such as:

- login
- signup

The project uses Docker Compose.

Alembic is available and should be used for future database schema changes.

Requirements are pinned.

Database migrations should remain synchronized.

Do not introduce duplicate infrastructure without a clear reason.

---

# 10. Phase 4 — Ingestion + RAG Foundation (Completed)

Phase 4 is the beginning of the actual AI pipeline.

Goal:

    Upload Document
          ↓
    File Storage
          ↓
    Background Processing
          ↓
    File Validation
          ↓
    Text Extraction
          ↓
    Text Cleaning
          ↓
    Chunking
          ↓
    Embeddings
          ↓
    Vector Storage
          ↓
    Retrieval
          ↓
    Basic RAG
          ↓
    Grounded AI Response

Phase 4 should transform NeuroOS from a CRUD backend into an AI knowledge system.

Phase 4 should support an initial set of practical document formats such as:

- PDF
- TXT
- Markdown
- DOCX where appropriate

Do not build the React frontend during Phase 4.

---

# 11. Phase 4 Engineering Requirements

Phase 4 must be production-oriented.

Do not implement everything as one FastAPI route.

Separate responsibilities such as:

- Upload API
- Storage service
- File validation
- Document processing
- Text extraction
- Text cleaning
- Chunking
- Embedding service
- Vector store
- Retrieval service
- RAG service
- Background processing

Long-running document processing should not block normal HTTP requests.

Use background processing/worker architecture appropriate for the current stack.

Redis can be used where it provides real value.

Do not add infrastructure merely to make the architecture look complicated.

---

# 12. Storage Architecture

File storage must be abstracted.

Development may use local storage.

Production should be able to move toward object storage such as:

- S3
- S3-compatible storage
- Cloud object storage

without rewriting the entire application.

Avoid tightly coupling business logic to local filesystem paths.

Uploaded files are untrusted input.

Consider:

- file size limits
- allowed types
- MIME validation
- filename safety
- path traversal
- malicious files
- resource exhaustion

---

# 13. Document Processing

Documents should have a clear processing lifecycle.

Example:

    UPLOADED
       ↓
    PROCESSING
       ↓
    COMPLETED

or:

    PROCESSING
       ↓
     FAILED

Failures should be visible and recoverable where appropriate.

Processing should record useful metadata such as:

- processing status
- error information
- timestamps
- file type
- file size
- processing duration where useful

---

# 14. Text Extraction

Use an extensible extraction architecture.

Conceptually:

    Document
       ↓
    Extractor
       ↓
    Normalized Text

Different formats should be handled by appropriate extractors.

The extraction layer should be replaceable and testable.

Handle:

- corrupt files
- unsupported formats
- empty documents
- extraction failures
- very large files

---

# 15. Chunking

Chunk extracted text into smaller units suitable for retrieval.

Chunking should consider:

- chunk size
- overlap
- paragraph boundaries
- sentence boundaries where appropriate
- metadata
- source document
- chunk ordering
- Every chunk must remain traceable to its source Document.

Avoid blindly splitting text without understanding retrieval implications.

---

# 16. Embeddings

Embeddings convert text into numerical vectors representing semantic meaning.

Use an abstraction such as:

    EmbeddingService
          ↓
    Embedding Provider/Model

Do not tightly couple the entire application to one provider.

Important concepts:

- embedding dimensions
- similarity
- model choice
- batch processing
- model changes
- re-indexing

Changing embedding models can require re-embedding existing data.

---

# 17. Vector Storage

The vector layer must support:

- storing embeddings
- storing chunk metadata
- similarity search
- workspace filtering
- document filtering
- source tracing
- Workspace isolation is critical.
- A user must NEVER retrieve vector chunks belonging to another user's workspace.
- Vector retrieval must enforce ownership boundaries.

Prefer an architecture that integrates naturally with PostgreSQL when practical instead of automatically adding another database.

---

# 18. Retrieval

Conceptually:

    User Question
          ↓
    Query Embedding
          ↓
    Vector Search
          ↓
    Metadata Filtering
          ↓
    Top-K Chunks
          ↓
    Context

Retrieval should be implemented independently of HTTP.

Important concepts:

- top-k
- similarity
- metadata filtering
- relevance
- retrieval quality
- future reranking

Do not add complex reranking unless there is a clear reason.

---

# 19. RAG

Basic RAG:

    User Question
          ↓
    Query Embedding
          ↓
    Retrieve Relevant Chunks
          ↓
    Build Context
          ↓
    LLM
          ↓
    Grounded Answer

The LLM should be instructed to use retrieved context and avoid inventing unsupported facts.

Answers should eventually include source metadata so the frontend can show where the information came from.

---

# 20. Security

Treat documents and document contents as untrusted.

Important concerns:

- Authentication
- Authorization
- Workspace isolation
- File validation
- File size limits
- Path traversal
- Malicious documents
- Prompt injection inside documents
- Resource exhaustion
- Secrets management
- Sensitive logging

Never assume retrieved document text is safe instructions for the AI.

---

# 21. Performance

Design for efficient processing.

Avoid:

- blocking HTTP requests with expensive processing
- unnecessary database queries
- loading huge files into memory unnecessarily
- duplicate embedding operations
- duplicate document processing

Consider:

- batching embeddings
- deterministic identifiers
- idempotent processing
- retries
- caching
- background workers

Redis should be introduced for real use cases such as:

- rate limiting
- caching
- queues/state where appropriate

Do not cache everything.

---

# 22. Observability

Important processing stages should be observable.

Log events such as:

- document uploaded
- processing started
- extraction completed
- chunking completed
- embedding started/completed
- vector indexing completed
- processing failed
- processing duration

Never log:

- passwords
- JWT secrets
- API keys
- full sensitive document contents

Future production architecture can introduce:

- structured logging
- metrics
- tracing
- OpenTelemetry
- error tracking

---

# 23. Database Rules

Use Alembic for schema changes.

Do not rely on `Base.metadata.create_all()` for ongoing production schema evolution.

Every new model/column/index/constraint should have a migration.

Review migrations rather than blindly trusting autogenerated migrations.

---

# 24. Testing

Important behavior must have tests.

Phase 4 should test:

- upload authorization
- file validation
- supported file types
- unsupported files
- processing states
- extraction
- chunking
- embeddings
- vector storage
- retrieval
- workspace isolation
- RAG flow
- failure handling

Tests should verify actual behavior, not just code coverage.

---

# 25. Production vs MVP

Always distinguish between:

## Current implementation

What is appropriate for the current NeuroOS stage.

and:

## Production at scale

How the system could evolve for:

- thousands of users
- millions of documents
- large ingestion workloads
- multiple workers
- multiple API instances
- object storage
- distributed queues
- dedicated vector infrastructure
- model serving infrastructure

Do not over-engineer the current system.

Instead, build clean boundaries that allow future scaling without rewriting everything.

---

# 26. Development Philosophy

The project should prioritize:

1. Correctness
2. Security
3. Maintainability
4. Observability
5. Performance
6. Scalability

Do not sacrifice architecture simply to reduce lines of code.

At the same time, do not add unnecessary complexity just because something is "enterprise."

Every infrastructure component must have a reason.

---

# 27. Teaching / Explanation Requirements

When modifying or creating code, explain the important parts.

For every important file:

- What is this file?
- Why does it exist?
- What responsibility does it own?
- How does it connect to other components?

For every important class/function:

- What does it do?
- What does it receive?
- What does it return?
- Why is it designed this way?

For important fields:

- What does the field represent?
- Why is it stored?
- What other component uses it?

Do NOT waste time explaining obvious Python syntax.

Focus explanations on:

- architecture
- data flow
- AI concepts
- backend engineering
- infrastructure
- security
- scalability
- tradeoffs

The developer should be able to review the implementation afterward and understand why it exists.

---

# 28. Autonomous Coding Rule

Do not repeatedly ask the developer basic project questions that are already answered in this document.

Before making architectural decisions:

1. Read this file.
2. Inspect the existing repository.
3. Follow existing conventions.
4. Check current dependencies and configuration.
5. Avoid duplicating existing functionality.

If something genuinely conflicts with the existing codebase, explain the conflict and choose the safest compatible solution.

Do not redesign the entire project without a strong reason.

---

# 29. Current Priority

The immediate goal is:

PHASE 4 IS COMPLETE.

Phase 4 was completed with:

- reliable document upload
- secure file handling
- document processing
- text extraction
- text cleaning
- chunking
- embeddings (Gemini, gemini-embedding-001, 768 dims)
- vector storage
- semantic retrieval
- basic grounded RAG
- appropriate tests (69 passing)
- production-quality architecture

Next: Phase 5 — Frontend.

Do NOT build the frontend during Phase 4.

The frontend will be designed and implemented separately after the backend AI MVP is complete.

Do NOT move into agents, memory, MCP, advanced tool calling, or other Phase 5+ features until Phase 4 is stable.

---

# 30. Long-Term Roadmap

Phase 1 — Authentication
STATUS: COMPLETE

Phase 2 — Workspaces
STATUS: COMPLETE

Phase 3 — Documents
STATUS: COMPLETE

Phase 4 — Ingestion + RAG Foundation
STATUS: COMPLETE

Phase 5 — Frontend
STATUS: COMPLETE

Phase 6 — Conversations + Memory
STATUS: FUTURE

Phase 7 — AI Agents
STATUS: FUTURE

Phase 8 — Tool Calling / MCP
STATUS: FUTURE

Phase 9 — Advanced AI + Integrations
STATUS: FUTURE

Phase 10 — Production Scaling / Observability / Advanced Infrastructure
STATUS: FUTURE

---

# Final Principle

NeuroOS should not be treated as a tutorial project.

It should be treated as a real AI platform being built incrementally.

The objective is not:

"Make the code work."

The objective is:

"Build a system that works correctly today, has clean architectural boundaries, can be understood by another engineer, and can evolve into a production-scale AI platform tomorrow."