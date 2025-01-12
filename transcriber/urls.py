# from django.urls import path
# from . import views

# urlpatterns = [
#     path('', views.index, name='index'),
#     path('transcribe/', views.transcribe, name='transcribe'),
# ]

from django.urls import path
from . import views

urlpatterns = [
    path('', views.form, name='form'),
    path('start-call/', views.start_call, name='start_call'),
    path('call/', views.index, name='index'),
    path('transcribe/', views.transcribe, name='transcribe'),
]