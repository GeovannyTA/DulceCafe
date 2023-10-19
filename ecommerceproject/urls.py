from django.contrib import admin
from django.urls import path, include
from ecommerce import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.signout, name='logout'),
    path('login/', views.signin, name='login'),
    path('accounts/', include('allauth.urls')),
]
