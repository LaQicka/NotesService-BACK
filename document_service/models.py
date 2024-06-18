from django.db import models
from django.db.models import FileField


class DocType(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class Document(models.Model):
    id = models.AutoField(primary_key=True)
    file = FileField(upload_to='documents')
    TypeId = models.ForeignKey(DocType, on_delete=models.CASCADE, default=4)

    def __str__(self) -> str:
        return "Document " + str(self.id)
