@echo off
chcp 65001 >nul
echo [1/5] 가상환경 생성...
python -m venv .venv
call .venv\Scripts\activate.bat

echo [2/5] 패키지 설치...
pip install -r requirements.txt

echo [3/5] 폴더 준비...
if not exist instance mkdir instance
if not exist ajiteu\static\uploads mkdir ajiteu\static\uploads

if not exist .env copy .env.example .env

echo [4/5] DB 마이그레이션...
python -m flask db upgrade

echo [5/5] 시드 데이터...
python -c "from ajiteu import create_app; from database.seed import seed_if_empty; app=create_app(); ctx=app.app_context(); ctx.push(); print('seeded' if seed_if_empty() else 'already has users')"

echo.
echo 완료! 실행: python app.py
echo 테스트 계정: alice / password123
