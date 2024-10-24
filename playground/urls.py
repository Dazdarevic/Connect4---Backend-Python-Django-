from django.urls import path
from . import humanAiEasy
from . import humanAiMedium
from . import humanAiHard

urlpatterns = [
    path('get_best_move4/', humanAiEasy.get_best_move, name='get_best_move4'),
    path('get_best_move5/', humanAiMedium.get_best_move, name='get_best_move5'),
    path('hardAI/', humanAiHard.get_best_move, name='hardAI'),
]