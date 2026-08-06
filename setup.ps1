Write-Host "[1/5] 가상환경 생성..."
python -m venv .venv
& .\.venv\Scripts\Activate.ps1

Write-Host "[2/5] 패키지 설치..."
pip install -r requirements.txt

Write-Host "[3/5] 폴더 준비..."
New-Item -ItemType Directory -Force -Path instance | Out-Null
New-Item -ItemType Directory -Force -Path ajiteu\static\uploads | Out-Null

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host ".env 생성됨 (.env.example 복사)"
}

Write-Host "[4/5] DB 마이그레이션..."
python -m flask db upgrade

Write-Host "[5/5] 시드 데이터..."
python -c "from ajiteu import create_app; from database.seed import seed_if_empty; app=create_app(); ctx=app.app_context(); ctx.push(); print('seeded' if seed_if_empty() else 'already has users')"

Write-Host ""
Write-Host "완료! 실행: python app.py"
Write-Host "또는: flask run"
Write-Host "테스트 계정: alice / password123"
