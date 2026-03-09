from django.contrib import messages
from .models import Book
from django.utils import timezone


class SuccessMessageMixin:
    """Mixin to add success messages"""
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, self.get_success_message())
        return response
    
    def get_success_message(self):
        if hasattr(self, 'object') and self.object:
            return f'{self.object.__class__.__name__} {"created" if self.request.method == "POST" else "updated"} successfully!'
        return 'Operation completed successfully!'
    

class BookStatsMixin:
    """For visible books stastics"""
    def book_availbel(self):
        return Book.objects.filter(is_available=True).count()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        all_books = Book.objects.filter(is_deleted=False)
        genre= self.request.GET.get('genre', '')
        genre_books = Book.objects.filter(genre=genre)
        
        # Add statistics
        
        context['stats'] = {
            'total_books': all_books.count(),
            'available_books': all_books.filter(is_available=True).count(),
            'borrowed_books': all_books.filter(is_available = False).count(),
            'genre_books': genre_books.filter(is_deleted= False).count(),
        }
        
        return context





class SoftDeleteMixin:
    """Mixin for soft delete functionality"""
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        book_title = self.object.title
        
        # Soft delete
        self.object.is_deleted = True
        self.object.deleted_at = timezone.now()
        self.object.save()
        
        messages.success(request, f'Task "{book_title}" moved to trash.')
        return super().delete(request, *args, **kwargs)