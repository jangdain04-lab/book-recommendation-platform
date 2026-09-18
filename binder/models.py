from django.contrib.auth.models import User
from django.db import models


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100, blank=True)
    published_at = models.DateField(null=True, blank=True)
    isbn = models.CharField(max_length=20, blank=True, null=True)
    description = models.TextField(blank=True)
    cover_image = models.URLField(blank=True, null=True)
    price = models.CharField(max_length=20, blank=True, null=True)
    genre = models.CharField(max_length=100, blank=True, null=True)
    rating = models.FloatField(default=0.0)

    def __str__(self):
        return self.title


class BookTag(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="tags")
    tag = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.book.title} - #{self.tag}"


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


class Recommendation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="recommendations")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="recommendations")
    rating = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} → {self.book.title} ({self.rating})"


class RecommendedBook(models.Model):
    recommendation = models.ForeignKey(
        Recommendation,
        on_delete=models.CASCADE,
        related_name="recommended_books",
    )
    book = models.ForeignKey(Book, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.recommendation.id} → {self.book.title}"
