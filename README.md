# Book Recommendation Platform

> 사용자가 읽은 책과 리뷰·태그를 바탕으로 책을 기록하고, 관련 도서를 탐색할 수 있도록 만든 **Django 기반 도서 추천·리뷰 플랫폼**입니다.

**Project** Information Systems Development Project  
**Role** PM · Service Planning · Development  
**Focus** Book CRUD · Review/Tag Data · Recommendation · External API Integration

---

## Project Overview

책을 단순히 검색하는 기능에서 끝나는 것이 아니라, 사용자가 읽은 책과 리뷰를 기록하고 그 데이터를 다시 **다음 도서 탐색**으로 연결하는 흐름을 구현했습니다.

서비스는 `도서 등록 → 리뷰/평점/태그 기록 → 개인 기록 확인 → 관련 도서 추천`의 흐름으로 구성했습니다.

## Key Features

- 도서 정보 등록·조회·수정·삭제
- 사용자별 리뷰 및 평점 저장
- 리뷰별 태그 관리
- 개인 독서 기록 마이페이지
- Google Books API 기반 관련 도서 탐색
- 추천 결과 저장 및 상세 확인
- Hugging Face API를 활용한 대화형 기능 실험

## Service Flow

```text
Book Data
   ↓
Read / Review / Rating / Tag
   ↓
User Reading History
   ↓
Recommendation & Related Book Search
```

## My Contribution

- 서비스 정보구조 및 핵심 사용자 흐름 설계
- Django 데이터 모델과 CRUD 기능 구현
- 리뷰·태그 기반 데이터 구조 설계
- 추천 결과 저장 및 조회 기능 구현
- Google Books API 연동
- 외부 LLM API 연동 실험
- 화면 템플릿 및 사용자 기능 연결

## Tech Stack

| Area | Stack |
| --- | --- |
| Backend | Django, Python |
| Frontend | Django Templates, HTML, CSS, JavaScript |
| Database | SQLite / Django ORM |
| External API | Google Books API, Hugging Face Inference API |
| Collaboration | Git, GitHub |

## Repository Structure

```text
book-recommendation-platform/
├── config/                 # Django project configuration
├── binder/                 # Book, review, tag, recommendation domain logic
├── templates/              # User-facing pages
│   └── review/
├── manage.py
├── requirements.txt
├── .env.example
└── README.md
```

> 이 저장소는 채용 포트폴리오용 공개본입니다. 로컬 DB, IDE 설정, API 토큰 및 개인 환경값은 제외했습니다.

## Security Note

외부 API 인증정보는 코드에 직접 작성하지 않고 환경변수로 관리하도록 정리했습니다.

```env
HUGGING_FACE_API_TOKEN=
DJANGO_SECRET_KEY=
```

## Getting Started

```bash
python -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate

pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## What I Learned

추천 기능 자체뿐 아니라 **사용자가 남긴 데이터를 어떤 구조로 저장하고 다음 탐색 경험으로 연결할지** 설계하는 과정이 중요했습니다. 또한 외부 API를 실제 서비스 흐름에 연결하면서 환경변수와 인증정보 관리의 필요성을 배웠습니다.
