import random

from django.core.cache import cache
from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers, status
from rest_framework.exceptions import (
    NotFound,
    AuthenticationFailed,
    PermissionDenied,
    NotAuthenticated,
)
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenObtainSerializer,
)

from app.libs.cache_prefix import PHONE_VERIFICATION_CODE_PREFIX
from .models import VerificationType
from user.models import User


class JwtTokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user) -> TokenObtainPairSerializer.data:
        token = super().get_token(user)

        token["email"] = user.email

        return {"access": str(token.access_token), "refresh": str(token)}


class SignInUserSeriallizer(serializers.Serializer):
    email = serializers.EmailField(help_text="이메일", allow_null=True, required=False)
    phone_number = serializers.CharField(
        help_text="휴대전화번호", max_length=13, allow_null=True, required=False
    )
    password = serializers.CharField(
        help_text="비밀번호", max_length=255, allow_null=False, required=True
    )

    def validate(self, data):
        if not (data.get("email") or data.get("phone_number")):
            raise serializers.ValidationError("이메일 또는 휴대전화번호를 입력해주세요.")

        return data

    def get_user_by_email(self) -> User:
        email = self.validated_data.get("email")
        password = self.validated_data.get("password")

        user = User.objects.filter(email=email).first()

        if not user:
            raise NotFound("USER_NOT_FOUND")

        if not user.check_password(password):
            raise AuthenticationFailed("PASSWORD_INCORRECT")

        return user

    def get_user_by_phone_number(self) -> User:
        phone_number = self.validated_data.get("phone_number")
        password = self.validated_data.get("password")

        user = User.objects.filter(phone_number=phone_number).first()

        if not user:
            raise NotFound("USER_NOT_FOUND")

        if not user.check_password(password):
            raise AuthenticationFailed("PASSWORD_INCORRECT")

        return user


class VerificationCodeSerializer(serializers.Serializer):
    verification_code = serializers.CharField(
        help_text="인증번호", max_length=6, allow_null=False, required=True
    )
    verification_type = serializers.CharField(
        help_text="인증타입", allow_null=False, required=True
    )

    def validate_verification_code(self, verification_code):
        return verification_code.strip()

    def validate_verification_type(self, verification_type):
        # string 으로 입력 받은 verification_type 에 맞는 VerificationType 리턴
        # 없으면 KeyError raise
        return VerificationType[verification_type.upper()]


@extend_schema_serializer(exclude_fields=["verification_type"])
class GenerateVerificationCodeSerializer(serializers.Serializer):
    phone_number = serializers.CharField(
        help_text="전화번호", max_length=13, allow_null=False, required=True
    )
    verification_type = serializers.CharField(
        help_text="인증타입", allow_null=False, required=True
    )

    def validate_verification_type(self, verification_type):
        # string 으로 입력 받은 verification_type 에 맞는 VerificationType 리턴
        # 없으면 KeyError raise
        return VerificationType[verification_type.upper()]

    def generate_verification_code(self):
        phone_number = self.validated_data.get("phone_number")
        verification_type = self.validated_data.get("verification_type")
        cache_key = (
            f"{PHONE_VERIFICATION_CODE_PREFIX}{verification_type}_{phone_number}"
        )

        if (  # 회원가입을 위한 인증코드 생성시 중복번호인지 확인
            not User.check_duplicate_phone_number(phone_number)
            and verification_type is VerificationType.SIGN_UP
        ):
            raise PermissionDenied("PHONE_NUMBER_ALREADY_EXIST")

        if (  # 비밀번호 재설정을 위한 인증코드 생성시 번호에 해당하는 유저 찾기
            User.check_duplicate_phone_number(phone_number)
            and verification_type is VerificationType.RESET_PASSWORD
        ):
            raise NotFound("USER_NOTFOUND")

        code = str(random.random())[2:8]
        cache.set(
            cache_key,
            code,
            timeout=180,
        )
        print(cache_key + " // " + str(cache.get(cache_key)))
        return {"verification_code": code, "verification_type": verification_type}


@extend_schema_serializer(exclude_fields=["verification_type"])
class VerifyVerificationCodeSerializer(VerificationCodeSerializer):
    phone_number = serializers.CharField(
        help_text="전화번호", max_length=13, allow_null=False, required=True
    )
    verification_code = serializers.CharField(
        help_text="인증번호", max_length=6, allow_null=False, required=True
    )
    verification_type = serializers.CharField(
        help_text="인증타입", allow_null=False, required=True
    )

    def validate_verification_code(self, verification_code):
        return verification_code.strip()

    def validate_verification_type(self, verification_type):
        # string 으로 입력 받은 verification_type 에 맞는 VerificationType 리턴
        # 없으면 KeyError raise
        return VerificationType[verification_type.upper()]

    def verify_verification_code(self):
        phone_number = self.validated_data.get("phone_number")
        verification_code = self.validated_data.get("verification_code")
        verification_type = self.validated_data.get("verification_type")
        cache_key = (
            f"{PHONE_VERIFICATION_CODE_PREFIX}{verification_type}_{phone_number}"
        )
        code = cache.get(cache_key)
        print(cache_key + " // " + str(code))

        if code is None:
            raise NotFound("VERIFICATION_CODE_NOT_FOUND")

        """
        회원가입 시 인증코드 입력이 필요하기 때문에
        인증코드 인증 API에서는 인증되면 인증번호의 TTL을 늘려줌
        """
        if code == verification_code:
            cache.set(
                cache_key,
                code,
                timeout=3600,
            )
            return True
        else:
            raise NotAuthenticated("VERIFICATION_CODE_INCORRECT")
