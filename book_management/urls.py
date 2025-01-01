from django.urls import path
from .views import UserRegistrationView, UserLoginView, UserProfileView, BookListView, BookDetailView, ReadingListView, ReadingListDetailView,BookRecommendationsView,BookDescriptionView, BookQueryView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('books/', BookListView.as_view(), name='book-list'),
    path('books/<int:pk>/', BookDetailView.as_view(), name='book-detail'),
    path('reading-lists/', ReadingListView.as_view(), name='reading-list'),
    path('reading-lists/<int:pk>/', ReadingListDetailView.as_view(), name='reading-list-detail'),
    path('book-recommendation/', BookRecommendationsView.as_view(), name='book-recommendation'),
    path('book-description/', BookDescriptionView.as_view(), name='book-description'),
    path('book-query/', BookQueryView.as_view(), name='book-query')
]
