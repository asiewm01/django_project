from django.contrib import admin
from .models import Book, Loan, Fine, UserProfile

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'available_copies', 'genre')
    search_fields = ('title', 'author', 'isbn')

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('book', 'user', 'loan_date', 'due_date', 'is_returned')
    list_filter = ('is_returned', 'due_date')
    search_fields = ('book__title', 'user__username')

@admin.register(Fine)
class FineAdmin(admin.ModelAdmin):
    list_display = ('loan', 'amount', 'paid')
    list_filter = ('paid',)