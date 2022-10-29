from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from user.models import User
from .models import VerificationType
from .serializers import (
    SignInUserSeriallizer,
    JwtTokenSerializer,
    VerificationCodeSerializer,
    GenerateVerificationCodeSerializer,
    VerifyVerificationCodeSerializer,
)


class AuthViewSet(viewsets.GenericViewSet):

    authentication_classes = ()
    permission_classes = ()

    serializer_class = SignInUserSeriallizer
    queryset = User.objects.all()

    @extend_schema(
        request=SignInUserSeriallizer,
        responses={status.HTTP_201_CREATED: TokenObtainPairSerializer},
    )
    @action(methods=["post"], detail=False)
    def sign_in(self, request):
        serializer = SignInUserSeriallizer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = None
        if serializer.validated_data.get("email"):
            user = serializer.get_user_by_email()
        elif serializer.validated_data.get("phone_number"):
            user = serializer.get_user_by_phone_number()
        if user is None:
            return NotFound("USER_NOT_FOUND")

        user.update_last_login_at()
        return Response(
            JwtTokenSerializer.get_token(user),
            status=status.HTTP_201_CREATED,
        )


class AuthVerificationCodeViewSet(viewsets.GenericViewSet):

    authentication_classes = ()
    permission_classes = ()

    @extend_schema(
        request=GenerateVerificationCodeSerializer,
        responses={status.HTTP_201_CREATED: VerificationCodeSerializer},
        parameters=[
            OpenApiParameter(
                name="verificationType",
                type={
                    "type": "enum",
                    "enum": [
                        VerificationType.SIGN_UP.value,
                        VerificationType.RESET_PASSWORD.value,
                    ],
                },
                location=OpenApiParameter.QUERY,
                description="VerificationType",
            ),
        ],
    )
    @action(methods=["post"], detail=False)
    def generate(self, request):
        serializer = GenerateVerificationCodeSerializer(
            data={
                "phone_number": request.data.get("phone_number"),
                "verification_type": request.query_params.get("verificationType"),
            }
        )
        serializer.is_valid(raise_exception=True)
        print(serializer.data)
        result = serializer.generate_verification_code()

        return Response(
            {
                "verification_code": result.get("verification_code"),
                "verification_type": result.get("verification_type").value,
            },
            status.HTTP_200_OK,
        )

    @extend_schema(
        request=VerifyVerificationCodeSerializer,
        responses={status.HTTP_200_OK: {}},
        parameters=[
            OpenApiParameter(
                name="verificationType",
                type={
                    "type": "enum",
                    "enum": [
                        VerificationType.SIGN_UP.value,
                        VerificationType.RESET_PASSWORD.value,
                    ],
                },
                location=OpenApiParameter.QUERY,
                description="VerificationType",
            ),
        ],
    )
    @action(methods=["post"], detail=False)
    def verify(self, request):
        serializer = VerifyVerificationCodeSerializer(
            data={
                "phone_number": request.data.get("phone_number"),
                "verification_code": request.data.get("verification_code"),
                "verification_type": request.query_params.get("verificationType"),
            }
        )
        serializer.is_valid(raise_exception=True)
        serializer.verify_verification_code()

        return Response(
            "VERIFY_SUCCESS",
            status.HTTP_200_OK,
        )
