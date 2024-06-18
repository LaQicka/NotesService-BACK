from django.contrib.auth.models import User
from django.db import models

from document_service.models import Document


class Type(models.Model):
    id = models.AutoField(primary_key=True)
    TypeName = models.CharField(max_length=255)

    def __str__(self):
        return self.TypeName


class Note(models.Model):
    id = models.AutoField(primary_key=True)
    creationDate = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    docId = models.ForeignKey(Document, on_delete=models.CASCADE, null=True, blank=True)
    typeId = models.ForeignKey(Type, on_delete=models.DO_NOTHING)
    payload = models.TextField()

    def __str__(self):
        return f"Note #{self.id} - {self.subject}"


class Tag(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class TagNoteSub(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    note = models.ForeignKey(Note, on_delete=models.CASCADE)

    class Meta:
        # Уникальность пары child-parent
        unique_together = ('tag', 'note')

    def __str__(self):
        return f"{self.tag.title} -> {self.note.subject}"


class Genealogy(models.Model):
    child = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name='child_relations')
    parent = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name='parent_relations')

    class Meta:
        # Уникальность пары child-parent
        unique_together = ('child', 'parent')

    def __str__(self):
        return f"{self.parent.title} -> {self.child.title}"
