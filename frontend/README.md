NeuroOS Frontend (Phase 5)

This is the initial scaffold for the NeuroOS frontend. It includes:

- Vite + React + TypeScript scaffold
- API client (`src/api/client.ts`) configured with `VITE_API_BASE`
- Design tokens and global styles (`src/styles`)
- App shell with `Topbar`, `Sidebar`, and placeholder content

This scaffold includes working authentication, routing, workspace & document pages, upload progress and polling, and an AI Chat page wired to the backend RAG endpoint.

Run locally:

1. cd frontend
2. npm install
3. npm run dev

Ensure the backend API is running (default expected at `http://localhost:8000`) and `frontend/.env` `VITE_API_BASE` is set accordingly.

What's included:
- Auth: login/signup via `/users` and `/users/login` (JWT stored in `localStorage`).
- Workspaces: list and detail pages (`/workspaces`, `/workspaces/:id`) with document upload and processing polling.
- Documents: documents list per workspace.
- AI Chat: `/chat` posts to `/workspaces/{id}/query` and renders grounded answers + sources.
- Design tokens and primitives: buttons, inputs, cards, pills, status badges.
- Motion: subtle page and card animations using Framer Motion.

Notes:
- I did not modify backend code — frontend consumes the existing FastAPI routes.
- This is a feature-complete frontend foundation for Phase 5; further polish (typography, spacing, animations) can be iterated.
