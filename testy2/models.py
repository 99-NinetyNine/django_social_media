from django.utils import timezone
from django.db import models
import datetime
from django.contrib.auth.models import User
from django.shortcuts import reverse
from PIL import Image
from django.contrib.auth.models import AbstractBaseUser

#class Market(models.Model)



class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transaction")
    #symbol = models.CharField(max_length=200, blank=True)
    transaction_date = models.DateTimeField(default=timezone.now)
    buy_sell = models.BooleanField(default=False, blank=True)
    quantity = models.PositiveIntegerField(blank=True, default=0)
    #favourite = models.ManyToManyField(User, related_name="favourite", blank=True)

    class Meta:
        ordering = ["-transaction_date"]

    def __str__(self):
        return f"{self.user.username} transaction"

    """
    def get_absolute_url(self):
        return reverse("transaction_detail", args=[str(self.id)])
    """


class Party(models.Model):
    nature = models.ForeignKey(Nature, on_delete=models.CASCADE, related_name="media")
    about = models.CharField(max_length=50, blank=True)
    photo = models.FileField(upload_to="images/", blank=True, null=True)
    is_photo = models.BooleanField(default=False, blank=True)

    """
    def save(self, *args, **kwargs):

        super().save(*args, **kwargs)
        if not self.photo:
            return

        image = Image.open(self.photo.path)
        # change filename

        if image.height > 1200 or image.width > 1200:
            output_size = (1000, 1000)
            image.thumbnail(output_size)
            image.save(self.photo.path)
            print("image resized from model")
    """
    def __str__(self):
        return f"{self.nature.user.username} images"


class Market(models.Model):
    nature = models.ForeignKey(Nature, on_delete=models.CASCADE, default=None)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # likes = models.ManyToManyField(User, related_name="c_likes", blank=True)
    reply = models.ForeignKey(
        "self", related_name="replies", on_delete=models.CASCADE, null=True
    )
    comment = models.TextField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["timestamp"]

    def was_recent(self):
        return self.timestamp >= timezone.now() - datetime.timedelta(seconds=30)

    def __str__(self):
        return self.comment


class Bank(models.Model):
    user_from = models.ForeignKey(User, related_name="u_from", on_delete=models.CASCADE)
    user_to = models.ForeignKey(User, related_name="u_to", on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user_from", "user_to"], name="unique users"
            )
        ]

        ordering = ["-created"]

    def __str__(self):
        return "{} follows {}".format(self.user_from, self.user_to)

    def was_recent(self):
        return self.created >= timezone.now() - datetime.timedelta(days=1)

    """ 
    def clean(self):
        if self.user_to.profile.is_private:
            return
    """
