from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from my_app import views  # Import your app's views
from .views import AdminLoginView, AdminDashboardView, UserDashboardView 



app_name = 'my_app'

urlpatterns = [
    # Root path - User Registration & Login
    path('', include('my_app.urls')),  # This includes all user-related paths under 'my_app.urls'

    # User Authentication (Login/Logout)
    path('registration/login/', views.CustomLoginView.as_view(), name='login'),
    path('registration/logout/', LogoutView.as_view(template_name='registration/logout.html'), name='logout'),

    # Password Reset Views
    path('registration/password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset_request'),
    path('registration/password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),

    # User Dashboard & Profile
    path('user_dashboard/', UserDashboardView.as_view(), name='user_dashboard'),
    path('userprofile/user_profile/', views.user_profile, name='user_profile'),
    path('userprofile/book-loans/', views.user_book_loan, name='user_book_loan'),
    path('userprofile/book-fines/', views.user_book_fine, name='user_book_fine'),

    # Book Management (User)
    path('books/search/', views.book_search, name='book_search'),
    path('books/add/', views.add_book, name='add_book'),
    path('books/<int:book_id>/checkout/', views.checkout_book, name='checkout_book'),
    path('books/<int:book_id>/', views.book_detail, name='book_detail'),
    
    # Admin Management
    path('admin_login/', AdminLoginView.as_view(), name='admin_login'),
    path('admin_dashboard/', AdminDashboardView.as_view(), name='admin_dashboard'),
    
    # Admin Dashboard URLs (You can also move these to a separate admin-specific URL config if needed)
    path('admin/user/loan/<int:user_id>/<int:loan_id>/', views.admin_user_loan, name='admin_user_loan'),
    path('admin/user/fine/<int:user_id>/', views.admin_user_fine, name='admin_user_fine'),

    # Admin Email Confirmation & Reminders
    path('confirm/<int:user_id>/', views.confirm_email, name='confirm_email'),
    path('send_bulk_not_returned_emails/', views.send_bulk_not_returned_emails, name='send_bulk_not_returned_emails'),
    path('send-bulk-emails/', views.send_bulk_emails, name='send_bulk_emails'),
    path('send_due_date_reminder/', views.send_due_date_reminder, name='send_due_date_reminder'),

    # Admin Book Management
    path('book-management/', views.book_management, name='book_management'),
    path('add-book/', views.add_book, name='add_book'),
    path('edit-book/<int:pk>/', views.edit_book, name='edit_book'),
    path('delete-book/<int:pk>/', views.delete_book, name='delete_book'),

    # User & Loan Management - Admin
    path('user-management/', views.user_management, name='user_management'),
    path('loan-management/<int:user_id>/', views.loan_management, name='loan_management'),
]

# Serve media files in debug mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
