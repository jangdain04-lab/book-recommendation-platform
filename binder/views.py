from .models import Book, Recommendation, RecommendedBook
from .models import RecommendedBook
from django.http           import HttpResponse
from django.http           import JsonResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models     import User
from .models import Recommendation, Book, BookTag, Review


def _is_ajax(request):
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'


@csrf_exempt
@login_required
def recommendation_list_create(request):
    # POST: 새로운 추천 저장
    if request.method == 'POST':
        try:
            payload = json.loads(request.body)
            book    = Book.objects.get(pk=payload['book_id'])
            rec     = Recommendation.objects.create(
                          user = request.user,
                          book = book,
                      )
            for bid in payload.get('recommended', []):
                try:
                    b = Book.objects.get(pk=bid)
                    RecommendedBook.objects.create(recommendation=rec, book=b)
                except Book.DoesNotExist:
                    continue
            data = {
                'id':         rec.id,
                'user_id':    rec.user.id,
                'book_id':    rec.book.id,
                'created_at': rec.created_at.isoformat(),
            }
            return JsonResponse(data, status=201)
        except (Book.DoesNotExist, json.JSONDecodeError) as e:
            return JsonResponse({'error': str(e)}, status=400)

    # GET: 폼 렌더링 및 리스트/JSON 제공
    if request.method == 'GET':
        action = request.GET.get('action')
        # 1) 새 추천 양식
        if action == 'new':
            read_books = Book.objects.filter(review__user=request.user).distinct()
            return render(request, 'recommendation_form.html', {
                'action': 'new',
                'rec':    None,
                'books':  read_books,
            })
        # 2) AJAX 요청: JSON으로 추천 리스트 반환
        # views.py (수정된 부분만)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            recs = Recommendation.objects.filter(user=request.user).select_related('book').order_by('-created_at')
            data = [{
                'id': r.id,
                'user_id': r.user.id,
                'rating': r.rating,
                'book': {
                    'title': r.book.title,
                    'author': r.book.author,
                    'cover_image': r.book.cover_image
                }
            } for r in recs]
            return JsonResponse(data, safe=False)

        # 3) 일반 브라우저 요청: HTML 렌더링
        return render(request, 'recommendation_list.html')

    return HttpResponseNotAllowed(['GET', 'POST'])

@csrf_exempt
def recommendation_detail_update_delete(request, id):
    rec = get_object_or_404(Recommendation, pk=id, user=request.user)

    if request.method == 'GET':
        # Render your new Bootstrap‐styled detail page
        return render(request, 'recommendation_detail.html', {'rec': rec})

    if request.method == 'DELETE':
        rec.delete()
        return JsonResponse({}, status=204)

    return HttpResponseNotAllowed(['GET', 'DELETE'])
    try:
        rec = Recommendation.objects.get(pk=id)
    except Recommendation.DoesNotExist:
        return JsonResponse({'error': 'Recommendation not found'}, status=404)

    if request.method == 'GET':
        data = {
            'id': rec.id,
            'user_id': rec.user.id,
            'book_id': rec.book.id,
            'rating': rec.rating,
            'tags': rec.tags,
            'created_at': rec.created_at.isoformat(),
            'updated_at': rec.updated_at.isoformat(),
        }
        return JsonResponse(data, status=200)

    elif request.method in ('PUT', 'PATCH'):
        try:
            payload = json.loads(request.body)
            if 'user_id' in payload:
                rec.user = User.objects.get(pk=payload['user_id'])
            if 'book_id' in payload:
                rec.book = Book.objects.get(pk=payload['book_id'])
            if 'rating' in payload:
                rec.rating = payload['rating']
            if 'tags' in payload:
                rec.tags = payload['tags']
            rec.save()

            data = {
                'id': rec.id,
                'user_id': rec.user.id,
                'book_id': rec.book.id,
                'rating': rec.rating,
                'tags': rec.tags,
                'created_at': rec.created_at.isoformat(),
                'updated_at': rec.updated_at.isoformat(),
            }
            return JsonResponse(data, status=200)

        except (User.DoesNotExist, Book.DoesNotExist, json.JSONDecodeError) as e:
            return JsonResponse({'error': str(e)}, status=400)

    elif request.method == 'DELETE':
        rec.delete()
        return HttpResponse(status=204)

    else:
        return HttpResponseNotAllowed(['GET', 'PUT', 'PATCH', 'DELETE'])


#수정됨
import os, re, json, requests
from django.contrib.auth.decorators import login_required

@login_required
@login_required
def recommendation_similar(request):

    book_id = request.GET.get('book_id')
    book    = get_object_or_404(Book, pk=book_id)

    # Google Books API 호출
    resp = requests.get(
        'https://www.googleapis.com/books/v1/volumes',
        params={'q': book.title, 'maxResults': 5},
        timeout=5
    )
    items = resp.json().get('items', [])

    data = []
    for item in items:
        vi = item.get('volumeInfo', {})
        data.append({
            'id':          item.get('id'),
            'title':       vi.get('title', ''),
            'cover_image': vi.get('imageLinks', {}).get('thumbnail', ''),
        })

    return JsonResponse(data, safe=False)




from django.shortcuts import render, get_object_or_404, redirect
from .models import Book, BookTag

def list_book(request):
    books = Book.objects.all()
    return render(request, 'book_list.html', {'books': books})

def create_book(request):
    if request.method == 'POST':
        isbn = request.POST.get('isbn', '')
        title = request.POST['title']
        author = request.POST['author']
        description = request.POST['description']
        rating = request.POST.get('rating', 0)
        cover_image = request.POST.get('cover_image', '')
        price = request.POST.get('price', '')
        genre = request.POST.get('genre', '')

        book = Book.objects.create(
            isbn=isbn,
            title=title,
            author=author,
            description=description,
            rating=rating,
            cover_image=cover_image,
            price=price,
            genre=genre
        )
        tags = request.POST.get('tags', '')
        for tag in tags.split(','):
            if tag.strip():
                BookTag.objects.create(book=book, tag=tag.strip())
        return redirect('list_book')
    return render(request, 'book_form.html')

def update_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        book.isbn = request.POST.get('isbn', '')
        book.title = request.POST['title']
        book.author = request.POST['author']
        book.description = request.POST['description']
        book.rating = request.POST.get('rating', book.rating)
        book.cover_image = request.POST.get('cover_image', '')
        book.price = request.POST.get('price', '')
        book.genre = request.POST.get('genre', '')
        book.save()

        book.tags.all().delete()
        tags = request.POST.getlist('tags')
        for tag in tags:
            if tag.strip():
                BookTag.objects.create(book=book, tag=tag.strip())
        return redirect('list_book')
    return render(request, 'book_form.html', {'book': book})

def delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    book.delete()
    return redirect('list_book')








from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Book, Review, TagDictionary, ReviewTag
from django.contrib.auth.models import User
import requests
import json

# Hugging Face API 토큰 (본인 것으로 교체)
HUGGINGFACE_API_TOKEN = os.getenv("HUGGING_FACE_API_TOKEN", "")

# 1. 리뷰 작성 폼 + 저장
def add_review(request):
    if request.method == 'POST':
        book_id = request.POST.get('book_id')
        content = request.POST.get('content')
        rating = request.POST.get('rating')
        tag_names = request.POST.get('tags', '').split(',')

        # 로그인 안 된 경우(임시) 첫 번째 사용자 사용
        user = request.user if request.user.is_authenticated else User.objects.first()
        book = Book.objects.get(id=book_id)
        review = Review.objects.create(user=user, book=book, content=content, rating=rating)

        for tag_name in tag_names:
            tag_name = tag_name.strip()
            if tag_name:
                tag_obj, _ = TagDictionary.objects.get_or_create(name=tag_name)
                ReviewTag.objects.create(review=review, tag=tag_obj)
        return redirect('mypage_view')
    else:
        books = Book.objects.all()
        tags = TagDictionary.objects.all()
        return render(request, 'review/review_form.html', {'books': books, 'tags': tags})

# 2. 마이페이지
def mypage_view(request):
    user = request.user if request.user.is_authenticated else User.objects.first()
    my_reviews = Review.objects.filter(user=user).select_related('book')
    review_tags = ReviewTag.objects.select_related('review', 'tag')
    return render(request, 'review/mypage.html', {'reviews': my_reviews, 'review_tags': review_tags})



import os
import requests
import json
import traceback
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseBadRequest
from dotenv import load_dotenv

# .env 파일에서 환경변수 로드
load_dotenv()

HUGGING_FACE_API_TOKEN = os.getenv("HUGGING_FACE_API_TOKEN", "")
LLM_MODEL = "HuggingFaceH4/zephyr-7b-beta"
API_URL = f"https://api-inference.huggingface.co/models/{LLM_MODEL}"

@login_required
@csrf_exempt
def gpt_chatbot(request):
    # GET 요청 시 챗 UI 렌더링
    if request.method == 'GET':
        return render(request, 'review/chatbot.html')

    # POST 요청: 사용자 메시지 처리
    user_msg = request.POST.get('message', '').strip()
    if not user_msg:
        return JsonResponse({'response': '메시지를 입력해주세요.'})

    # 토큰 미설정 시 오류 안내
    if not HUGGING_FACE_API_TOKEN:
        return JsonResponse({'response': '서버에 API 토큰이 설정되지 않았습니다.'})

    headers = {
        'Authorization': f'Bearer {HUGGING_FACE_API_TOKEN}',
        'Content-Type': 'application/json'
    }
    payload = {
        'inputs': user_msg,
        'parameters': {
            'max_new_tokens': 128,
            'temperature': 0.7
        }
    }

    try:
        # Hugging Face API 호출
        resp = requests.post(API_URL, headers=headers, json=payload, timeout=10)
        # 디버그 출력
        print(f"[gpt_chatbot] Status: {resp.status_code}, Response: {resp.text}")
        resp.raise_for_status()

        result = resp.json()
        # zephyr 모델의 응답 파싱
        if isinstance(result, list) and 'generated_text' in result[0]:
            ai_text = result[0]['generated_text']
        else:
            ai_text = result.get('generated_text', '') if isinstance(result, dict) else ''

    except requests.exceptions.RequestException as e:
        # 네트워크/타임아웃/인증 오류 등
        traceback.print_exc()
        return JsonResponse({'response': f'챗봇 호출에 실패했습니다: {e}'}, status=200)
    except json.JSONDecodeError:
        traceback.print_exc()
        return JsonResponse({'response': '챗봇 응답 파싱에 실패했습니다.'}, status=200)
    except Exception as e:
        # 예기치 못한 에러
        traceback.print_exc()
        return JsonResponse({'response': f'서버 오류가 발생했습니다: {e}'}, status=200)

    # 정상 응답
    return JsonResponse({'response': ai_text}, status=200)


@login_required
def recommendation_categories(request):
    """
    GET: Fetch unique categories from Google Books API for given query.
    """
    q = request.GET.get('q', '').strip()
    categories = set()
    if q:
        resp = requests.get(
            'https://www.googleapis.com/books/v1/volumes',
            params={'q': q, 'maxResults': 20},
            timeout=5
        )
        for item in resp.json().get('items', []):
            for cat in item.get('volumeInfo', {}).get('categories', []):
                categories.add(cat)
    return JsonResponse(sorted(categories), safe=False)
