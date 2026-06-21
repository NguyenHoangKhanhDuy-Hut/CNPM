@echo off
title MediPredict Backend

cd /d "C:\Users\Asus vivobook\CNPM\App\backend"

uvicorn main:app --reload --host 0.0.0.0 --port 8000

pause