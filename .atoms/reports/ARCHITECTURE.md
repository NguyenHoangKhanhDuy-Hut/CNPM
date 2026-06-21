# Architecture Design

## System Overview
MediPredict - Medical AI Prescription Website. Full-stack web application with React frontend and Atoms Cloud backend providing disease prediction and drug recommendation powered by AI.

## Tech Stack
- Frontend: React 18 + TypeScript + Vite + Tailwind CSS + shadcn/ui + Recharts
- Backend: FastAPI (Python) + SQLAlchemy + PostgreSQL (Atoms Cloud)
- AI: AIHubService with deepseek-v4-pro for symptom-disease matching
- Auth: Atoms Cloud built-in auth (OIDC)
- SDK: @metagptx/web-sdk for frontend-backend communication

## Module Design
| Module | Responsibility | Key Files |
|--------|---------------|-----------|
| Homepage | Landing page with hero, search, popular diseases | src/pages/Index.tsx |
| Search | Disease search with filters | src/pages/SearchPage.tsx |
| Predict | AI prediction from symptoms | src/pages/PredictPage.tsx |
| Disease Detail | Full disease info | src/pages/DiseaseDetailPage.tsx |
| Drug Detail | Full drug info | src/pages/DrugDetailPage.tsx |
| Drugs List | Browse all drugs | src/pages/DrugsPage.tsx |
| Admin | Dashboard with CRUD management | src/pages/AdminDashboard.tsx |
| Shared | Header, Footer, Cards | src/components/ |
| Backend Predict | AI prediction API | backend/routers/predict.py |

## Tech Decisions
| Decision | Choice | Rationale |
|----------|--------|-----------|
| State management | React Query + useState | Simple, efficient for CRUD apps |
| Styling | Tailwind CSS + shadcn/ui | Consistent, fast development |
| Charts | Recharts | Lightweight, React-native charts |
| AI Model | deepseek-v4-pro | Cost effective for text classification |
| Auth | Atoms Cloud built-in | No custom auth needed |

## File Tree Plan
```
app/frontend/src/
├── App.tsx (Router)
├── pages/
│   ├── Index.tsx (Homepage)
│   ├── SearchPage.tsx (Disease search)
│   ├── PredictPage.tsx (AI prediction)
│   ├── DiseaseDetailPage.tsx
│   ├── DrugDetailPage.tsx
│   ├── DrugsPage.tsx
│   └── AdminDashboard.tsx
├── components/
│   ├── Header.tsx
│   ├── Footer.tsx
│   ├── DiseaseCard.tsx
│   └── DrugCard.tsx
└── lib/
    └── client.ts
```

## Implementation Guide
1. Database setup complete with all tables and mock data
2. AI prediction endpoint at /api/v1/predict accepts symptoms and returns matched disease + drugs
3. Frontend uses @metagptx/web-sdk client for all API calls
4. Entity access: client.entities.diseases.query(), client.entities.drugs.query()
5. Custom API: client.apiCall.invoke({ url: '/api/v1/predict', method: 'POST', data: {...} })
6. Auth: client.auth.toLogin() for login, client.auth.me() for current user