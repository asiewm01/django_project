from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        # Log the creation of a new user profile
        logger.debug(f"Creating profile for user {instance.username}")
        # Check if the profile already exists
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