from django.urls import path, re_path
from . import views
from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls import url


urlpatterns = [
    path("", views.IndexView, name="index_page"),
    path("nature/", views.NatureCreate, name="nature_page"),  # nature=Nature
    path("account/settings/", views.AccountSettings, name="account_setting"),
    path("nature/<int:pk>/", views.NatureDetail, name="nature_detail"),
    path("nature/hide/", views.HidePost, name="nature_hide"),
    path("comment/restrict/", views.CommentRestrict, name="comment_restrict"),
    path("account/visibility/", views.ProfileVisibility, name="private_public"),
    path("post/<int:pk>/delete", views.NatureDelete.as_view(), name="nature_delete"),
    url(r"(?P<id>\d+)/nature/edit$", views.NatureEdit, name="nature_edit"),
    # for ajax
    # path("total_likes/", views.TotalLikes, name="total_likes"),
    path("nature/likes/", views.LikePost, name="like_post"),
    path("total_likes/<int:pk>/", views.TotalLikes, name="total_likes"),
    # it works for cmnt also.
    path("total_comments/<int:pk>/", views.TotalComments, name="total_comments"),
    path("nature/follow/", views.FollowUnfollow, name="follow_user"),
    path("change/photo/", views.ChangeProfile, name="change_profile"),
    path("profile/edit/", views.EditProfile, name="edit_profile"),
    re_path(r"^(?P<username>\w+)/profile$", views.ProfileView, name="profile_view"),
    re_path(r"^(?P<username>\w+)/followers$", views.FollowerList, name="followers"),
    re_path(r"^(?P<username>\w+)/following$", views.FollowerList, name="following"),
    path("search/", views.SearchUser, name="search_user"),
    path("notifications/", views.Notify, name="notify_page"),
    path("live/", views.LiveStream, name="live_page"),
    path("story/", views.StoryCreate, name="story_page"),
    path("story/<int:pk>/", views.StoryDetail, name="story_detail"),
    path("explore/", views.Explore, name="explore_page"),
    path("suggestion/", views.Suggestion, name="suggestion_page"),
    # archives
    path(
        "<int:user_id>/<int:year>/",
        views.NatureYearArchiveView.as_view(),
        name="nature_year_archive",
    ),
    path(
        "<int:user_id>/<int:year>/<int:month>/",
        views.NatureMonthArchiveView.as_view(month_format="%m"),
        name="archive_month_numeric",
    ),
    # Example: /2012/aug/
    path(
        "<int:user_id>/<int:year>/<str:month>/",
        views.NatureMonthArchiveView.as_view(),
        name="archive_month",
    ),
    path(
        "<int:user_id>/<int:year>/week/<int:week>/",
        views.NatureWeekArchiveView.as_view(),
        name="archive_week",
    ),
    path(
        "comment/<int:pk>/update", views.CommentUpdate.as_view(), name="comment_update"
    ),
    path(
        "comment/<int:pk>/delete", views.CommentDelete.as_view(), name="comment_delete"
    ),
    path("my/favourites/", views.FavouritePostList, name="fav_list"),
    path("favourites/edit/", views.FavouritePost, name="fav_edit"),
    path("test/123/", views.TestView, name="test_on"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
