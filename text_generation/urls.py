from django.urls import path
from text_generation.views import home, rag, textgen, generate_text, runtest, login_view, register, logout_view

urlpatterns = [
    path('', home, name='home'),
    path('textgen/', textgen, name='index'),
    path('rag/', rag, name='rag'),
    path('generate_text/', generate_text, name='text_generation_generate_text'),
    path('runtest/', runtest, name='text_generation_runtest'),
    path('login/', login_view, name='login'),
    path('register/', register, name='register'),
    path('logout/', logout_view, name='logout'),
]