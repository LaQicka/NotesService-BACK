from django.urls import path, include
from . import views  # Assuming your DocumentViewSet is in a views.py file

urlpatterns = [
    path('documents/<int:pk>/download/', views.DocumentViewSet.as_view({'get': 'download'}), name='document-download'),
    # ... (other URL patterns)
]
