from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView,
    TemplateView, View
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Q
from django.utils import timezone

from .models import Book
from .forms import BookForm
from .mixins import BookStatsMixin, SuccessMessageMixin, SoftDeleteMixin


# Book Views
class BookListView(BookStatsMixin, ListView):

    """
    This class is used for Listview of all books.

    It take a input for filter book according to book or author name.
    also it have filter options for genre, book is available or not and 
    publication year.

    It also used BooksStatsMixins for calculate book stastics and send as a context data.

    It handle aslo pagination.

    It sends a

    """
    model = Book
    template_name = 'books/book_list.html'
    context_object_name = 'books'
    paginate_by = 10
    
    def get_queryset(self):
        """
        This method queryset as a input. 

        It extracts inputs queries and filter accroding to query.
        """
        queryset = super().get_queryset()
        
        # Search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(author__icontains=search)
            )
        
        # Filter by genre
        genre = self.request.GET.get('genre')
        
        if genre:
            queryset = queryset.filter(genre=genre)
        
        # Filter by priority
        is_available = self.request.GET.get('is_available')
        
        if is_available == 'true':
            fil_value = True

        elif is_available == 'false':
            fil_value = False


        if is_available:
            queryset = queryset.filter(is_available=fil_value)

        p_year = self.request.GET.get('p_year')
        

        if p_year == 'before1950':
            queryset = queryset.filter(publication_year__lt = int(1950))

        elif p_year == 'between1950and2000':
            queryset = queryset.filter(publication_year__lt = int(2000),publication_year__gte = int(1950))

        elif p_year == 'between2000and2010':
            queryset = queryset.filter(publication_year__lt = int(2010),publication_year__gte = int(2000))

        elif p_year == 'after2010':
            queryset = queryset.filter(publication_year__gte = int(2010))

        queryset = queryset.filter(is_deleted=False)

        
        return queryset
    
    def get_context_data(self, **kwargs):

        """
        This method send a diffrent value take from inputs and for showing them
        send as a context data.
        """
        context = super().get_context_data(**kwargs)
        
        # Add filter values for form
        context['search_query'] = self.request.GET.get('search', '')
        context['filter_value'] = self.request.GET.get('genre', '')
        context['status_value'] = self.request.GET.get('is_available', '')
        context['pub_value'] = self.request.GET.get('p_year','')
        
        return context
    



class BookDetailView(DetailView):
    """
    This class is used for showing details of books using 
    Detailview.
    """
    model = Book
    template_name = 'books/book_detail.html'
    context_object_name = 'book'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add related tasks
        context['related_book'] = Book.objects.filter(
            title=self.object.title,
            is_deleted=False
        ).exclude(pk=self.object.pk)
        
        
        return context

class BookCreateView(SuccessMessageMixin, CreateView):
    """
    This class is used for create a book with createview.
    
    It add a book when form is valid and usng SuccessMessageMixins 
    It show a message as a notification.
    """

    model = Book
    form_class = BookForm
    template_name = 'books/book_form.html'
    success_url = reverse_lazy('book_list')
    
    def form_valid(self, form):
        # form.instance.created_by = self.request.user
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Create'
        return context

class BookUpdateView(SuccessMessageMixin,UpdateView):
    """
    This class is used for updatebook.
    
    It use updateview for updating book detail.
    It send a Notification when opeation successfully.
    """
    model = Book
    form_class = BookForm
    template_name = 'books/book_form.html'
    success_url = reverse_lazy('book_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Update'
        return context

class BookDeleteView(SoftDeleteMixin, DeleteView):
    """
    This class is for deleting book.

    It use softdeletemixin and deleteview. 
    It redirect user for confirmation.
    """
    model = Book
    template_name = 'books/book_confirm_delete.html'
    success_url = reverse_lazy('book_list')

# Trash/Restore Views
class BookTrashView(ListView):
    """
    This class is used for Book show in trash.
    When a user clic a trash then it shows a trash book.

    It use Listview and view for showing deleted task.
    """
    model = Book
    template_name = 'books/book_trash.html'
    context_object_name = 'books'
    
    def get_queryset(self):
        queryset = super().get_queryset()

        queryset = queryset.filter(is_deleted=True)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
    
        all_books = Book.objects.filter(is_deleted=True)
        context['deleted_books']= all_books

        return context
    
class BookRestoreView(SuccessMessageMixin, ListView):
    """
    This class is for book restore view from tash.

    It restore books which is deleted.
    """
    model = Book
    context_object_name='books'
    success_url = 'books/book_trash.html'
    
    def get(self, request, pk):
        book = get_object_or_404(Book, pk=pk) 
        
        book.is_deleted = False
        book.deleted_at = None
        
        book.save()
        
        messages.success(request, f'Book "{book.title}" restored successfully!')
        return redirect('book_trash')
    
class BookBorrowedView(SuccessMessageMixin,DetailView):
    """
    This class is for book borrowed view using detailview.
    """
    model = Book
    form_class = BookForm
    template_name = 'books/book_borrowed.html'
    success_url = reverse_lazy('book_list')

    
    def post(self, request, pk):
        
        book = get_object_or_404(Book, pk=pk)

        # Toggle available status
        
        if book.is_available:
            book.is_available = False
            messages.success(request,f"{book.title} Book is Borrowed!.")
        else:
            book.is_available = True
            messages.success(request,f"{book.title} Book is Returned Successfully!.")
    
        book.save()
        
        return redirect('book_list')
    


# class BulkActionView(View):
#     model = Book
#     suceess_url = reverse_lazy('book_list')    

#     def get(self,request):

#         selected_books = request.GET.getlist("check")
#         action = request.GET.get("action")

#         books = Book.objects.filter(id__in=selected_books)

#         if action == "borrow":
#             books.update(is_available=False)

#         elif action == "return":
#             books.update(is_available=True)

#         return redirect("book_list")


class BookBorrowedList(ListView):
    """
    This class show a book borrowed page as a List.
    """
    model= Book
    template_name = 'books/book_borrowed_list.html'
    success_url = reverse_lazy('book_borrowed_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
    
        all_books = Book.objects.filter(is_available=False)
        context['borrowed_books']= all_books

        return context

#Book Toggle Complete View
class BookToggleCompleteView(ListView,View):
    """This class is used for book borrow
    from the available book.
    """
    model = Book
    success_url = reverse_lazy("book_list")

    def post(self, request, pk):
        
        book = get_object_or_404(Book, pk=pk)

        # Toggle available status
        
        if book.is_available:
            book.is_available = False
            messages.success(request,f"{book.title} Book is Borrowed!.")
        else:
            book.is_available = True
            messages.success(request,f"{book.title} Book is Returned Successfully!.")
    
        book.save()
        
        return redirect('book_list')
    
class BookConfirmDeleteview(SuccessMessageMixin,ListView,View):
    """
    This class is used for delete the book when
    user confirm delete action.
    """
    model = Book
    success_url = reverse_lazy("book_list")

    def post(self,request,pk):

        book = get_object_or_404(Book,pk=pk)

        book.is_deleted = True
        book.deleted_at = timezone.now()

        book.save()

        return redirect('book_list')
    


# Dashboard View
# class DashboardView(BookStatsMixin,TemplateView):
#     template_name = 'tasks/dashboard.html'
    
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         # user = self.request.user
        
#         # Statistics
#         all_books = Book.objects.filter(is_deleted=False)
#         context['stats'] = {
#             'total_books': all_books.count(),
#             'borrowed_books': all_books.filter(is_available=False).count(),
#             'available_books': all_books.filter(is_available=True).count(),
#         }
        
#         # Recent tasks
#         context['recent_books'] = all_books.order_by('-created_at')[:5]
        
#         # Tasks due soon
#         # context['upcoming_tasks'] = all_tasks.filter(
#         #     due_date__lte=timezone.now().date() + timezone.timedelta(days=7),
#         #     is_completed=False
#         # ).order_by('due_date')[:5]
        
#         return context