from django.db import models

from libs.common.model.abstract_model import AbstractModel


class User(AbstractModel):
    email = models.EmailField(help_text="이메일", unique=True, max_length=320, null=False)
    nick_name = models.CharField(help_text="닉네임", max_length=50, null=True, blank=True)
    password = models.CharField(help_text="비밀번호", max_length=255, null=False)
    name = models.CharField(help_text="이름", max_length=50, null=False)
    phone_number = models.CharField(
        help_text="휴대전화", unique=True, max_length=13, null=False
    )
    last_login_at = models.DateTimeField(
        help_text="마지막 로그인 시간", auto_now_add=True, null=True, blank=True
    )

    class Meta:
        db_table = "user"
        indexes = [
            models.Index(fields=["id"]),
            models.Index(fields=["email"]),
            models.Index(fields=["phone_number"]),
        ]
        constraints = []