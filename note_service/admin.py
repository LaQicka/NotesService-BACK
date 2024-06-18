from django.contrib import admin
from .models import Type, Note, Tag, Genealogy, TagNoteSub

admin.site.register(Type)
admin.site.register(Note)
admin.site.register(Tag)
admin.site.register(TagNoteSub)
admin.site.register(Genealogy)