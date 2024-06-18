from django.contrib import admin

from .models import Document, DocType

admin.site.register(Document)
admin.site.register(DocType)
