import json
import os
import traceback

import requests
from dotenv import load_dotenv
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotAllowed, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt

from .models import (
    Book,
    BookTag,
    Recommendation,
    RecommendedBook,
    Review,
    ReviewTag,
    TagDictionary,
)

load_dotenv()

HUGGING_FACE_API_TOKEN = os.getenv("HUGGING_FACE_API_TOKEN", "")
LLM_MODEL = "HuggingFaceH4/zephyr-7b-beta"
LLM_API_URL = f"https://api-inference.huggingface.co/models/{LLM_MODEL}"


@csrf_exempt
@login_required
def recommendation_list_create(request):
    if request.method == "POST":
        try:
            payload = json.loads(request.body)
            book = Book.objects.get(pk=payload["book_id"])
            recommendation = Recommendation.objects.create(
                user=request.user,
                book=book,
                rating=payload.get("rating", 0),
            )

            for book_id in payload.get("recommended", []):
                try:
                    recommended_book = Book.objects.get(pk=book_id)
                    RecommendedBook.objects.create(
                        recommendation=recommendation,
                        book=recommended_book,
                    )
                except Book.DoesNotExist:
                    continue

            return JsonResponse(
                {
                    "id": recommendation.id,
                    "user_id": recommendation.user_id,
                    "book_id": recommendation.book_id,
                    "rating": recommendation.rating,
                    "created_at": recommendation.created_at.isoformat(),
                },
                status=201,
            )
        except (Book.DoesNotExist, KeyError, json.JSONDecodeError) as exc:
            return JsonResponse({"error": str(exc)}, status=400)

    if request.method == "GET":
        if request.GET.get("action") == "new":
            read_books = Book.objects.filter(review__user=request.user).distinct()
            return render(
                request,
                "recommendation_form.html",
                {"action": "new", "rec": None, "books": read_books},
            )

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            recommendations = (
                Recommendation.objects.filter(user=request.user)
                .select_related("book")
                .order_by("-created_at")
            )
            data = [
                {
                    "id": rec.id,
                    "user_id": rec.user_id,
                    "book_id": rec.book_id,
                    "rating": rec.rating,
                    "book": {
                        "title": rec.book.title,
                        "author": rec.book.author,
                        "cover_image": rec.book.cover_image,
                    },
                }
                for rec in recommendations
            ]
            return JsonResponse(data, safe=False)

        return render(request, "recommendation_list.html")

    return HttpResponseNotAllowed(["GET", "POST"])


@csrf_exempt
@login_required
def recommendation_detail_update_delete(request, id):
    recommendation = get_object_or_404(
        Recommendation.objects.select_related("book"),
        pk=id,
        user=request.user,
    )

    if request.method == "GET":
        return render(
            request,
            "recommendation_detail.html",
            {"rec": recommendation},
        )

    if request.method in ("PUT", "PATCH"):
        try:
            payload = json.loads(request.body)
            if "book_id" in payload:
                recommendation.book = Book.objects.get(pk=payload["book_id"])
            if "rating" in payload:
                recommendation.rating = payload["rating"]
            recommendation.save()

            return JsonResponse(
                {
                    "id": recommendation.id,
                    "book_id": recommendation.book_id,
                    "rating": recommendation.rating,
                    "updated_at": recommendation.updated_at.isoformat(),
                }
            )
        except (Book.DoesNotExist, json.JSONDecodeError) as exc:
            return JsonResponse({"error": str(exc)}, status=400)

    if request.method == "DELETE":
        recommendation.delete()
        return JsonResponse({}, status=204)

    return HttpResponseNotAllowed(["GET", "PUT", "PATCH", "DELETE"])


@login_required
def recommendation_similar(request):
    book = get_object_or_404(Book, pk=request.GET.get("book_id"))
    response = requests.get(
        "https://www.googleapis.com/books/v1/volumes",
        params={"q": book.title, "maxResults": 5},
        timeout=5,
    )
    response.raise_for_status()

    data = []
    for item in response.json().get("items", []):
        volume = item.get("volumeInfo", {})
        data.append(
            {
                "id": item.get("id"),
                "title": volume.get("title", ""),
                "cover_image": volume.get("imageLinks", {}).get("thumbnail", ""),
            }
        )
    return JsonResponse(data, safe=False)


@login_required
def recommendation_categories(request):
    query = request.GET.get("q", "").strip()
    categories = set()

    if query:
        response = requests.get(
            "https://www.googleapis.com/books/v1/volumes",
            params={"q": query, "maxResults": 20},
            timeout=5,
        )
        response.raise_for_status()
        for item in response.json().get("items", []):
            categories.update(item.get("volumeInfo", {}).get("categories", []))

    return JsonResponse(sorted(categories), safe=False)


def list_book(request):
    books = Book.objects.prefetch_related("tags").all()
    return render(request, "book_list.html", {"books": books})


@login_required
def create_book(request):
    if request.method == "POST":
        book = Book.objects.create(
            isbn=request.POST.get("isbn", ""),
            title=request.POST["title"],
            author=request.POST.get("author", ""),
            description=request.POST.get("description", ""),
            rating=request.POST.get("rating", 0),
            cover_image=request.POST.get("cover_image", ""),
            price=request.POST.get("price", ""),
            genre=request.POST.get("genre", ""),
        )
        for tag in request.POST.get("tags", "").split(","):
            if tag.strip():
                BookTag.objects.create(book=book, tag=tag.strip())
        return redirect("binder:list_book")

    return render(request, "book_form.html")


@login_required
def update_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    if request.method == "POST":
        book.isbn = request.POST.get("isbn", "")
        book.title = request.POST["title"]
        book.author = request.POST.get("author", "")
        book.description = request.POST.get("description", "")
        book.rating = request.POST.get("rating", book.rating)
        book.cover_image = request.POST.get("cover_image", "")
        book.price = request.POST.get("price", "")
        book.genre = request.POST.get("genre", "")
        book.save()

        book.tags.all().delete()
        for tag in request.POST.get("tags", "").split(","):
            if tag.strip():
                BookTag.objects.create(book=book, tag=tag.strip())

        return redirect("binder:list_book")

    return render(request, "book_form.html", {"book": book})


@login_required
def delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == "POST":
        book.delete()
        return redirect("binder:list_book")
    return render(request, "book_confirm_delete.html", {"book": book})


@login_required
def add_review(request):
    if request.method == "POST":
        book = get_object_or_404(Book, id=request.POST.get("book_id"))
        review = Review.objects.create(
            user=request.user,
            book=book,
            content=request.POST.get("content", ""),
            rating=request.POST.get("rating", 0),
        )

        for tag_name in request.POST.get("tags", "").split(","):
            tag_name = tag_name.strip()
            if tag_name:
                tag, _ = TagDictionary.objects.get_or_create(name=tag_name)
                ReviewTag.objects.create(review=review, tag=tag)

        return redirect("binder:mypage_view")

    return render(
        request,
        "review/review_form.html",
        {
            "books": Book.objects.all(),
            "tags": TagDictionary.objects.all(),
        },
    )


@login_required
def mypage_view(request):
    reviews = Review.objects.filter(user=request.user).select_related("book")
    review_tags = ReviewTag.objects.select_related("review", "tag").filter(
        review__user=request.user
    )
    return render(
        request,
        "review/mypage.html",
        {"reviews": reviews, "review_tags": review_tags},
    )


@login_required
@csrf_exempt
def gpt_chatbot(request):
    if request.method == "GET":
        return render(request, "review/chatbot.html")

    user_message = request.POST.get("message", "").strip()
    if not user_message:
        return JsonResponse({"response": "메시지를 입력해주세요."}, status=400)

    if not HUGGING_FACE_API_TOKEN:
        return JsonResponse(
            {"response": "Hugging Face API 토큰이 설정되지 않았습니다."},
            status=503,
        )

    headers = {
        "Authorization": f"Bearer {HUGGING_FACE_API_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "inputs": user_message,
        "parameters": {"max_new_tokens": 128, "temperature": 0.7},
    }

    try:
        response = requests.post(
            LLM_API_URL,
            headers=headers,
            json=payload,
            timeout=10,
        )
        response.raise_for_status()
        result = response.json()

        if isinstance(result, list) and result:
            ai_text = result[0].get("generated_text", "")
        elif isinstance(result, dict):
            ai_text = result.get("generated_text", "")
        else:
            ai_text = ""

        return JsonResponse({"response": ai_text})
    except requests.exceptions.RequestException as exc:
        traceback.print_exc()
        return JsonResponse({"response": f"챗봇 호출에 실패했습니다: {exc}"}, status=502)
    except (json.JSONDecodeError, TypeError, AttributeError):
        traceback.print_exc()
        return JsonResponse({"response": "챗봇 응답을 처리하지 못했습니다."}, status=502)
