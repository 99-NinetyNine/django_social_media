from django.utils import timezone
from django.db import models
import datetime
from django.contrib.auth.models import User
from django.shortcuts import reverse
from PIL import Image
from django.contrib.auth.models import AbstractBaseUser


class Nature(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="nature")
    caption = models.CharField(max_length=200, blank=True)
    pub_date = models.DateTimeField(default=timezone.now)
    location = models.CharField(max_length=19, blank=True)
    likes = models.ManyToManyField(User, related_name="likes", blank=True)
    # is_photo = models.BooleanField(default=False, blank=True)
    hide_post = models.BooleanField(default=False, blank=True)
    restrict_comment = models.BooleanField(default=False, blank=True)
    favourite = models.ManyToManyField(User, related_name="favourite", blank=True)

    class Meta:
        ordering = ["-pub_date"]

    def __str__(self):
        return f"{self.user.username} nature"

    def total_likes(self):
        return self.likes.count()

    def get_absolute_url(self):
        return reverse("nature_detail", args=[str(self.id)])

    def one_day(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)

    def is_latest(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=2)

    def was_recent(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(seconds=30)


class NatureImage(models.Model):
    nature = models.ForeignKey(Nature, on_delete=models.CASCADE, related_name="media")
    about = models.CharField(max_length=50, blank=True)
    photo = models.FileField(upload_to="images/", blank=True, null=True)
    is_photo = models.BooleanField(default=False, blank=True)

    def save(self):
        if not self.photo:
            return

        super().save()

        image = Image.open(self.photo.path)
        # change filename

        if image.height > 1200 or image.width > 1200:
            output_size = (1000, 1000)
            image.thumbnail(output_size)
            image.save(self.photo.path)
            print("image resized from model")

    def __str__(self):
        return f"{self.nature.user.username} images"


class Comments(models.Model):
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


class Contact(models.Model):
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


User.add_to_class(
    "following",
    models.ManyToManyField(
        "self", through=Contact, related_name="followers", symmetrical=False
    ),
)


class Notification(models.Model):
    user = models.ForeignKey(
        User, related_name="notes", on_delete=models.CASCADE, default=None
    )
    user_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    # this should be removed "default=none" while lauch caz no objects
    content = models.CharField(max_length=100)
    link = models.PositiveIntegerField(blank=True, default=0)
    is_like = models.BooleanField(blank=True, default=False)
    is_comment = models.BooleanField(blank=True, default=False)
    is_follow = models.BooleanField(blank=True, default=False)
    created = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return self.content


# featured posts
class Story(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="story")
    photo = models.FileField(upload_to="images/", blank=True)
    is_photo = models.BooleanField(default=False, blank=True)
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-pub_date"]

    def save(self, *args, **kwargs):
        if not self.photo:
            return
        image = Image.open(self.photo.path)
        if image.height > 600 or image.width > 600:
            output_size = (500, 500)
            image.thumbnail(output_size)
            image.save(self.photo.path)
            print("image resized from model")

        super(Nature, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} story"

    def is_story(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)

    def get_absolute_url(self):
        return reverse("story_detail", args=[str(self.id)])


""" 
class Live(models.model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="live")
    photo = models.FileField(upload_to="images/", blank=True)
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-pub_date"]

    def __str__(self):
        return f"{self.user.username} live video"
"""


class Test(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="live")
    photo = models.ImageField(upload_to="images/", blank=True)
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-pub_date"]

    def __str__(self):
        return f"{self.user.username} test photo/video"
