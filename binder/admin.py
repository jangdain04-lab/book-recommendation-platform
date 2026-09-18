from django.contrib import admin
from .models import Book, Recommendation

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display   = ('id', 'title', 'author', 'published_at')
    search_fields  = ('title', 'author')
    list_filter    = ('published_at',)
    ordering       = ('-published_at',)

@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display   = ('id', 'user', 'book', 'rating', 'created_at', 'updated_at')
    search_fields  = ('user__username', 'book__title')
    list_filter    = ('rating', 'created_at')
    ordering       = ('-created_at',)
