from django.urls import path
from . import views

urlpatterns = [
    
    
    # Task CRUD
    path('', views.BookListView.as_view(), name='book_list'),
    path('book/borrow/',views.BookBorrowedList.as_view(), name='book_borrowed_list'),
    path('book/<int:pk>/', views.BookDetailView.as_view(), name='book_detail'),
    path('book/create/', views.BookCreateView.as_view(), name='book_create'),
    path('book/<int:pk>/update/', views.BookUpdateView.as_view(), name='book_update'),
    path('book/<int:pk>/delete/', views.BookDeleteView.as_view(), name='book_delete'),
    path('book/<int:pk>/borrowed/', views.BookBorrowedView.as_view(), name='book_borrowed'),
    path('book/<int:pk>/toggle/',views.BookToggleCompleteView.as_view()  ,name='book_borrow_toggle'),
    path('book/<int:pk>/confirmdelete/',views.BookConfirmDeleteview.as_view()  ,name='book_confirm_delete'),
    
    
    # Trash/Restore
    path('trash/', views.BookTrashView.as_view(), name='book_trash'),
    path('book/<int:pk>/restore/', views.BookRestoreView.as_view(), name='book_restore'),
]