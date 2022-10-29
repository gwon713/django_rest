from typing import Type, Union

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema

from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from authentication.serializers import JwtTokenSerializer
from .models import User
from .serializers import (
    UserSerializer,
    SignUpUserSerializer,
    ResetPasswordUserSerializer,
)


class UserViewSet(viewsets.GenericViewSet):

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get_serializer_class(self) -> Type[Union[UserSerializer, SignUpUserSerializer]]:
        if self.action in "sign_up":
            return SignUpUserSerializer
        if self.action in ("list", "retrieve"):
            return UserSerializer

        return UserSerializer

    def list(self, request):
        serializer = UserSerializer(self.queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        user = get_object_or_404(self.queryset, pk=pk)
        serializer = UserSerializer(user)
        return Response(serializer.data)


class SignUpUserView(APIView):

    authentication_classes = ()
    permission_classes = ()

    serializer_class = UserSerializer
    queryset = User.objects.all()

    @extend_schema(
        request=SignUpUserSerializer,
        responses={status.HTTP_201_CREATED: TokenObtainPairSerializer},
    )
    def post(self, request):
        serializer = SignUpUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.verify(validated_data=serializer.validated_data)
        result = serializer.create(validated_data=serializer.validated_data)
        token = JwtTokenSerializer.get_token(result)

        return Response(
            token,
            status=status.HTTP_201_CREATED,
        )


class ResetPasswordUserView(APIView):

    authentication_classes = ()
    permission_classes = ()

    serializer_class = UserSerializer
    queryset = User.objects.all()

    @extend_schema(
        request=ResetPasswordUserSerializer,
        responses={status.HTTP_200_OK: {}},
    )
    def put(self, request):
        serializer = ResetPasswordUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.verify(validated_data=serializer.validated_data)
        serializer.update_password(validated_data=serializer.validated_data)

        return Response(
            "SUCCESS_RESET_PASSWORD",
            status=status.HTTP_201_CREATED,
        )
