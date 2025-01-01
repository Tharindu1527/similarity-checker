from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_assignment, name='upload_assignment'),
    path('compare/', views.compare_assignments, name='compare_assignments'),
    path('list/', views.get_assignments, name='get_assignments'),
]