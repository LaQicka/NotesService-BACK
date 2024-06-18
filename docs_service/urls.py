from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from document_service.views import DocumentViewSet, DocTypeViewSet
from note_service.views import TypeViewSet, NoteViewSet, TagViewSet

router = DefaultRouter()
router.register(r'documents', DocumentViewSet, basename='documents')
router.register(r'doctypes', DocTypeViewSet, basename='doctypes')
router.register(r'noteservice/notes', NoteViewSet, basename='notes')
router.register(r'noteservice/types', TypeViewSet, basename='notes_types')
router.register(r'noteservice/tags', TagViewSet, basename='notes_tags')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/documents/<int:pk>/download/', DocumentViewSet.as_view({'get': 'download'}), name='document-download'),
    # ... (other URL patterns)
]
