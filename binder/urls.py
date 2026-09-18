from django.urls import path

from . import views

app_name = "binder"

urlpatterns = [
    path("", views.list_book, name="home"),
    path("books/", views.list_book, name="list_book"),
    path("books/new/", views.create_book, name="create_book"),
    path("books/<int:book_id>/edit/", views.update_book, name="update_book"),
    path("books/<int:book_id>/delete/", views.delete_book, name="delete_book"),
    path("recommendations/", views.recommendation_list_create, name="recommendation-list-create"),
    path("recommendations/similar/", views.recommendation_similar, name="recommendation-similar"),
    path("recommendations/categories/", views.recommendation_categories, name="recommendation-categories"),
    path(
        "recommendations/<int:id>/",
        views.recommendation_detail_update_delete,
        name="recommendation-detail-update-delete",
    ),
    path("reviews/new/", views.add_review, name="add_review"),
    path("mypage/", views.mypage_view, name="mypage_view"),
    path("chatbot/", views.gpt_chatbot, name="gpt_chatbot"),
]
