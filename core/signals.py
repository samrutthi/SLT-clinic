
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Patient
from .models import Profile
import random
import string

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=Patient)
def generate_patient_id(sender, instance, created, **kwargs):
    if created and not instance.patient_id:
        # Generate 6-digit alphanumeric ID
        instance.patient_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        instance.save()