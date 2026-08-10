NeuroOS Frontend (Phase 5)

This is the initial scaffold for the NeuroOS frontend. It includes:

- Vite + React + TypeScript scaffold
- API client (`src/api/client.ts`) configured with `VITE_API_BASE`
- Design tokens and global styles (`src/styles`)
- App shell with `Topbar`, `Sidebar`, and placeholder content

Next steps:
- Implement authentication flows (login/signup)
- Add pages and routing
- Implement design system components
- Connect to backend endpoints discovered in `backend/app/api`

To run locally:

1. cd frontend
2. npm install
3. npm run dev

Set `VITE_API_BASE` to `http://localhost:8000` in an `.env` file if necessary.
