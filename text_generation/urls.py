from django.urls import path
from text_generation.views import index, generate_text, runtest

urlpatterns = [
    path('index/', index, name='text_generation_index'),
    path('generate_text/', generate_text, name='text_generation_generate_text'),
    path('runtest', runtest, name='text_generation_runtest'),
]