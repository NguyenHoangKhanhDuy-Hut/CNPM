# Hướng dẫn chạy toàn bộ dự án

## Yêu cầu

- Python 3.10+
- Node.js 18+ & pnpm (hoặc npm)
- SQL Server (đã cài đặt và đang chạy)
- Windows Authentication: tài khoản Windows hiện tại có quyền truy cập SQL Server

---

## 1. Khởi tạo Database

Mở **SQL Server Management Studio (SSMS)**, đăng nhập bằng Windows Authentication, chạy file:

```
App/backend/scripts/init_sqlserver.sql
```

Script sẽ tạo database `medipredict` và tất cả các bảng cần thiết.

---

## 2. Cấu hình môi trường

Tạo file `App/backend/.env`:

```ini
DATABASE_URL=mssql+pymssql://localhost:1433/medipredict

HOST=0.0.0.0
PORT=8000

JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60

OIDC_ISSUER_URL=https://your-oidc-issuer
OIDC_CLIENT_ID=your-client-id
OIDC_CLIENT_SECRET=your-client-secret
OIDC_SCOPE=openid profile email

ADMIN_USER_ID=admin
ADMIN_USER_EMAIL=admin@example.com

FRONTEND_URL=http://localhost:3000

ENVIRONMENT=dev
```

> **DATABASE_URL:**
> - Windows Auth: `mssql+pymssql://localhost:1433/medipredict`
> - Named instance: `mssql+pymssql://localhost/INSTANCE_NAME/medipredict`
> - SQL Auth: `mssql+pymssql://sa:password@localhost:1433/medipredict`

---

## 3. Chạy Backend

Mở **Terminal 1**:

```powershell
cd App/backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend chạy tại: http://localhost:8000  
Swagger UI: http://localhost:8000/docs

---

## 4. Chạy Frontend

Mở **Terminal 2**:

```powershell
cd App/frontend
pnpm install
pnpm run dev
```

Frontend sẽ chạy tại: http://localhost:3000

> Frontend tự động proxy các request `/api/*` về backend `http://localhost:8000` (xem `vite.config.ts`).

---

## 5. Kiểm tra

- Mở http://localhost:3000 trong trình duyệt
- Backend health check: http://localhost:8000/health
- DB health check: http://localhost:8000/database/health
- API docs: http://localhost:8000/docs

---

## Cấu trúc thư mục

```
App/
├── backend/
│   ├── alembic/           # Database migrations
│   ├── core/              # Config, database engine, auth utils
│   ├── dependencies/      # FastAPI dependencies
│   ├── models/            # SQLAlchemy ORM models
│   ├── routers/           # API routes
│   ├── schemas/           # Pydantic schemas
│   ├── services/          # Business logic
│   ├── mock_data/         # Seed JSON data
│   ├── scripts/           # init_sqlserver.sql
│   ├── main.py            # Backend entry point
│   └── .env               # Environment variables
└── frontend/
    ├── src/               # React source
    ├── package.json
    └── vite.config.ts
```

## Công nghệ

| Thành phần | Công nghệ |
|---|---|
| Backend | FastAPI, SQLAlchemy 2.0, pymssql |
| Database | Microsoft SQL Server |
| Frontend | React, Vite, TypeScript, shadcn/ui |
| Auth | OIDC, JWT |
| AI | OpenAI-compatible API (deepseek) |
