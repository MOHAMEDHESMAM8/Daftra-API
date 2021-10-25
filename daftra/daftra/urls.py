
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path,include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('users/', include('Users.urls')),
    path('store/', include('Store.urls')),
    path('sales/', include('Sales.urls')),
    path('purchases/', include('Purchases.urls')),

]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
