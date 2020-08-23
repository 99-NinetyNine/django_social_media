from django.contrib.auth.models import User
from .models import (
    Nature,
    Comments,
    Notification,
    Contact,
)
from users.models import Profile
from django.dispatch import receiver
from django.db.models.signals import (
    post_save,
    post_delete,
    m2m_changed,
)
from django.core.signals import request_finished
import django.dispatch
from django.utils import timezone

# custom class -boy :)
index_view_done = django.dispatch.Signal(providing_args=["request",])


@receiver(m2m_changed, sender=Nature.likes.through)
def like_alert(sender, instance, action, pk_set, **kwargs):
    if instance:
        msg = ""
        u = []  # like user
        for x in pk_set:
            u = User.objects.get(id=x)
        user = instance.user
        # nature's user
        if action == "post_add":
            if user.notes.filter(link=instance.id, is_like=True).exists():
                if instance.likes.all().count() >= 3:
                    username_list = ""
                    for notes_user in instance.likes.all()[0:2]:
                        if not notes_user == user:
                            username_list += notes_user.username + ","
                    remaining_likes = instance.likes.all().count() - 2
                    msg = (
                        username_list
                        + " and "
                        + str(remaining_likes)
                        + " others liked your post!"
                    )

                    user.notes.filter(link=instance.id, is_like=True).update(
                        content=msg
                    )

            elif not u == user:  # avoid sailesh like sailesh post.
                msg = u.username + " liked " + user.username + " post!"
                Notification.objects.create(
                    user=instance.user,
                    user_by=u,
                    content=msg,
                    link=instance.id,
                    is_like=True,
                )

        elif action == "post_remove":
            msg = u.username + " disliked " + instance.user.username + " post!"
            user.notes.filter(user_by=u, link=instance.id, is_like=True).delete()


@receiver(post_save, sender=Nature)
def tweet_alert(sender, instance, **kwargs):
    print(instance.user.username, "posted a tweet!", instance.caption)


@receiver(m2m_changed, sender=Contact)
def follow_alert(sender, instance, action, pk_set, **kwargs):
    if instance:
        msg = ""
        u = []
        for x in pk_set:
            u = User.objects.get(id=x)
        print("instance==>", instance)
        user = instance

        if action == "post_add":
            msg = u.username + " started following you"

            if not u == instance:
                Notification.objects.create(
                    user=instance, user_by=u, content=msg, is_follow=True
                )

            print(msg)
        elif action == "post_remove":
            user.notes.filter(user=instance, user_by=u, is_follow=True).delete()
            print(u.username, "unfollowed " + instance.username)


# @receiver(m2m_changed, sender=Contact)
def follow_alert_private(sender, instance, action, pk_set, **kwargs):
    if instance:
        msg = ""
        u = []
        for x in pk_set:
            u = User.objects.get(id=x)
        print("instance==>", instance)
        user = instance
        if user.profile.private is False:
            return
        if action == "pre_add":
            msg = u.username + " requested to follow " + instance.username

            if not u == instance:
                Notification.objects.create(
                    user=instance, user_by=u, content=msg, is_follow_request=True
                )

            print("Signal has done its job")


# afule garda no
# afulai reply yes
# cmnt -->post-user lai dine
# reply chai anywhere
# instance.likes.all() liked your post
# reply ko cmnt--lai update
# post-remove--if likn id xa vaney remove
@receiver(post_save, sender=Comments)
def comment_alert(sender, instance, **kwargs):
    if instance.user:
        msg = ""
        if instance.reply:
            msg = (
                instance.user.username
                + " replied to your comment "
                + instance.reply.comment
            )
        else:
            msg = (
                instance.user.username
                + " commented on "
                + instance.nature.user.username
                + " post "
                + "!"
            )

        if not instance.user == instance.nature.user:
            if not instance.nature.user.notes.filter(
                user_by=instance.user, link=instance.nature.id, is_comment=True
            ).exists():
                Notification.objects.create(
                    user=instance.nature.user,
                    user_by=instance.user,
                    content=msg,
                    link=instance.nature.id,
                    is_comment=True,
                )


@receiver(post_delete, sender=Comments)
def comment_remove(sender, instance, **kwargs):
    if instance.user:
        instance.nature.user.notes.filter(
            user_by=instance.user, link=instance.nature.id, is_comment=True
        ).delete()


@receiver(index_view_done, sender=None)
def update_last_seen(sender, request, **kwargs):  # after index page completes
    Profile.objects.filter(user__id=request.user.id).update(last_seen=timezone.now())
