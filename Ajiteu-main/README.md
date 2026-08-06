# Ajiteu — Flask 커뮤니티 앱

세션 기반 인증과 JSON API를 사용하는 게시판/커뮤니티 웹 앱입니다.

---

## 빠른 시작

### 1) 최초 설치 (한 번만)

**Windows PowerShell**

```powershell
cd C:\Users\user\OneDrive\Desktop\Ajiteu-main
.\setup.ps1
```

또는 **CMD**

```cmd
setup.bat
```

`setup` 스크립트가 하는 일:

- Python 가상환경 `.venv` 생성
- `requirements.txt` 패키지 설치
- `.env` 파일 생성 (없을 때)
- DB 마이그레이션 (`flask db upgrade`)
- 테스트 계정·샘플 게시글 시드

### 2) 서버 실행 (매번)

```powershell
cd C:\Users\user\OneDrive\Desktop\Ajiteu-main
.\.venv\Scripts\Activate.ps1
python app.py
```

브라우저: **http://127.0.0.1:5000**

### 3) 테스트 계정

| 아이디 | 비밀번호 |
|--------|----------|
| `alice` | `password123` |
| `bob`   | `password123` |

---

## 주요 URL

| 경로 | 설명 |
|------|------|
| `/auth/login/` | 로그인 |
| `/auth/signup/` | 회원가입 |
| `/` | 메인 피드 (로그인 필요) |
| `/my-posts` | 내가 쓴 글 |

---

## 기능 요약

- 로그인 / 회원가입 (세션 인증)
- 게시글 목록 · 검색 · 카테고리 필터
- 페이지네이션 (페이지당 10개, `< 1 2 3 ... >` 형식)
- 게시글 작성 · 수정 · 삭제 (본인 글만)
- 좋아요 · 조회수 · 댓글
- 이미지 업로드 (게시글 / 댓글 / 프로필)
- 프로필 설정 (닉네임, 소개, 프로필 사진)
- 상세 모달 좌우 화살표로 이전/다음 게시글 이동
- 상세 모달 `...` 메뉴: 삭제 · 수정 · 게시물로 이동 · 취소

---

## 프로젝트 구조

```
Ajiteu-main/
├── app.py                  # Flask 진입점 (앱 생성 + API 등록)
├── config.py               # SECRET_KEY, DB, 업로드 경로
├── requirements.txt        # Python 의존성
├── setup.ps1 / setup.bat   # 최초 설치 스크립트
├── .env / .env.example     # 환경 변수
│
├── api/                    # JSON REST API (프론트 ↔ 서버)
│   ├── posts.py            # 게시글 CRUD, 좋아요, 업로드, 페이지네이션
│   ├── comments.py         # 댓글
│   ├── users.py            # 내 정보, 프로필 수정
│   ├── meta_models.py      # 조회수·카테고리 (post_meta)
│   ├── comment_meta.py     # 댓글 이미지
│   └── helpers.py          # ok(), fail(), require_login()
│
├── database/
│   ├── seed.py             # 테스트 데이터 삽입
│   └── db.py               # DB 유틸
│
├── migrations/             # Alembic DB 마이그레이션
├── instance/
│   └── ajiteu.db           # SQLite DB (실행 후 생성)
│
└── ajiteu/                 # Flask 앱 본체
    ├── __init__.py         # create_app(), Blueprint 등록
    ├── models.py           # User, Post, Comment, Reply 등
    ├── forms.py            # WTForms (로그인/회원가입)
    │
    ├── views/              # HTML 페이지 라우트
    │   ├── auth_views.py   # 로그인, 회원가입
    │   ├── main_views.py   # 메인, 내가 쓴 글
    │   └── post_api.py     # 구버전 /post 라우트 (레거시)
    │
    ├── templates/
    │   ├── main.html       # 메인 UI
    │   └── auth/           # login.html, signup.html
    │
    └── static/
        ├── css/            # main.css, components.css
        ├── js/
        │   ├── main.js         # 카드·페이지네이션 렌더링
        │   └── app-bridge.js   # API 연동 (글쓰기, 댓글, 프로필 등)
        └── uploads/        # 업로드 이미지 저장
```

---

## 아키텍처

```
브라우저 (main.html + main.js)
        ↓ fetch /api/...
app.py → api/*.py
        ↓ SQLAlchemy
ajiteu/models.py → instance/ajiteu.db (SQLite)
```

- **인증:** Flask 세션 (`session['user_id']`)
- **프론트:** `main.js`는 UI 렌더링, `app-bridge.js`는 API 호출 담당
- **모델 확장:** `ajiteu/models.py`는 최대한 유지하고, 부가 정보는 `post_meta`, `comment_meta` 테이블로 분리

---

## API 엔드포인트 (주요)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/api/posts?page=&per_page=10` | 게시글 목록 |
| GET | `/api/posts/mine` | 내 게시글 |
| GET | `/api/posts/trending` | 주간 트렌드 |
| GET | `/api/posts/{id}` | 게시글 상세 (+ 조회수) |
| POST | `/api/posts` | 게시글 작성 |
| PUT | `/api/posts/{id}` | 게시글 수정 |
| DELETE | `/api/posts/{id}` | 게시글 삭제 |
| POST | `/api/posts/{id}/like` | 좋아요 토글 |
| POST | `/api/posts/upload` | 이미지 업로드 |
| GET/POST | `/api/posts/{id}/comments` | 댓글 목록/작성 |
| GET | `/api/me` | 로그인 사용자 정보 |
| PUT | `/api/profile` | 프로필 수정 |

응답 형식 예시:

```json
{
  "ok": true,
  "data": {
    "posts": [],
    "total": 20,
    "page": 1,
    "pages": 2
  }
}
```

---

## 환경 변수 (`.env`)

```env
SECRET_KEY=change-me-in-production
DATABASE_URL=sqlite:///instance/ajiteu.db
```

SQLite 상대 경로는 Windows/OneDrive 환경에서 오류가 날 수 있어, `config.py`에서 **절대 경로로 자동 변환**합니다.

---

## 자주 쓰는 명령

```powershell
# 가상환경 활성화
.\.venv\Scripts\Activate.ps1

# 서버 실행
python app.py

# DB 마이그레이션 적용
flask db upgrade

# 새 마이그레이션 생성 (모델 변경 후)
flask db migrate -m "설명"
```

---

## 문제 해결

| 증상 | 확인 방법 |
|------|-----------|
| 로그인 안 됨 | `instance/ajiteu.db` 존재 여부, `setup.ps1` 재실행 |
| API 404 | `python app.py`로 실행 중인지 확인 (`app.py`가 `api/`를 등록함) |
| CSS/JS 변경 안 보임 | 브라우저 **Ctrl + F5** 강력 새로고침 |
| 페이지네이션 안 보임 | 게시글 11개 이상 필요 (10개/page) |
| DB 파일 오류 | `.env`의 `DATABASE_URL` 경로 확인 |

---

## 기술 스택

- **Backend:** Python 3, Flask 3, Flask-SQLAlchemy, Flask-Migrate, Flask-WTF
- **Database:** SQLite
- **Frontend:** HTML, Bootstrap 5, Vanilla JavaScript
- **Auth:** Flask Session (쿠키 기반)
