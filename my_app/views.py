from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from .models import UserProfile, Book, Loan, Fine
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy, reverse, get_resolver
from django.utils import timezone
from django import forms
from .forms import BookForm
from datetime import timedelta
from datetime import date
from django.utils import timezone
from django.utils.timezone import now
from django.http import HttpResponse
from .utils import send_bulk_emails 
import logging
from my_app.models import UserProfile
from django.views.generic import TemplateView



def home(request):
    return render(request, 'home.html')

class CustomLoginView(LoginView):
    def form_valid(self, form):
        user = form.get_user()
        # Ensure the user has a profile
        if not hasattr(user, 'profile'):
            UserProfile.objects.create(user=user)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('login_success')  # Redirect to the login success view


@login_required
def login_success(request):
    return render(request, 'registration/login_success.html')


@login_required
class UserDashboardView(TemplateView):
    template_name = 'userprofile/user_dashboard.html'
    
@login_required
def user_profile(request):
    return render(request, 'userprofile/user_profile.html')

def logout(request):
    return render(request, 'registration/logout.html')


def signup(request):
    if request.method == "POST":
        # Retrieve form data
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        image = request.FILES.get('image')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if not all([username, first_name, last_name, email, password, confirm_password]):
            messages.error(request, "Please fill in all the required fields.")
            return render(request, 'userprofile/signup.html')

        # Check if username exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists. Please choose a different username.')
            return render(request, 'userprofile/signup.html')

        # Check if passwords match
        if password != confirm_password:
            messages.error(request, 'Password and Confirm Password do not match.')
            return render(request, 'userprofile/signup.html')

        try:
            # Create user and user profile
            user = User.objects.create_user(username=username, email=email, password=password, first_name=first_name, last_name=last_name)
            profile = UserProfile.objects.create(user=user, profile_pic=image)
            user.is_active = False  # Make user inactive until email is confirmed
            user.save()
            profile.save()

            # Send confirmation email with Django's built-in send_mail
            domain = request.get_host()
            confirmation_link = f"http://{domain}/confirm/{user.id}/"

            print(f"Sending email to: {email}")  # Confirm that we're attempting to send the email

            send_mail(
                subject="Library Registration - Confirm Your Account",
                message=f"Dear {first_name},\n\nThank you for registering as a member of the Silent Library.\n\nPlease click the link below to confirm your registration:\n{confirmation_link}\n\nThank you, Silent Library Team",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email]  # Send to the dynamically captured user email
            )

            messages.success(request, 'Registration Successful. Please check your email for confirmation.')
            return redirect('signup_success')

        except Exception as e:
            messages.error(request, f'Error creating user or profile: {str(e)}')
            return render(request, 'userprofile/signup.html')

    return render(request, 'userprofile/signup.html')


def signup_success(request):
    return render(request, 'userprofile/signup_success.html')


def confirm_email(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        user.is_active = True  # Activate the user after email confirmation
        user.save()

        messages.success(request, 'Your email has been successfully confirmed! You can now log in.')
        return redirect('login')  # Redirect to the login page after confirmation
    except User.DoesNotExist:
        messages.error(request, 'Invalid confirmation link.')
        return redirect('home')


def password_reset_request(request):
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            associated_users = User.objects.filter(email=email)
            if associated_users.exists():
                for user in associated_users:
                    # Generate token and URL
                    token = default_token_generator.make_token(user)
                    uid = urlsafe_base64_encode(str(user.pk).encode())  # Fix here

                    # Build the reset link
                    reset_url = f"http://{get_current_site(request).domain}/reset/{uid}/{token}/"

                    # Send the email
                    email_subject = "Password Reset Request"
                    email_message = render_to_string('password_reset_email.html', {
                        'user': user,
                        'reset_url': reset_url,
                    })
                    send_mail(email_subject, email_message, 'from@example.com', [user.email])

                messages.success(request, "We've emailed you instructions for setting your password.")
                return redirect('password_reset_done')
            else:
                messages.error(request, "There is no user with this email address.")
    else:
        form = PasswordResetForm()

    return render(request, 'registration/password_reset_form.html', {'form': form})


def password_reset_confirm(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
        if default_token_generator.check_token(user, token):
            if request.method == "POST":
                form = SetPasswordForm(user, request.POST)
                if form.is_valid():
                    form.save()
                    messages.success(request, "Your password has been successfully reset.")
                    return redirect('login')
            else:
                form = SetPasswordForm(user)
            return render(request, 'password_reset_confirm.html', {'form': form})
        else:
            messages.error(request, "This link has expired or is invalid.")
            return redirect('password_reset_request')
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        messages.error(request, "This link has expired or is invalid.")
        return redirect('password_reset_request')


def password_reset_done(request):
    return render(request, 'registration/password_reset_done.html')


# Form for adding a new book
class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'isbn', 'published_date', 'description']


# View for adding a new book
def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()  # Save the book to the database
            return redirect('book_search')  # Redirect to the book search page
    else:
        form = BookForm()
    return render(request, 'book/add_book.html', {'form': form})


def book_search(request):
    query = request.GET.get('q', '')  # Get search query
    books = Book.objects.filter(title__icontains=query)  # Search by title
    return render(request, 'book/book_search.html', {'books': books, 'query': query})


def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    return render(request, 'book/book_detail.html', {'book': book})


def checkout_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    # Implement your checkout logic here
    return render(request, 'checkout.html', {'book': book})

logger = logging.getLogger(__name__)

class AdminLoginView(LoginView):
    template_name = 'my_app/admin/admin_login.html'
    success_url = reverse_lazy('my_app:admin_dashboard')
    
    def form_valid(self, form):
        user = form.get_user()
        # Ensure the user has a profile
        if not hasattr(user, 'profile'):
            print(f"Profile missing for {user.username}, creating one.")
            UserProfile.objects.create(user=user)
        return super().form_valid(form)

    def dispatch(self, *args, **kwargs):
        # Redirect if user is already authenticated
        if self.request.user.is_authenticated and self.request.user.is_superuser:
            return redirect(self.success_url)
        return super().dispatch(*args, **kwargs)

    def get_success_url(self):
        return self.success_url

class AdminDashboardView(TemplateView):
    template_name = 'my_app/admin/admin_dashboard.html'

# View to display all books (Read)
def book_management(request):
    books = Book.objects.all()  # Get all books from the database
    return render(request, 'admin_crud/book_management.html', {'books': books})


# View to create a new book (Create)
def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_crud/book_management')  # Redirect to book list after saving
    else:
        form = BookForm()
    return render(request, 'admin_crud/add_book.html', {'form': form})


# View to edit a book (Update)
def edit_book(request, pk):
    book = get_object_or_404(Book, pk=pk)

    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            return redirect('admin_crud/book_management')  # Redirect after save
    else:
        form = BookForm(instance=book)

    return render(request, 'admin_crud/edit_book.html', {'form': form, 'book': book})


# View to delete a book (Delete)
def delete_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.delete()
        return redirect('admin_crud/book_management')
    return render(request, 'admin_crud/delete_book.html', {'book': book})

# User Management View
def user_management(request):
    users = User.objects.all()  # Get all users
    user_data = []

    for user in users:
        # Filter loans associated with the user
        loans = Loan.objects.filter(user=user)

        # Filter fines associated with the user through loans
        fines = Fine.objects.filter(loan__user=user)

        user_data.append({
            'user': user,
            'loans': loans,
            'fines': fines
        })
        
    return render(request, 'admin_crud/user_management.html', {'user_data': user_data})

# Loan Management View
def loan_management(request, user_id):
    user = get_object_or_404(User, id=user_id)
    loans = Loan.objects.filter(user=user)
    
    if request.method == 'POST':
        loan_id = request.POST.get('loan_id')
        action = request.POST.get('action')
        
        loan = get_object_or_404(Loan, id=loan_id)
        
        if action == 'extend':
            loan.due_date += timedelta(days=7)  # Extend by 7 days
            loan.save()
            messages.success(request, 'Loan extended by 7 days.')
        elif action == 'return':
            loan.status = 'Returned'
            loan.save()
            messages.success(request, 'Book returned successfully.')
        
        # Redirect or re-render page to reflect changes
        return redirect('admin_crud/loan_management', user_id=user.id)

    return render(request, 'admin_crud/loan_management.html', {'user': user, 'loans': loans})


# Bulk Email Sending View for Overdue Fines
def send_bulk_emails():
    unpaid_loans = Loan.objects.filter(is_returned=False, fine__paid=False)
    
    for loan in unpaid_loans:
        user = loan.user
        subject = 'Reminder: Your Loan is Overdue'
        message = f'Hello {user.first_name},\n\nYou have an overdue loan for the book "{loan.book.title}". Please return it as soon as possible to avoid further fines.'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [user.email]
        
        send_mail(subject, message, from_email, recipient_list)

def send_bulk_email_view(request):
    send_bulk_emails()
    return HttpResponse("Bulk emails sent successfully!")

def send_bulk_emails_not_returned():
    loans_not_returned = Loan.objects.filter(return_date__isnull=True)
    
    for loan in loans_not_returned:
        user = loan.user
        subject = 'Reminder: Return Your Loaned Book'
        message = f'Hello {user.first_name},\n\nYou have a book "{loan.book.title}" that you have not yet returned. Please return it to avoid any penalties.'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [user.email]
        
        send_mail(subject, message, from_email, recipient_list)

def send_due_date_reminder(request):
    if request.method == 'POST':
        loans_due_soon = Loan.objects.filter(due_date__lte=now().date() + timedelta(days=14), return_date__isnull=True)
        
        for loan in loans_due_soon:
            send_mail(
                "Reminder: Upcoming Due Date",
                "This is a reminder that your book is due soon. Please return it before the due date.",
                'library@example.com',  # Your email address
                [loan.user.email],
                fail_silently=False,
            )

        return HttpResponse("Due date reminder emails sent!")
    return HttpResponse("Invalid request method.", status=405)

def send_bulk_not_returned_emails(request):
    if request.method == 'POST':
        overdue_loans = Loan.objects.filter(return_date__isnull=True)

        for loan in overdue_loans:
            send_mail(
                "Reminder: Books Not Returned",
                "This is a reminder that the following books have not been returned on time.",
                'library@example.com',  # Your email address
                [loan.user.email],
                fail_silently=False,
            )

        return HttpResponse("Bulk emails sent to users with not returned loans!")
    return HttpResponse("Invalid request method.", status=405)

# Fine Calculation View
def calculate_fines(request):
    fines = Fine.objects.filter(paid=False)  # Get all unpaid fines
    
    for fine in fines:
        overdue_days = (timezone.now().date() - fine.due_date).days
        if overdue_days > 0:
            fine.amount = overdue_days * 0.50  # $0.50 per overdue day
            fine.save()  # Save the updated fine amount
    
    messages.success(request, 'Fines updated successfully based on overdue days.')
    return render(request, 'admin_crud/fine_management.html')

from django.http import Http404

def admin_user_loan(request, user_id, loan_id):
    try:
        user = User.objects.get(id=user_id)
        loan = Loan.objects.get(id=loan_id, user=user)
    except User.DoesNotExist:
        raise Http404("User not found")
    except Loan.DoesNotExist:
        raise Http404("Loan not found")

    today = now().date()

    # Determine loan status
    status = None
    if loan.is_returned:
        if loan.return_date <= loan.due_date:
            status = "Returned before due"
        else:
            fine = Fine.objects.filter(loan=loan, paid=False).first()
            status = "Overdue - Fine Unpaid" if fine else "Returned late but fine paid"
    else:
        status = "Overdue" if loan.due_date < today else "On Loan"

    return render(request, 'admin_crud/admin_user_loan.html', {'loan': loan, 'status': status})

def admin_user_fine(request, user_id):
    user = get_object_or_404(User, id=user_id)
    fines = Fine.objects.filter(user=user)
    today = date.today()  # Current date for overdue calculation

    return render(request, 'admin_crud/admin_user_fine.html', {'user': user, 'fines': fines, 'today': today})

def user_book_loan(request):
    # Get today's date
    today_date = timezone.now().date()  # Or date.today() if timezone is not necessary
    loans = Loan.objects.filter(user=request.user)
    return render(request, 'userprofile/user_book_loan.html', {'loans': loans, 'today_date': today_date})

def user_book_fine(request):
    # Fetch the fines (assuming you have a model for fines or you calculate it based on overdue loans)
    loans = Loan.objects.filter(user=request.user)
    fines = []
    
    for loan in loans:
        # Calculate fine (assuming $1 per day for overdue books)
        fine_amount = 0
        if loan.due_date < timezone.now().date() and not loan.return_date:
            fine_amount = (timezone.now().date() - loan.due_date).days  # Fine is $1 per day
        fines.append({'loan': loan, 'fine': fine_amount})

    can_loan_more = all(fine['fine'] == 0 for fine in fines)  # If there are no fines, user can loan more books

    return render(request, 'userprofile/user_book_fine.html', {'fines': fines, 'can_loan_more': can_loan_more})

def some_view(request, user_id, loan_id):
    user = request.user
    profile = user.profile  
    url = reverse('admin_user_loan', args=[user_id, loan_id])
    return redirect(url)