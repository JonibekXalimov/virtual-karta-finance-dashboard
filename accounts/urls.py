from django.urls import path
from django.contrib.auth.views import LogoutView

from .views import CustomLoginView, ProfileDetailView, SignUpView

urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("signup/", SignUpView.as_view(), name="signup"),
    path("profile/", ProfileDetailView.as_view(), name="profile"),
]
