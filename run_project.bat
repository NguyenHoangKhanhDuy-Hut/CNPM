@echo off
title MediPredict Full Stack

start "Backend" cmd /k "cd /d C:\Users\ASA\Desktop\Nhóm 8\App\backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000"

start "Frontend" cmd /k "cd /d C:\Users\ASA\Desktop\Nhóm 8\App\frontend && pnpm run dev"