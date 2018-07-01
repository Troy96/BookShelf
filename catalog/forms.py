from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from datetime import date
from datetime import timedelta

class RenewBookForm(forms.Form):
	renewal_date = forms.DateField(help_text="Enter a date between today and 4 weeks (default 3).")

	def clean_renewal_date(self):
		data = self.cleaned_data['renewal_date']

		#Check if date not in past
		if data < date.today():
			raise ValidationError(_('Invalid date - renewal in the past'))

		#Check date is in the given range
		if data > date.today() + timedelta(weeks=4):
			raise ValidationError(_('Invalid date - renewal more than 4 weeks not allowed'))

		#Cleaned data is returned
		return data	
