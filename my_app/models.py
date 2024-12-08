from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import timedelta
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)

# Book Model
class Book(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    published_date = models.DateField()
    isbn = models.CharField(max_length=25, unique=True)
    description = models.TextField(null=True, blank=True)  # Optional field
    available_copies = models.IntegerField(default=0)
    genre = models.CharField(max_length=100, default="Unknown Genre")
    image = models.ImageField(upload_to='book_pics/', null=True, blank=True)  # Optional field

    def __str__(self):
        return self.title


class Fine(models.Model):
    loan = models.ForeignKey('Loan', on_delete=models.CASCADE, related_name='fines')  # Linking fine to loan
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    paid = models.BooleanField(default=False)  # Whether the fine has been paid or not

    def calculate_fine(self):
        """Calculate fine based on overdue days"""
        # Use the loan's return_date if available; otherwise, use the current date
        if self.loan.return_date:
            overdue_days = (self.loan.return_date - self.loan.due_date).days
        else:
            overdue_days = (timezone.now().date() - self.loan.due_date).days

        # Only calculate fine for overdue days
        if overdue_days > 0:
            self.amount = overdue_days * 1  # $1 per day
        else:
            self.amount = 0

        self.save()

    def __str__(self):
        return f"Fine for Loan {self.loan.id} - ${self.amount}"


# Loan Model (Updated)
class Loan(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    loan_date = models.DateField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    return_date = models.DateField(blank=True, null=True)
    is_returned = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.due_date:
            self.due_date = self.loan_date + timedelta(days=60)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.book.title} loaned to {self.user.username}'


# Define UserProfile model first
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_of_birth = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(max_length=254, null=True, blank=True)
    picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return f"Profile of {self.user.username}"


# Signal to create or update UserProfile
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        # Log the creation of a new user profile
        logger.debug(f"Creating profile for user {instance.username}")
        # Check if the profile already exists or create it
        UserProfile.objects.get_or_create(user=instance)
    else:
        # Check if the user has an associated profile
        if not hasattr(instance, 'profile'):
            # Log if the profile is missing and create it
            logger.debug(f"Profile missing for user {instance.username}, creating it now.")
            UserProfile.objects.get_or_create(user=instance)
        else:
            # If profile exists, save it
            logger.debug(f"Saving profile for user {instance.username}")
            instance.profile.save()