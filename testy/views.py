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
    UserEditForm,
    ProfilePictureEditForm,
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
    ImageFormset = modelformset_factory(
        NatureImage, fields=("about", "photo",), formset=BaseArticleFormSet
    )

    if request.method == "POST":
        formset = ImageFormset(request.POST or None, request.FILES)
        if formset.is_valid():
            print("my validator")
        else:
            form_errors = formset.errors
        return render(
            "testy/test.html", {"formset": formset, "form_errors": form_errors}
        )
    else:
        formset = ImageFormset(queryset=Nature.objects.none())

    context = {
        "formset": formset,
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


class NatureWeekArchiveView(LoginRequiredMixin, WeekArchiveView):
    def get_queryset(self):
        self.user = get_object_or_404(User, id=self.kwargs["user_id"])
        return Nature.objects.filter(user=self.user)

    context_object_name = "natures"
    template_name = "testy/profile_view.html"
    date_field = "pub_date"
    week_format = "%W"
    allow_future = True


class NatureMonthArchiveView(LoginRequiredMixin, MonthArchiveView):
    def get_queryset(self):
        self.user = get_object_or_404(User, id=self.kwargs["user_id"])
        return Nature.objects.filter(user=self.user)

    context_object_name = "natures"
    template_name = "testy/profile_view.html"
    date_field = "pub_date"
    allow_future = True


class NatureYearArchiveView(LoginRequiredMixin, YearArchiveView):
    def get_queryset(self):
        self.user = get_object_or_404(User, id=self.kwargs["user_id"])
        return Nature.objects.filter(user=self.user)

    context_object_name = "natures"
    template_name = "testy/profile_view.html"
    date_field = "pub_date"
    make_object_list = True
    allow_future = True


@login_required
def IndexView(request):
    print("bug me")
    users = request.user.following.all()
    if not users:
        return render(request, "testy/index.html")

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
            if ppu.pub_date >= ppu.user.profile.last_seen:
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
                    >= ppu_older.user.profile.last_seen - datetime.timedelta(days=days)
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

    from .signals import index_view_done

    index_view_done.send(sender=None, request=request)

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
    from .forms import NatureForm

    ImageFormset = modelformset_factory(
        NatureImage, fields=("about", "photo",), formset=BaseImageFormset
    )
    if request.method == "POST":
        form = NatureForm(request.POST)
        formset = ImageFormset(request.POST or None, request.FILES)
        if form.is_valid() and formset.is_valid():
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

                    natureimage.save()
                except Exception as e:
                    print("error @ formset")
                    if not natureimage:
                        no_of_error += 1

                no_of_formset += 1
            print(no_of_error)
            print(no_of_formset)
            if no_of_formset == no_of_error:
                nature.delete()
                return redirect("nature_page")

            messages.success(request, "Post has been successfully created.")
            return redirect("index_page")

    else:
        formset = ImageFormset(queryset=Nature.objects.none())
    return render(request, "testy/nature_create.html", {"formset": formset,})


def NatureEdit(request, id):
    nature = get_object_or_404(Nature, id=id)
    ImageFormset = modelformset_factory(
        NatureImage, fields=("about", "photo",), extra=4, max_num=4
    )
    if nature.user != request.user:
        raise Http404()
    if request.method == "POST":
        form = NatureEditForm(request.POST or None, instance=post)
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
                        d.image = photo.image
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
        if self.request.user == post.user:
            return True

        return False


@login_required
def NatureDetail(request, pk):
    nature = get_object_or_404(Nature, id=pk)
    nature_comments = Comments.objects.filter(nature=nature, reply=None)
    first_cmnt = None
    first_cmnt = Comments.objects.filter(nature=nature, reply=None).first()
    comments_context = []
    if first_cmnt.was_recent():
        comments_context = [
            first_cmnt,
        ]
    comments_context += nature_comments
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

            return reverse("nature_detail", args=[nature.id,])

    else:
        comment_form = CommentForm()

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
def EditProfile(request):
    if request.method == "POST":
        user_form = UserEditForm(data=request.POST or None, instance=request.user)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            return HttpResponseRedirect(
                reverse("profile_view", args=[request.user.username])
            )

    else:
        user_form = UserEditForm(instance=request.user)

    context = {
        "user_form": user_form,
    }
    messages.success(request, "Your profile picture  has been updated successfully.")
    # return render(request, "testy/profile_edit.html", context)
    # return HttpResponseRedirect(request.user.profile.get_absolute_url())


def ProfileVisibility(request):
    user = get_object_or_404(User, id=request.POST.get("id"))
    if not user == request.user:
        raise Http404()
    is_private = False
    if user.profile.private:
        is_private = False
    elif not user.profile.private:
        is_private = True

    Profile.objects.filter(user=user).update(private=is_private)
    context = {
        "is_private": is_private,
    }
    if request.is_ajax():
        html = render_to_string("testy/private_account.html", context, request=request)
        return JsonResponse({"form": html})


@login_required
def ChangeProfile(request):
    if request.method == "POST":
        pp_change = ProfilePictureEditForm(
            data=request.POST or None,
            instance=request.user.profile,
            files=request.FILES,
        )
        if pp_change.is_valid():
            f = pp_change.save(commit=False)
            f.user = request.user
            f.save()
            return HttpResponseRedirect(
                reverse("profile_view", args=[request.user.username])
            )

    else:
        pp_change = ProfilePictureEditForm(instance=request.user.profile)

    context = {
        "pp_change": pp_change,
    }

    return render(request, "testy/pp_change.html", context)


@login_required
def ProfileView(request, username):
    if not username:
        username = request.user.username

    user = User.objects.get(username=username)
    visitor = request.user
    is_following = False
    is_private = False
    if Contact.objects.filter(user_from=visitor, user_to=user).exists():
        is_following = True
    if is_following is False and user.profile.private:
        natures = None
        is_private = True
    else:
        natures = Nature.objects.filter(user=user)

    context = {
        "is_following": is_following,
        "user": user,
        "natures": natures,
        "followers": user.followers.all().count(),
        "following": user.following.all().count(),
        "is_private": is_private,
    }
    return render(request, "testy/profile_view.html", context)


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
    pk = request.POST.get("id")
    if Contact.objects.filter(user_from=visitor, user_to=user).exists():
        user.followers.remove(visitor)
        is_following = False

    else:
        user.followers.add(visitor)
        is_following = True

    context = {
        "user": user,
        "is_following": is_following,
        "followers": user.followers.all().count(),
        "following": user.following.all().count(),
    }
    just_form = request.POST.get("just_form")
    if just_form == pk:
        context = {
            "user": user,
            "is_following": is_following,
        }
    if request.is_ajax():
        if just_form == pk:
            html = render_to_string("testy/follow_form.html", context, request=request)
        else:
            html = render_to_string("testy/follow.html", context, request=request)
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
    if request.is_ajax():
        html = render_to_string("testy/base.html", context, request=request)
        return JsonResponse({"form": html})

    return render(request, "testy/search.html", context)


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
        Story, fields=("photo",), extra=4, can_delete=True
    )
    if request.method == "POST":
        formset = ImageFormset(request.POST or None, request.FILES or None)
        if formset.is_valid():
            for f in formset:
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
                    break
            messages.success(request, "Story has been successfully created.")
            return redirect("index_page")

    else:
        formset = ImageFormset(queryset=Story.objects.none())

    return render(request, "testy/story_create.html", {"formset": formset,})


def Explore(request):
    natures = Nature.objects.all()[0:10]
    """ 
    explore=[]
    for post in natures:
        if post.total_likes()>=1000:
            #explore+=post
    """

    context = {
        "explores": natures,
    }
    return render(request, "testy/explore.html", context)


@login_required
def Suggestion(request):
    sugges = []
    suggested_user = []
    user_follwings = request.user.following.all()[0 : random.randint(1, 15)]
    for user in user_follwings:
        for suspect_user in user.following.all():
            if suspect_user.followers.count() >= 5:  # or suspect_user.is_verified()
                suggested_user += suspect_user
            try:
                c = Contact.objects.get(user_from=request.user, user_to=suspect_user)
                if c.was_recent():
                    suggested_user += suspect_user

            except:
                print("not found")

    if len(suggested_user) < 100:  # always true so that more suggested_user
        total_users = User.objects.all().count()
        for i in range(1, 11):
            random_divisible = random.randint(1, 19)
            random_user_id = random.randint(
                total_users // random_divisible, total_users
            )
            suggested_user += User.objects.filter(id=random_user_id)

    # trending == rate of lines/cmnts growth ==>numpy bla bla
    users = {}
    is_following = False
    for user in suggested_user:
        sugges += Nature.objects.filter(user=user)
        if not user == request.user:  # randint may show self.
            if not user.followers.filter(id=request.user.id).exists():
                users[user] = is_following

    context = {
        "users": users,
        "suggestions": sugges,
    }

    return render(request, "testy/suggestion.html", context)


@login_required
def LiveStream(request):
    return HttpResponse("We are working on this feature!!")


@login_required
def AccountSettings(request):
    return render(request, "testy/account.html")
