# In your app's forms.py
from django import forms
from .models import Book

class PasswordResetForm(forms.Form):
    email = forms.EmailField(label="Enter your email address", max_length=254)

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'published_date', 'isbn', 'description', 'available_copies', 'genre', 'image']
        
    # Optional: Add custom validation or widgets if needed

    def clean_isbn(self):
        isbn = self.cleaned_data.get('isbn')
        if len(isbn) < 10:
            raise forms.ValidationError("ISBN must be at least 10 characters long.")
        return isbn