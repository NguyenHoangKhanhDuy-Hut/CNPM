# Requirements & Progress

## Requirements Overview
Website dự đoán và gợi ý thuốc phù hợp theo bệnh lý - Full-stack Web App (React frontend + Atoms Cloud Backend with Database, Auth, CRUD API). Redesigned from C# MVC source to modern web technologies while keeping all functionality identical.

## User Stories
- User can browse homepage with disease overview and search
- User can search/filter diseases by name, group, risk level
- User can use AI prediction to get disease diagnosis from symptoms
- User can view disease details with symptoms, causes, diagnosis, treatment
- User can view drug details with dosage, side effects, contraindications
- User can browse all drugs with filtering
- Admin can manage drugs, diseases, mappings via admin dashboard
- User can view prediction history (authenticated)

## Task Breakdown
- [x] Create database tables (diseases, drugs, disease_drug_mappings, prediction_histories)
- [x] Insert mock data for diseases, drugs, and mappings
- [x] Create AI prediction backend endpoint
- [ ] Build frontend: Homepage (Index.tsx)
- [ ] Build frontend: SearchPage, DrugsPage
- [ ] Build frontend: PredictPage with AI integration
- [ ] Build frontend: DiseaseDetailPage, DrugDetailPage
- [ ] Build frontend: Admin Dashboard with CRUD
- [ ] Build frontend: Header, Footer, shared components
- [ ] Configure routing in App.tsx
- [ ] Lint and build check

## Progress Log
- 2026-06-20: Database tables created (diseases, drugs, disease_drug_mappings, prediction_histories)
- 2026-06-20: Mock data inserted (8 diseases, 8 drugs, 13 mappings)
- 2026-06-20: AI prediction endpoint created at /api/v1/predict