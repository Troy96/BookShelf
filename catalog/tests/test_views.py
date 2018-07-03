from django.test import TestCase

from catalog.models import Author
from django.urls import reverse

class AuthorListView(TestCase):

	@classmethod
	def setUpTestData(cls):
		#create 10 authors for tests
		num = 15
		for author in range(num):
			Author.objects.create(first_name='Tuhin %s' % author, last_name='Roy %s' % author, )

	
	def test_view_url_exists_at_desired_location(self):
		res = self.client.get('/catalog/author/')
		self.assertEqual(res.status_code, 200)

	def test_view_url_accessible_by_name(self):
		res = self.client.get(reverse('author-list'))
		self.assertEqual(res.status_code, 200)

	def test_view_uses_correct_template(self):
		res = self.client.get(reverse('author-list'))
		self.assertEqual(res.status_code, 200)
		self.assertTemplateUsed(res, 'catalog/author_list.html')
	
	def test_pagination_equal_ten(self):
		res = self.client.get(reverse('author-list'))
		self.assertEqual(res.status_code, 200)
		self.assertTrue('is_paginated', res.context)
		self.assertTrue(res.context['is_paginated'] == True)
		self.assertTrue(len(res.context['author_list']) == 10)

	def test_lists_all_authors(self):
		#second page tesring for 5 authors
		res = self.client.get(reverse('author-list')+'?page=2')
		self.assertEqual(res.status_code, 200)
		self.assertTrue('is_paginated' in res.context)
		self.assertTrue(res.context['is_paginated'] == True)
		self.assertTrue(len(res.context['author_list']) == 5)


import datetime
from django.utils import timezone
from catalog.models import BookInstance, Book, Genre, Language
from django.contrib.auth.models import User #Required to assign User as a borrower
				
class LoanedBookInstanceByUserLostViewTest(TestCase):
	def setUp(self):
		sample_user1 = User.objects.create(username='testuser1', password='1234abcd')
		sample_user1.save()
		
		sample_user2 = User.objects.create(username='testuser2', password='1234abcd')
		sample_user2.save()
		permission = Permission.objects.get(name='Set book as retuned')
		sample_user2.user_permissions.add(permission)
		sample_user2.save()


		sample_author =  Author.objects.create(first_name='Jon', last_name='Snow')
		sample_genre = Genre.objects.create(name='Fanstasy')
		sample_language = Language.objects.create(name='English')
		sample_book = Book.objects.create(title='Book', summary='Sample summary', isbn='abcdef', author=sample_author, language=sample_language)

		genre_objects_for_book = Genre.objects.all() # ManytoMany direct assignment not allowed
		sample_book.genre.set(genre_objects_for_book)
		sample_book.save()

		#20 book instance
		numBooks = 30
		for book in range(numBooks):
			return_date = timezone.now() + datetime.timedelta(days=book%5)
			if book % 2:
				the_borrower = sample_user1
			else:
				the_borrower = sample_user2	
			status ='m'
			BookInstance.objects.create(book=sample_book, imprint='Unlikely imprint, 2016', due_date=return_date, borrower=the_borrower, status=status)


	def test_redirect_if_not_logged_in(self):
		res = self.client.get(reverse('my-borrowed'))
		self.assertRedirects(res,'/accounts/login/?next=/catloge/mybooks/')

	
	def test_logged_in_uses_correct_template(self):
		login = self.client.login(username='testuser1', password='1234abcd')
		res = self.client.get(reverse('my-borrowed'))

		self.assertEqual(str(res.context['user']), 'testuser1')
		self.assertEqual(res.status_code, 200)

		self.assertTemplateUsed(res, 'catlog/bookinstance_list_borrowed_user.html')

	def test_only_borrowed_books(self):
		login = self.client.login(username='testuser1', password='1234abcd')
		res = self.client.get(reverse('my-borrowed'))

		self.assertEqual(str(res.context['user']), 'testuser1')
		self.assertEqual(res.status_code, 200)

		self.assertTrue('bookinstance_list' in res.context)
		self.assertEqual(len(res.context['bookinstance_list']), 0)

		top_ten_books = BookInstance.objects.all[:10]

		for copy in top_ten_books:
			copy.status='o'
			copy.save()
		resp = self.client.get(reverse('my-borrowed'))
		self.assertEqual(str(resp.context['user']), 'testuser1')
		self.assertEqual(resp.status_code, 200)
		self.assertTrue('bookinstance_list' in resp.context)

		for bookitem in res.context['bookinstance_list']:
			self.assertEqual(res.context['user'],bookitem.borrower)
			self.assertEqual('o', bookitem.status)


	def test_pages_ordered_by_due_date(self):
		for copy in  BookInstance.objects.all()
			copy.status='o'
			copy.save()
		login = self.client.login(username='testuser1', password='1234abcd')
		res = self.client.get(reverse('my-borrowed'))

		self.assertEqual(str(res.context['user']), 'testuser1')
		self.assertEqual(res.status_code, 200)	
		self.assertEqual(len(res.context['bookinstance_list']),10)

		last_date = 0
		for copy in res.context['bookinstance_list']:
			if last_date == 0:
				last_date=copy.due_date
			else:
				self.assertTrue(last_date <= copy.due_date)
					

	def test_redirect_if_not_logged_in(self):
		res=self.client.get(reverse('renew-book', kwargs={'pk':self.test_bookinstance1.pk,}))			
		self.assertEqual(res.status_code, 302)
		self.assertTrue(res.url.startswith('/accounts/login/'))

	def test_redirect_if_logged_in_but_not_correct_permission(self):
		login = self.client.login(usename='testuser1', password='1234abcd')
		res=self.client.get(reverse('renew-book', kwargs={'pk':self.test_bookinstance1.pk,}))			
		self.assertEqual( resp.status_code,302)
		self.assertTrue( resp.url.startswith('/accounts/login/') )

	def test_logged_in_with_permission(self):
		login = self.client.login(username='testuser2', password='1234abcd')
		res=self.client.get(reverse('renew-book', kwargs={'pk':self.test_bookinstance2.pk,}))			
		self.assertEqual( resp.status_code,200)


	def test_HTTP404_for_invalid_book_if_logged_in(self):
		import uuid
		test_uid = uuid.uuid4()
		login = self.client.login(username='testuser2', password='1234abcd')
		res = self.client.get(reverse('renew-book', kwargs={'pk':test_uid,}) )	
		self.assertEqual( res.status_code,404)

	def test_uses_correct_template(self):
		login = self.client.login(usename='testuser2', password='1234abcd')	
		res = self.client.get(reverse('renew-book', kwargs={'pk':test_uid,}) )	
		self.assertEqual( res.status_code,200)

		self.assertTemplateUsed(res, 'catalog/book_renew.html')

	def test_form_renewal_date_initially_has_date_three_weeks_in_future(self):
		login = self.client.login(usename='testuser2', password='1234abcd')	
		res = self.client.get(reverse('renew-book', kwargs={'pk':test_uid,}) )	

		self.assertEqual(res.status_code, 200)

		date_in_future = datetime.date.today() + datetime.timedelta(weeks=3)

		self.assertEqual(res.context['form'].initial['renewal_date'], date_in_future)

	def test_redirects_to_all_borrowed_list_of_books(self):
		login = self.client.login(usename='testuser2', password='1234abcd')	
		valid_date = datetime.date.today() + datetime.timedelta(weeks=2)
		res = self.client.post(reverse('renew-book', kwargs={'pk':self.test_bookinstance1.pk,}), {'renewal_date':valid_date_in_future} )
		res.assertRedirects(res,reverse('all-borrowed'))

		
