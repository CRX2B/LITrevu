"""
URL configuration for litrevu project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordChangeView,
    PasswordChangeDoneView,
)
from django.conf import settings
from django.urls import path
from django.conf.urls.static import static
import review.views
import authentication.views

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "",
        LoginView.as_view(
            template_name="authentication/login.html",
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    path("update-user/", authentication.views.update_user, name="update_user"),
    path(
        "logout/",
        LogoutView.as_view(
            template_name="authentication/login.html", next_page="login"
        ),
        name="logout",
    ),
    path("home/", review.views.home, name="home"),
    path("signup/", authentication.views.signup, name="signup"),
    path(
        "password-change/",
        PasswordChangeView.as_view(
            template_name="authentication/passwordchange.html",
            success_url="/password-change/done/",
        ),
        name="passwordchange",
    ),
    path(
        "password-change/done/",
        PasswordChangeDoneView.as_view(
            template_name="authentication/passwordchangedone.html",
        ),
        name="passwordchangedone",
    ),
    path(
        "ticket/create/", review.views.TicketCreateView.as_view(), name="create_ticket"
    ),
    path(
        "ticket/detail/<int:pk>/",
        review.views.TicketDetailView.as_view(),
        name="detail_ticket",
    ),
    path(
        "ticket/<int:pk>/update/",
        review.views.TicketUpdateView.as_view(),
        name="update_ticket",
    ),
    path(
        "ticket/<int:pk>/delete/",
        review.views.TicketDeleteView.as_view(),
        name="delete_ticket",
    ),
    path(
        "review/create/<int:ticket_pk>/",
        review.views.ReviewCreateView.as_view(),
        name="create_review",
    ),
    path(
        "review/create/",
        review.views.create_review_and_ticket,
        name="create_review_and_ticket",
    ),
    path(
        "review/detail/<int:pk>/",
        review.views.ReviewDetailView.as_view(),
        name="detail_review",
    ),
    path(
        "review/<int:pk>/update/",
        review.views.ReviewUpdateView.as_view(),
        name="update_review",
    ),
    path(
        "review/<int:pk>/delete/",
        review.views.ReviewDeleteView.as_view(),
        name="delete_review",
    ),
    path("follow/", review.views.FollowUsersView.as_view(), name="follow_users"),
    path(
        "unfollow/<int:user_id>/",
        review.views.UnfollowUserView.as_view(),
        name="unfollow_user",
    ),
    path("user_posts/", review.views.user_posts, name="user_posts"),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
