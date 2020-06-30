from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default="default.jpg", upload_to="profile_pics")
    last_seen = models.DateTimeField(null=True, blank=True)
    private = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return f"{self.user.username} Profile"

    def get_absolute_url(self):
        return reverse("profile_view", args=[str(self.user.username)])
