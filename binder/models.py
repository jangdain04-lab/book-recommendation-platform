# binder/models.py

from django.db import models
from django.contrib.auth.models import User

class Book(models.Model):
    """
    도서 정보가 아직 정의되어 있지 않다면 이곳에 간단히 추가합니다.
    실제로는 별도 앱에 Book 모델이 있을 수도 있으니, 필요하면 import 경로를 조정하세요.
    """
    objects = None
    title       = models.CharField(max_length=200)
    author      = models.CharField(max_length=100, blank=True)
    published_at= models.DateField(null=True, blank=True)
    isbn = models.CharField(max_length=20, blank=True, null=True)
    description = models.TextField(blank=True)
    cover_image = models.URLField(blank=True, null=True)
    price = models.CharField(max_length=20, blank=True, null=True)
    genre = models.CharField(max_length=100, blank=True, null=True)
    rating = models.FloatField(default=0.0)

    def __str__(self):
        return self.title


class Recommendation(models.Model):
    """
    사용자→도서 추천(CRUD) 정보를 저장하는 모델
    """
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommendations')
    book       = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='recommendations')
    rating     = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} → {self.book.title} ({self.rating})"

class RecommendedBook(models.Model):
    """
    한 Recommendation에 대해 유사 추천된 Book들을 저장
    """
    recommendation = models.ForeignKey(
        Recommendation,
        on_delete=models.CASCADE,
        related_name='recommended_books'
    )
    book = models.ForeignKey(Book, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.recommendation.id} → {self.book.title}"

from django.db import models


class BookTag(models.Model):
    objects = None
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='tags')
    tag = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.book.title} - #{self.tag}"

from django.db import models
from django.contrib.auth.models import User


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    content = models.TextField()
    rating = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.book.title}"


class TagDictionary(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f"#{self.name}"

class ReviewTag(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    tag = models.ForeignKey(TagDictionary, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.review.id} - #{self.tag.name}"




