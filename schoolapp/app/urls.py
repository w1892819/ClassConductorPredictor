from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('update-behavior/<int:student_id>/', views.update_behavior, name='update_behavior'),
    path('get-prediction/<int:student_id>/', views.get_behavior_prediction, name='get_prediction'),
]
