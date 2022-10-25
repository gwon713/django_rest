from django.db import models


class AbstractModel(models.Model):
    created_at = models.DateTimeField(help_text='생성일', auto_now_add=True, null=False)
    updated_at = models.DateTimeField(help_text='마지막 수정일', auto_now=True, null=False)
    deleted_at = models.DateTimeField(help_text='삭제일', null=True, blank=True)

    class Meta:
        abstract = True