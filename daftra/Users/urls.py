from django.urls import path
from .views import *

urlpatterns = [
    path('login/', CustomTokenObtainPairView.as_view()),
    path('logout/blacklist/', BlacklistTokenUpdateView.as_view(),
         name='blacklist'),
]
