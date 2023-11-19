from django.contrib import admin
from django.urls import path, include

from django.conf.urls.static import static
from django.conf import settings
from ecommerce.views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ecommerce/', include('ecommerce.urls')),
    path('', home, name='home')
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)