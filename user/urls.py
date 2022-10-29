from django.urls import path
from rest_framework import routers

from .views import UserViewSet, SignUpUserView, ResetPasswordUserView

router = routers.DefaultRouter()

router.register(r"", UserViewSet, basename="User")

urlpatterns = [
    path(r"sign_up", SignUpUserView.as_view()),
    path(r"reset_pwd", ResetPasswordUserView.as_view()),
]

urlpatterns += router.urls
