# Ajiteu (아지트)

함께 나누는 이야기, 더 가까워지는 우리.

Flask 기반 SNS형 커뮤니티 웹 애플리케이션입니다.  
게시글·댓글·프로필을 **반투명 overlay 모달**로 열어 페이지 이동 없이 가볍게 소통할 수 있습니다.

---

## 목차

- [주요 기능](#주요-기능)
- [기술 스택](#기술-스택)
- [프로젝트 구조](#프로젝트-구조)
- [시작하기](#시작하기)
- [설정 파일](#설정-파일)
- [API / 라우트](#api--라우트)
- [데이터베이스](#데이터베이스)
- [모달 UX](#모달-ux)
- [GitHub](#github)

---

## 주요 기능

| 기능 | 설명 |
|------|------|
| 회원가입 / 로그인 | 세션 기반 인증, 비밀번호 해시 저장 |
| 게시글 | 작성·수정·삭제, 다중 이미지 업로드 |
| 댓글 / 답글 | 작성·수정·삭제, overlay 내 fetch 갱신 |
| 좋아요 | 게시글·댓글·답글 추천 (M:N) |
| 프로필 | 닉네임, 소개글, 프로필 사진 |
| 검색 / 카테고리 | 키워드 검색, 여행·운동·음식 필터 |
| 모달 UX | 게시물·프로필·글쓰기를 overlay 팝업으로 표시 |
| 이미지 갤러리 | Bootstrap Carousel, 여러 장 순환 |

---

## 기술 스택

| 구분 | 사용 기술 |
|------|-----------|
| Backend | Python, Flask 3.1, Blueprint |
| ORM | Flask-SQLAlchemy, Flask-Migrate (Alembic) |
| Form | Flask-WTF, WTForms |
| Database | SQLite (로컬 개발) |
| Frontend | Jinja2, Bootstrap 5.3, Vanilla JS (fetch API) |
| Auth | Werkzeug password hash, Flask session |

---

## 프로젝트 구조

```
Ajiteu/
├── app.py                      # 로컬 실행 진입점 (python app.py)
├── config.py                   # 로컬 설정 (gitignore, 직접 생성)
├── requirements.txt            # Python 패키지 목록
├── README.md                   # 프로젝트 문서 (현재 파일)
│
├── ajiteu/                     # Flask 애플리케이션 패키지
│   ├── __init__.py             # create_app(), Blueprint 등록
│   ├── models.py               # User, Post, Comment, Reply, liker 테이블
│   ├── forms.py                # WTForms (회원가입, 게시글, 댓글, 프로필)
│   ├── filter.py               # Jinja2 datetime 필터
│   │
│   ├── views/                  # Blueprint (라우트·비즈니스 로직)
│   │   ├── main_views.py       # 메인 페이지 (/)
│   │   ├── auth_views.py       # 회원가입·로그인·로그아웃 (/auth)
│   │   ├── post_api.py         # 게시물 CRUD·좋아요·목록 (/post)
│   │   ├── comment_api.py      # 댓글 CRUD (/comment)
│   │   ├── reply_api.py        # 답글 CRUD (/reply)
│   │   └── profile.py          # 프로필 설정 (/profile)
│   │
│   ├── templates/              # Jinja2 HTML
│   │   ├── main.html           # 메인 레이아웃 + overlay JS
│   │   ├── post_detail.html    # 게시물 상세 모달
│   │   ├── post_create.html    # 글쓰기·수정 모달
│   │   ├── profile.html        # 프로필 설정 모달
│   │   ├── base.html           # 인증 페이지 공통 레이아웃
│   │   ├── form_errors.html    # 폼 오류 표시
│   │   └── auth/
│   │       ├── login.html
│   │       └── signup.html
│   │
│   └── static/
│       ├── css/
│       │   ├── main.css        # 메인 레이아웃
│       │   ├── components.css  # 카드·글쓰기 모달
│       │   ├── detail.css      # overlay·갤러리·액션시트
│       │   ├── pagination.css  # 페이지네이션
│       │   ├── auth.css        # 로그인·회원가입
│       │   └── flash.css       # 알림 메시지
│       ├── js/
│       │   ├── main.js         # (현재 미사용, main.html inline JS 사용)
│       │   └── profile.js      # 프로필 사진 미리보기
│       ├── images/             # 로고, 기본 프로필 등
│       └── photo/              # 게시글 업로드 이미지 (날짜별 폴더)
│
├── migrations/                 # Alembic DB 마이그레이션
│   ├── alembic.ini
│   ├── env.py
│   └── versions/
│
└── scripts/
    └── generate_team_ppt.py    # 팀 발표 PPT 생성 스크립트
```

### gitignore 대상 (업로드·공유하지 않음)

- `config.py` — DB URI, SECRET_KEY
- `venv/` — 가상환경
- `*.db` — SQLite 데이터베이스
- `.env`, `instance/`

---

## 시작하기

### 1. 저장소 클론

```bash
git clone https://github.com/t01040588614-source/Ajiteu.git
cd Ajiteu
```

### 2. 가상환경 및 패키지 설치

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 3. 설정 파일 생성

프로젝트 루트에 `config.py`를 만듭니다. (Git에 포함되지 않음)

```python
import os

basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'ajiteu.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = 'dev-secret-key-change-in-production'
```

### 4. 데이터베이스 마이그레이션

```bash
# Windows
set FLASK_APP=app.py
flask db upgrade

# macOS / Linux
export FLASK_APP=app.py
flask db upgrade
```

### 5. 서버 실행

```bash
python app.py
```

브라우저에서 **http://127.0.0.1:5000** 접속

---

## 설정 파일

| 파일 | 역할 | Git 포함 |
|------|------|----------|
| `config.py` | DB 연결, SECRET_KEY | ❌ |
| `requirements.txt` | 패키지 버전 고정 | ✅ |
| `migrations/` | DB 스키마 버전 관리 | ✅ |

---

## API / 라우트

### 인증 (`/auth`)

| Method | URL | 설명 |
|--------|-----|------|
| GET/POST | `/auth/signup/` | 회원가입 |
| GET/POST | `/auth/login/` | 로그인 |
| GET | `/auth/logout` | 로그아웃 |

### 게시물 (`/post`)

| Method | URL | 설명 |
|--------|-----|------|
| GET | `/post/list/<user_id>` | 게시글 목록 (메인) |
| GET/POST | `/post/create/<user_id>` | 글 작성 |
| GET | `/post/detail/<post_id>/` | 게시글 상세 |
| GET/POST | `/post/modify/<post_id>/` | 글 수정 |
| GET | `/post/delete/<post_id>/` | 글 삭제 |
| POST | `/post/like/<post_id>/` | 좋아요 (JSON) |
| GET | `/post/user/<user_id>` | 특정 사용자 글 목록 |

### 댓글 (`/comment`)

| Method | URL | 설명 |
|--------|-----|------|
| POST | `/comment/create/<post_id>/` | 댓글 작성 |
| GET/POST | `/comment/modify/<comment_id>/` | 댓글 수정 |
| GET | `/comment/delete/<comment_id>/` | 댓글 삭제 |

### 답글 (`/reply`)

| Method | URL | 설명 |
|--------|-----|------|
| POST | `/reply/create/comment/<comment_id>/` | 답글 작성 |
| GET/POST | `/reply/modify/comment/<reply_id>/` | 답글 수정 |
| GET | `/reply/delete/comment/<reply_id>/` | 답글 삭제 |

### 프로필 (`/profile`)

| Method | URL | 설명 |
|--------|-----|------|
| GET/POST | `/profile/detail/<user_id>/` | 프로필 조회·수정 |

---

## 데이터베이스

### ER 관계 (요약)

```
User ──1:N──▶ Post
User ──1:N──▶ Comment
User ──1:N──▶ Reply
Post ──1:N──▶ Comment
Comment ──1:N──▶ Reply

User ◀──M:N──▶ Post   (post_liker)
User ◀──M:N──▶ Comment (comment_liker)
User ◀──M:N──▶ Reply   (reply_liker)
```

### 주요 테이블

| 테이블 | 주요 컬럼 |
|--------|-----------|
| `user` | username, email, nickname, user_intro, image_path, password |
| `post` | content, image_path, view_count, user_id, create_date |
| `comment` | content, post_id, user_id, create_date, modify_date |
| `reply` | content, comment_id, post_id, user_id |

---

## 모달 UX

페이지 전체 이동 대신 **fetch + overlay** 패턴을 사용합니다.

| 동작 | JS 함수 | 설명 |
|------|---------|------|
| 게시물 클릭 | `openPostDetailModal(postId)` | 상세 모달 + 반투명 배경 |
| 프로필 설정 | `openProfileModal(event)` | 프로필 모달 |
| 글쓰기 | `openWriteModal(event)` | 작성·수정 모달 |
| ⋯ 메뉴 | `openAjiteuActionSheet(el)` | 삭제·수정·게시물로 이동 |
| 모달 닫기 | `closeAjiteuPageOverlay()` | X, ESC, 바깥 클릭 |
| 댓글 등록/삭제 | `reloadPostDetailInOverlay()` / `reloadCommentsInOverlay()` | overlay 유지, 영역만 갱신 |

핵심 DOM:

- `#ajiteuPageOverlay` — 반투명 배경
- `#ajiteuPageOverlaySlot` — 모달 콘텐츠 삽입 영역
- `#ajiteuActionOverlay` — ⋯ 액션 시트

---

## GitHub

| 저장소 | URL |
|--------|-----|
| 팀 저장소 | https://github.com/t01040588614-source/Ajiteu |
| 원본 저장소 | https://github.com/Ajiteu/Ajiteu |

---

## 팀 발표 PPT 생성 (선택)

```bash
pip install python-pptx
python scripts/generate_team_ppt.py
```

생성 파일: `Ajiteu_팀발표.pptx`, `Ajiteu_Team_Presentation.pptx`

---

## 라이선스

팀 프로젝트용. 별도 라이선스 명시 전까지 내부 학습·발표 목적으로 사용.
