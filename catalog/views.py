from django.shortcuts import render
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.

from .models import Book, Author, BookInstance, Genre

def index(request):

	count_books = Book.objects.all().count()
	count_instances = BookInstance.objects.all().count()
	count_avail_books = BookInstance.objects.filter(status__exact='a').count()
	count_authors = Author.objects.all().count()
	count_requests = request.session.get('num_visits',0)
	request.session['num_visits']=count_requests+1


	return render(
		request,
		'index.html',
		context={'count_books':count_books,'count_instances':count_instances, 
		'count_avail_books':count_avail_books,'count_authors':count_authors,
		'count_requests':count_requests},

	)

class BookListView(generic.ListView):
	model = Book
	#overriding the get_queryset method
	# def get_queryset(self):      
	# 	return Book.objects.filter(title__icontains='war')[::5]

#Overidding the get_context_data to pass more context variables to templates

	# def get_context_data(self, **kwargs):
 #        # Call the base implementation first to get the context
 #        context = super(BookListView, self).get_context_data(**kwargs)
 #        # Create any data and add it to the context
 #        context['some_data'] = 'This is just some data'
 #        return context


class BookDetailView(generic.DetailView):
	model = Book

	
class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    """
    Generic class-based view listing books on loan to current user. 
    """
    model = BookInstance
    template_name ='catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10
    
    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_date')