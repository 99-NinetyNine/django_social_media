from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ValidationError
from django import forms
from django.http import Http404
from django.views.generic.dates import (
    YearArchiveView,
    MonthArchiveView,
    WeekArchiveView,
)
from django.contrib.auth.decorators import user_passes_test

from .models import (
    Nature,
    NatureImage,
    Comments,
    Notification,
    Contact,
    Story,
)


from users.models import Profile
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    View,
    CreateView,
    UpdateView,
    DetailView,
    DeleteView,
)
from django.views.generic.list import MultipleObjectMixin
from django.utils import timezone
from django.contrib.auth.models import User
from .forms import (
    CommentForm,
    NatureEditForm,
    StoryForm,
    CommentEditForm,
)
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.forms import modelformset_factory
from django.contrib import messages
from django.db.models import Q
import datetime
import random


from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View

from .forms import TestForm
from django.forms import BaseModelFormSet

# my test


from django.core.files.images import get_image_dimensions


class BaseImageFormset(BaseModelFormSet):
    def clean(self):
        super().clean()
        """Checks that no two articles have the same title."""
        if any(self.errors):
            # Don't bother validating the formset unless each form is valid on its own
            return

        for form in self.forms:

            photo = form.cleaned_data["photo"]
            if not photo:
                raise forms.ValidationError("No image!")
            else:
                w, h = get_image_dimensions(photo)
                if w <= 100:
                    raise forms.ValidationError("Not supported.")
                if h <= 100:
                    raise forms.ValidationError("Not supported.")
                print("i came valid ")
            return photo


def TestView(request):
    users=User.objects.all()
    context = {
        "users": users,
    }
    return render(request, "testy/test.html", context)


class AjaxableResponseMixin:
    """
    Mixin to add AJAX support to a form.
    Must be used with an object-based FormView (e.g. CreateView)
    """

    def form_invalid(self, form):
        response = super().form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        # We make sure to call the parent's form_valid() method because
        # it might do some processing (in the case of CreateView, it will
        # call form.save() for example).
        response = super().form_valid(form)
        if self.request.is_ajax():
            data = {
                "pk": self.object.pk,
            }
            return JsonResponse(data)
        else:
            return response


class NatureWeekArchiveView(LoginRequiredMixin, UserPassesTestMixin, WeekArchiveView):
    def get_queryset(self):
        self.user = get_object_or_404(User, id=self.kwargs["user_id"])
        return Nature.objects.filter(user=self.user)

    context_object_name = "natures"
    template_name = "testy/profile_view.html"
    date_field = "pub_date"
    week_format = "%W"
    allow_future = True

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context["user"] = self.user
        context["is_archive"] = True
        return context

    def test_func(self):
        self.user = get_object_or_404(User, id=self.kwargs["user_id"])
        if not self.user == self.request.user:
            if self.user.profile.private:
                if not self.user.followers.filter(id=self.request.user.id).exists():
                    return False
                else:
                    return True
            else:
                return True

        elif self.user == self.request.user:
            return True


class NatureMonthArchiveView(LoginRequiredMixin, UserPassesTestMixin, MonthArchiveView):
    def get_queryset(self):
        self.user = get_object_or_404(User, id=self.kwargs["user_id"])
        return Nature.objects.filter(user=self.user)

    context_object_name = "natures"
    template_name = "testy/profile_view.html"
    date_field = "pub_date"
    allow_future = True

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context["user"] = self.user
        context["is_archive"] = True
        return context

    def test_func(self):
        self.user = get_object_or_404(User, id=self.kwargs["user_id"])
        if not self.user == self.request.user:
            if self.user.profile.private:
                if not self.user.followers.filter(id=self.request.user.id).exists():
                    return False
                else:
                    return True
            else:
                return True

        elif self.user == self.request.user:
            return True


class NatureYearArchiveView(LoginRequiredMixin, UserPassesTestMixin, YearArchiveView):
    def get_queryset(self):
        self.user = get_object_or_404(User, id=self.kwargs["user_id"])
        return Nature.objects.filter(user=self.user)

    context_object_name = "natures"
    template_name = "testy/profile_view.html"
    date_field = "pub_date"
    make_object_list = True
    allow_future = True

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context["user"] = self.user
        context["is_archive"] = True
        return context

    def test_func(self):
        self.user = get_object_or_404(User, id=self.kwargs["user_id"])
        if not self.user == self.request.user:
            if self.user.profile.private:
                if not self.user.followers.filter(id=self.request.user.id).exists():
                    return False
                else:
                    return True
            else:
                return True

        elif self.user == self.request.user:
            return True


@login_required
def IndexView(request):
    from .signals import index_view_done
    index_view_done.send(sender=None, request=request)
    users = request.user.following.all()

    if not users:
        idea="Follow People to view thier post."
        users=SuggestionAlgorithm(request)
        context={
            "idea":idea,
            "users":users,
        }
        return render(request, "testy/suggestion.html",context)

    post_per_user = []
    post_context = []
    context = []
    first_post = None
    days = 1

    first_post = Nature.objects.filter(user=request.user).first()
    # my post just after posting
    if first_post:
        if not first_post.was_recent():
            first_post = None
        elif first_post.was_recent():
            context = [
                first_post,
            ]

    for u in users:
        post_per_user = Nature.objects.filter(user=u)
        
        for ppu in post_per_user:
            if ppu.pub_date >= request.user.profile.last_seen:
                post_context.append(ppu)
        if not post_context:
            days = random.randint(1, 7)
        c = 0
        while not post_context:
            print("i came down")
            if c == 7:
                break
            for ppu_older in post_per_user:
                if (
                    ppu_older.pub_date
                    >= request.user.profile.last_seen - datetime.timedelta(days=days)
                ):
                    post_context.append(ppu_older)
                days = random.randint(1, 7)
            c += 1
    context += post_context

    # 1st post as well as other no need to check 1st post in template
    # context.append(t)

    nature_context = {}
    for n in context:
        is_liked = False
        is_fav = False
        if not n.hide_post:
            if n.likes.filter(id=request.user.id).exists():
                is_liked = True
            if n.favourite.filter(id=request.user.id).exists():
                is_fav = True
            nature_context[n] = (is_liked, is_fav)

        # if you want it
        # context[first_cmnt] = n.comments_set.first()

    cont = {
        "natures_context": nature_context,
        # "stories": story_list(request.user),
    }

    
    return render(request, "testy/index.html", cont)


@login_required
def story_list(req_user):
    user = req_user.following.all()
    mystory = Story.objects.filter(user=req_user).first()
    s = [
        mystory,
    ]
    for u in user:
        st = Story.objects.filter(user=u).first()
        if st:
            s.append(st)
    return s


    
@login_required
def NatureCreate(request):
    first_post = Nature.objects.filter(user=request.user).first()
    if(first_post):
        if((timezone.now()-datetime.timedelta(days=1))>=first_post.pub_date):
            Profile.objects.filter(user=request.user).update(has_one_post_published=False)
    from .forms import NatureForm
    #request.user.profile.has_one_post_published=True
    ImageFormset = modelformset_factory(
        NatureImage, fields=("about", "photo",),
    )
    if request.method == "POST":
        form = NatureForm(request.POST)
        formset = ImageFormset(request.POST or None, request.FILES)
        if form.is_valid() and formset.is_valid() and not request.user.profile.has_one_post_published:
            Profile.objects.filter(user=request.user).update(has_one_post_published=True)
            nature = form.save(commit=False)
            nature.user = request.user
            nature.save()
            no_of_formset = 0
            no_of_error = 0
            for f in formset:
                try:
                    natureimage = NatureImage(
                        nature=nature,
                        about=f.cleaned_data.get("about"),
                        photo=f.cleaned_data.get("photo"),
                    )
                    
                    """ 
                    if natureimage.photo.path.lower().endswith(
                        (
                            ".png",
                            ".jpg",

                            ".jpeg",
                            ".bmp",
                            ".tif",
                            ".tiff",
                            ".jpe",
                            ".jfif",
                        )
                    ):
                        natureimage.is_photo = True
                    else:
                        natureimage.is_photo = False 
                    """
                    natureimage.save()
                    
                except Exception as e:
                    print("error @ formset",e)
                    if not natureimage:
                        no_of_error += 1

                no_of_formset += 1
            
            if no_of_formset == no_of_error:
                nature.delete()
                return redirect("nature_page")

            messages.success(request, "Post has been successfully created.")
            return redirect("index_page")

    else:
        if request.user.profile.has_one_post_published:
            return render(request,"testy/nature_create_unallowed.html")
        formset = ImageFormset(queryset=NatureImage.objects.none())
    return render(request, "testy/nature_create.html", {"formset": formset,})


def NatureEdit(request, id):
    nature = get_object_or_404(Nature, id=id)
    ImageFormset = modelformset_factory(
        NatureImage, fields=("about", "photo",), extra=4, max_num=4
    )
    if nature.user != request.user:
        raise Http404()
    if request.method == "POST":
        form = NatureEditForm(request.POST or None, instance=nature)
        formset = ImageFormset(request.POST or None, request.FILES or None)
        if form.is_valid() and formset.is_valid():
            form.save()
            data = NatureImage.objects.filter(nature=nature)
            for index, f in enumerate(formset):
                if f.cleaned_data:
                    if f.cleaned_data["id"] is None:
                        photo = NatureImage(
                            nature=nature, photo=f.cleaned_data.get("photo")
                        )
                        photo.save()
                    elif f.cleaned_data["photo"] is False:
                        photo = NatureImage.objects.get(
                            id=request.POST.get("form-" + str(index) + "-id")
                        )
                        photo.delete()
                    else:
                        photo = NatureImage(
                            nature=nature, photo=f.cleaned_data.get("photo")
                        )
                        d = NatureImage.objects.get(id=data[index].id)
                        d.image = photo.photo
                        d.save()
            messages.success(request, "Post has been successfully updated!")
            return HttpResponseRedirect(nature.get_absolute_url())
    else:
        form = NatureEditForm(instance=nature)
        formset = ImageFormset(queryset=NatureImage.objects.filter(nature=nature))
    context = {
        "form": form,
        "post": nature,
        "formset": formset,
    }
    return render(request, "testy/nature_edit.html", context)


def FavouritePostList(request):
    user = request.user
    favourite_posts = user.favourite.all()
    context = {
        "favourite_posts": favourite_posts,
        "is_favourite": True,
    }
    return render(request, "testy/fav_natures.html", context)


def FavouritePost(request):
    nature = get_object_or_404(Nature, id=request.POST.get("id"))
    is_fav = False
    if not nature.user == request.user:
        if not nature.user.followers.filter(id=request.user.id).exists():
            if nature.user.profile.private or nature.hide_post:
                raise Http404()

    if nature.favourite.filter(id=request.user.id).exists():
        nature.favourite.remove(request.user)
    else:
        nature.favourite.add(request.user)
        is_fav = True
    context = {
        "nature": nature,
        "is_favourite": is_fav,
    }
    if request.is_ajax():
        html = render_to_string("testy/fav_section.html", context, request=request)
        return JsonResponse({"form": html})


class NatureDelete(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Nature
    template_name_suffix = "_delete"
    success_url = "/"

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.user


@login_required
def NatureDetail(request, pk):
    nature = get_object_or_404(Nature, id=pk)

    if not nature.user == request.user:
        if not nature.user.followers.filter(id=request.user.id).exists():
            if nature.user.profile.private or nature.hide_post:
                raise Http404("Sorry ,no posts found")

    comments_context = Comments.objects.filter(nature=nature, reply=None)
    first_cmnt = None
    # first_cmnt = Comments.objects.filter(nature=nature, reply=None).first()
    # comments_context = []
    # if first_cmnt:
    #    if first_cmnt.was_recent():
    #        comments_context = [
    #            first_cmnt,
    #        ]

    is_liked = False
    is_favourite = False
    if nature.likes.filter(id=request.user.id).exists():
        is_liked = True

    if nature.favourite.filter(id=request.user.id).exists():
        is_favourite = True

    if request.method == "POST":
        comment_form = CommentForm(request.POST or None)
        if comment_form.is_valid():
            content = request.POST.get("comment")
            reply_id = request.POST.get("comment_id")
            comment_qs = None

            if reply_id:
                comment_qs = Comments.objects.get(id=reply_id)

            comment = Comments.objects.create(
                nature=nature, user=request.user, comment=content, reply=comment_qs
            )

            # return reverse("nature_detail", args=[nature.id,])

    else:
        comment_form = CommentForm()
    if request.is_ajax():
        context = {
            "comments": Comments.objects.filter(nature=nature, reply=None),
        }
    else:
        context = {
            "nature": nature,
            "is_liked": is_liked,
            "is_favourite": is_favourite,
            "total_likes": nature.total_likes(),
            "comments": comments_context,
            "comment_form": comment_form,
        }

    if request.is_ajax():
        html = render_to_string("testy/nature_detail.html", context, request=request)
        return JsonResponse({"form": html})

    return render(request, "testy/nature_detail.html", context)


@login_required
def ProfileView(request, username):
    user=request.user
    if User.objects.filter(username=username).exists():
        user=User.objects.get(username=username)
    visitor = request.user
    is_following = False
    is_private = False
    is_follow_req_pending = False
    natures = None
    if not user == visitor:
        if user.followers.filter(id=visitor.id).exists():
            is_following = True

        if is_following is False and user.profile.private:
            if Notification.objects.filter(
                user=user, user_by=visitor, is_follow_request=True
            ).exists():
                is_follow_req_pending = True
            natures = None
            is_private = True

        elif is_following is True:
            natures = Nature.objects.filter(user=user)

    else:
        natures = Nature.objects.filter(user=user)

    context = {
        "is_following": is_following,
        "user": user,
        "natures": natures,
        "followers": user.followers.all().count(),
        "following": user.following.all().count(),
        "is_private": is_private,
        "is_follow_req_pending": is_follow_req_pending,
    }
    return render(request, "testy/profile_view.html", context)


@login_required
def StoryDetail(request, pk):
    story = get_object_or_404(Story, id=pk)
    user = story.user
    stories = user.story.filter(
        pub_date__gte=timezone.now() - datetime.timedelta(days=1)
    )

    """ 
    if request.method == "POST":
        comment_form = CommentForm(request.POST or None)
        if comment_form.is_valid():
            content = request.POST.get("comment")
            reply_id = request.POST.get("comment_id")
            comment_qs = None
            if reply_id:
                comment_qs = Comments.objects.get(id=reply_id)
            comment = Comments.objects.create(
                post=post, user=request.user, comment=content, reply=comment_qs
            )
            return HttpResponseRedirect(post.get_absolute_url())
    else:
        comment_form = CommentForm()
    """

    context = {
        "stories": stories,
        "user": user,
        # "comment_form": comment_form,
    }
    if request.is_ajax():
        html = render_to_string("testy/comments.html", context, request=request)
        return JsonResponse({"form": html})

    return render(request, "testy/story_detail.html", context)


def HidePost(request):
    nature = get_object_or_404(Nature, id=request.POST.get("id"))
    if not nature.user == request.user:
        raise Http404()
    hide_post = None
    if nature.hide_post is False:  # default ==false
        hide_post = True
    elif nature.hide_post is True:
        hide_post = False

    # update works only with filter so.
    nature_id = request.POST.get("id")
    Nature.objects.filter(id=nature_id).update(hide_post=hide_post)
    nature = get_object_or_404(Nature, id=request.POST.get("id"))
    print(nature.hide_post)
    context = {
        "nature": nature,
        "is_hidden": hide_post,
    }
    if request.is_ajax():
        html = render_to_string("testy/nature_hide.html", context, request=request)
        return JsonResponse({"form": html})


def CommentRestrict(request):
    nature = get_object_or_404(Nature, id=request.POST.get("id"))
    if not nature.user == request.user:
        raise Http404()
    is_restrict = None
    if nature.restrict_comment is False:
        is_restrict = True
    elif nature.restrict_comment is True:
        is_restrict = False

    # update works only with filter so.
    nature_id = request.POST.get("id")
    Nature.objects.filter(id=nature_id).update(restrict_comment=is_restrict)
    nature = get_object_or_404(Nature, id=request.POST.get("id"))
    context = {
        "nature": nature,
    }
    if request.is_ajax():
        html = render_to_string("testy/comment_restrict.html", context, request=request)
        return JsonResponse({"form": html})


class CommentUpdate(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Comments
    fields = ["comment"]
    template_name_suffix = "_update_form"

    def get_success_url(self, **kwargs):
        nature = self.get_object().nature
        obj = self.get_object()
        return reverse_lazy("nature_detail", args=(nature.id,))

    def test_func(self):
        return self.get_object().user == self.request.user


class CommentDelete(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comments
    fields = ["comment"]
    template_name_suffix = "_delete_form"

    def get_success_url(self, **kwargs):
        nature = self.get_object().nature
        obj = self.get_object()
        return reverse_lazy("nature_detail", args=(nature.id,))

    def test_func(self):
        return self.get_object().user == self.request.user


@login_required
def LikePost(request):
    nature = get_object_or_404(Nature, id=request.POST.get("id"))
    is_liked = False

    if not nature.user == request.user:
        if not nature.user.followers.filter(id=request.user.id).exists():
            if nature.user.profile.private or nature.hide_post:
                raise Http404("Sorry,no page found")

    if nature.likes.filter(id=request.user.id).exists():
        nature.likes.remove(request.user)
        is_liked = False
    else:
        nature.likes.add(request.user)
        is_liked = True

    context = {
        "nature": nature,
        "is_liked": is_liked,
        "total_likes": nature.total_likes(),
    }
    if request.is_ajax():
        html = render_to_string("testy/like_section.html", context, request=request)
        return JsonResponse({"form": html})


@login_required
def TotalLikes(request, pk):
    nature = get_object_or_404(Nature, id=pk)  # for ajax id=request.POST.get("id"))
    users = {}
    is_following = False
    heading = "Likes"
    for user in nature.likes.all():
        if user.followers.filter(id=request.user.id).exists():
            is_following = True

        users[user] = is_following
        is_following = False

    context = {
        "modal_heading": heading,
        "users": users,
    }
    print("ajax is bitch")
    """
    if request.is_ajax():
        html = render_to_string("testy/like_section2.html", context, request=request)
        return JsonResponse({"form": html})
    """
    return render(request, "testy/like_section2.html", context)


""" 
class UserList(View):
     """


@login_required
def TotalComments(request, pk):
    nature = get_object_or_404(Nature, id=pk)  # id=request.POST.get("id"))
    users = {}
    is_following = False
    heading = "Commented by:"
    comments = Comments.objects.filter(nature=nature)
    for comment in comments:
        if comment.user.followers.filter(id=request.user.id).exists():
            is_following = True

        users[comment.user] = is_following
        is_following = False

    context = {
        "modal_heading": heading,
        "users": users,
    }
    print("ajax is bitch")
    """
    if request.is_ajax():
        html = render_to_string("testy/like_section2.html", context, request=request)
        return JsonResponse({"form": html})
    """
    return render(request, "testy/like_section2.html", context)


@login_required
def FollowerList(request, username):
    user = User.objects.get(username=username)
    visitor = request.user
    is_following = False
    followers = {}
    following = {}
    for u in user.followers.all():
        if u.followers.filter(id=visitor.id).exists():
            is_following = True
        followers[u] = is_following
        is_following = False

    for u in user.following.all():
        if u.followers.filter(id=visitor.id).exists():
            is_following = True
        following[u] = is_following
        is_following = False

    context = {
        "followers": user.followers.count(),
        "following": user.following.count(),
        "followers_list": followers,
        "following_list": following,
    }
    return render(request, "testy/follower_list.html", context)


@login_required
def FollowUnfollow(request):
    visitor = request.user
    user = get_object_or_404(User, id=request.POST.get("id"))
    is_following = False
    is_follow_req_pending = False
    pk = request.POST.get("id")
    if Contact.objects.filter(user_from=visitor, user_to=user).exists():
        user.followers.remove(visitor)
        is_following = False

    else:
        if user.profile.private is False:
            user.followers.add(visitor)
            is_following = True
            is_follow_req_pending = False

        elif user.profile.private is True:
            note = Notification.objects.filter(
                user=user, user_by=visitor, is_follow_request=True
            )
            # note = get_object_or_404(Notification, id=request.POST.get("note"))
            if note.exists():
                for x in note:
                    user_note = x.user
                    user_by_note = x.user_by

                if visitor == user_by_note:  # for change (request to follow)  only
                    note.delete()
                    is_follow_req_pending = False
                    is_following = False
            else:
                msg = visitor.username + " requested to follow " + "you."
                Notification.objects.create(
                    user=user, user_by=visitor, content=msg, is_follow_request=True
                )
                is_follow_req_pending = True
                is_following = False

    just_form = request.POST.get("just_form")
    if just_form == pk:
        context = {
            "user": user,
            "is_following": is_following,
            "is_follow_req_pending": is_follow_req_pending,
        }
    else:
        context = {
            "user": user,
            "is_following": is_following,
            "is_follow_req_pending": is_follow_req_pending,
            "followers": user.followers.all().count(),
            "following": user.following.all().count(),
        }

    if request.is_ajax():
        if just_form == pk:
            html = render_to_string("testy/follow_form.html", context, request=request)

        else:

            html = render_to_string("testy/follow.html", context, request=request)
        return JsonResponse({"form": html})


@login_required
def AcceptFollower(request):
    user = request.user
    visitor = get_object_or_404(User, id=request.POST.get("user_id"))
    print(request.POST.get("user_id"), user, visitor)

    note = get_object_or_404(
        Notification, user=user, user_by=visitor, is_follow_request=True
    )
    if not note:
        return HttpResponse("go hell")
    else:
        user_note = note.user
        user_by_note = note.user_by
    is_following = False
    is_follow_req_pending = True
    # double check
    if Contact.objects.filter(user_from=visitor, user_to=user).exists():
        raise Http404()

    choice = request.POST.get("choice")
    print(choice)
    if "accept" in choice:
        user.followers.add(visitor)
        is_following = True
        is_follow_req_pending = False
        note.delete()

    elif choice == "decline":
        note.delete()
        is_follow_req_pending = False

    context = {
        "note": note,
        "is_follow_request_pending": is_follow_req_pending,
        "is_following": is_following,
    }

    if request.is_ajax():
        html = render_to_string("testy/accept_decline.html", context, request=request)
        return JsonResponse({"form": html})


@login_required
def SearchUser(request):
    query = request.GET.get("q")
    print(query)
    users = None
    if query:
        users = User.objects.filter(
            Q(username__icontains=query)
            | Q(username__contains=query)
            | Q(username__startswith=query)
            | Q(username__endswith=query)
            | Q(first_name__icontains=query)
            | Q(first_name__contains=query)
            | Q(first_name__startswith=query)
            | Q(first_name__endswith=query)
            | Q(last_name__icontains=query)
            | Q(last_name__contains=query)
            | Q(last_name__startswith=query)
            | Q(last_name__endswith=query)
        )
    context = {
        "users": users,
    }
    """ 
    if request.is_ajax():
        html = render_to_string("testy/base.html", context, request=request)
        return JsonResponse({"form": html})
    """
    return render(request, "testy/searched_user.html", context)


@login_required
def Notify(request):
    notes = Notification.objects.filter(user=request.user)
    context = {
        "notes": notes,
    }
    return render(request, "testy/notification.html", context)


@login_required
def StoryCreate(request):
    ImageFormset = modelformset_factory(
        Story, fields=("photo",),formset=BaseImageFormset,
    )
    if request.method == "POST":
        formset = ImageFormset(request.POST or None, request.FILES or None)
        if formset.is_valid():
            
            for f in formset:
                no_of_formset = 0
                no_of_error = 0
                try:
                    img = Story(user=request.user, photo=f.cleaned_data.get("photo"),)
                    if img.photo.path.endswith(
                        (
                            ".png",
                            ".jpg",
                            ".jpeg",
                            ".bmp",
                            ".tif",
                            ".tiff",
                            ".jpe",
                            ".jfif",
                        )
                    ):
                        img.is_photo = True
                    img.save()
                except Exception as e:
                    print("error @ formset")
                    if not natureimage:
                        no_of_error += 1
                    break
                no_of_formset += 1
            print(no_of_error)
            print(no_of_formset)
            messages.success(request, "Story has been successfully created.")
            return redirect("index_page")

    else:
        formset = ImageFormset(queryset=Story.objects.none())

    return render(request, "testy/story_create.html", {"formset": formset,})


def Explore(request):
    natures = Nature.objects.all()[0:10]
    context_nature = []
    for nature in natures:
        if not nature.user == request.user:
            if not nature.user.profile.private or nature.hide_post:
                context_nature.append(nature)

    """ 
    explore=[]
    for post in natures:
        if post.total_likes()>=1000:
            #explore+=post
    """

    context = {
        "explores": context_nature,
    }
    return render(request, "testy/explore.html", context)

def SuggestionAlgorithm(request):
    suggested_user = []
    user_follwings = request.user.following.all()
    if user_follwings:
        for user in user_follwings:
            for suspect_user in user.following.all():
                if not suspect_user.followers.filter(id=request.user.id).exists():
                    try:
                        c = Contact.objects.get(user_from=request.user, user_to=suspect_user)
                        if c.was_recent():
                            suggested_user += suspect_user
                    except:
                        pass
                    else:
                        suggested_user += suspect_user
                
    if len(suggested_user) < 3:  # always true so that more suggested_user
        total_users = User.objects.all().count()
        for i in range(1, 11):
            random_user_id = random.randint(
                1, total_users
            )
            try:
                random_user=User.objects.get(id=random_user_id)
                if not random_user == request.user and not random_user.followers.filter(id=request.user.id).exists() :
                    suggested_user += User.objects.filter(id=random_user_id)
            except:
                pass

    # trending == rate of lines/cmnts growth ==>numpy bla bla
    users = {}
    is_following = False
    for user in suggested_user:
         users[user] = is_following 
    
    print(users)
    return users


@login_required
def Suggestion(request):
    users=SuggestionAlgorithm(request)
    context={
        "users":users,
    }
    return render(request, "testy/suggestion.html", context)


@login_required
def LiveStream(request):
    msg="We are working on this feature."
    context={
        "msg":msg,
    }
    return render(request,'testy/live_stream.html',context)

