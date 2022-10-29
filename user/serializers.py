from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from authentication.models import VerificationType
from authentication.serializers import VerifyVerificationCodeSerializer
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "nick_name",
            "password",
            "name",
            "phone_number",
            "last_login_at",
            "created_at",
            "updated_at",
            "deleted_at",
        ]


class SignUpUserSerializer(serializers.ModelSerializer):
    verification_code = serializers.CharField(
        help_text="인증번호", max_length=6, allow_null=False, required=True
    )

    def verify(self, validated_data):
        phone_number = validated_data.get("phone_number")
        verification_code = validated_data.get("verification_code")

        verify = VerifyVerificationCodeSerializer(
            data={
                "phone_number": phone_number,
                "verification_code": verification_code,
                "verification_type": VerificationType.SIGN_UP.value,
            }
        )
        verify.is_valid(raise_exception=True)
        verify.verify_verification_code()

        return True

    def create(self, validated_data):
        password = validated_data.get("password")
        # User Model 인스턴스 만들기 전 verify를 완료한 code 제거
        validated_data.pop("verification_code")
        user_instance = self.Meta.model(**validated_data)
        # encrypt password use argon2
        if password is not None:
            user_instance.set_password(password)
        user_instance.save()
        return user_instance

    class Meta:
        model = User
        fields = [
            "email",
            "nick_name",
            "password",
            "name",
            "phone_number",
            "verification_code",
        ]


class ResetPasswordUserSerializer(serializers.Serializer):
    phone_number = serializers.CharField(
        help_text="전화번호", max_length=13, allow_null=False, required=True
    )
    verification_code = serializers.CharField(
        help_text="인증번호", max_length=6, allow_null=False, required=True
    )
    new_password = serializers.CharField(
        help_text="변경할 패스워드", max_length=255, allow_null=False, required=True
    )

    def validate_verification_code(self, verification_code):
        return verification_code.strip()

    def validate_verification_type(self, verification_type):
        # string 으로 입력 받은 verification_type 에 맞는 VerificationType 리턴
        # 없으면 KeyError raise
        return VerificationType[verification_type.upper()]

    def verify(self, validated_data):
        phone_number = validated_data.get("phone_number")
        verification_code = validated_data.get("verification_code")

        verify = VerifyVerificationCodeSerializer(
            data={
                "phone_number": phone_number,
                "verification_code": verification_code,
                "verification_type": VerificationType.RESET_PASSWORD.value,
            }
        )
        verify.is_valid(raise_exception=True)
        verify.verify_verification_code()

        return True

    def update_password(self, validated_data):
        new_password = validated_data.get("new_password")
        phone_number = validated_data.get("phone_number")

        user = User.objects.filter(phone_number=phone_number).first()

        if user.check_password(new_password):
            raise ValidationError("DUPLICATE_USER_PASSWORD")

        user.set_password(new_password)
        user.save()

        return user
