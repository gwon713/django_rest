from rest_framework import routers

from .views import AuthViewSet, AuthVerificationCodeViewSet

router = routers.DefaultRouter()

router.register(r"", AuthViewSet, basename="Auth")
router.register(r"code", AuthVerificationCodeViewSet, basename="Auth Verification Code")

urlpatterns = []

urlpatterns += router.urls
