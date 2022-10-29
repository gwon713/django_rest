import datetime

from django.db import models
from app.libs.abstract_model import AbstractModel

from argon2 import PasswordHasher

ph = PasswordHasher()


class User(AbstractModel):
    email = models.EmailField("user_email", unique=True, max_length=320, null=False)
    nick_name = models.CharField("user_nick_name", max_length=50, null=True, blank=True)
    password = models.CharField("user_password", max_length=255, null=False)
    name = models.CharField("user_name", max_length=50, null=False)
    phone_number = models.CharField(
        "user_phone_number", unique=True, max_length=13, null=False
    )
    last_login_at = models.DateTimeField(
        "user_last_login_at", auto_now_add=True, null=True, blank=True
    )

    class Meta:
        db_table = "user"
        indexes = [
            models.Index(fields=["id"]),
            models.Index(fields=["email"]),
            models.Index(fields=["phone_number"]),
        ]
        constraints = []

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["password"]

    @property
    def is_anonymous(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    def set_password(self, password):
        self.password = ph.hash(password)

    def check_password(self, password) -> bool:
        try:
            ph.verify(self.password, password)
            return True
        except:
            return False

    def update_last_login_at(self):
        self.last_login_at = datetime.datetime.now().time()

    @classmethod
    def check_duplicate_email(cls, email) -> bool:
        # 중복 이메일 유저 확인
        existing_email = User.objects.filter(email=email).first()
        if existing_email:
            return False
        return True

    @classmethod
    def check_duplicate_phone_number(cls, phone_number) -> bool:
        # 중복 핸드폰 번호 유저 확인
        existing_phone_number = User.objects.filter(phone_number=phone_number).first()
        if existing_phone_number:
            return False
        return True
