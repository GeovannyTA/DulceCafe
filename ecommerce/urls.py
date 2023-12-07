from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.signout, name='logout'),
    path('login/', views.signin, name='login'),
    path('accounts/', include('allauth.urls')),
    path('report/', views.report, name='report'),
    path('get_respuesta/', views.get_respuesta, name='get_respuesta'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('update_item/', views.updateItem, name='update_item'),
    path('process_order/', views.processOrder, name='process_order'),
    path('product/', views.product, name='product'),
    path('add_product/', views.add_product, name='add_product'),
    path('profile/', views.profile, name='profile'),
    path('add_shipping/<int:id>/', views.add_shipping, name='add_shipping'),
    path('edit_profile/<int:id>/', views.edit_profile, name='edit_profile'),
    path('edit_shipping/<int:id>/', views.edit_shipping, name='edit_shipping'),
    path('edit_product/<int:id>/', views.edit_product, name='edit_product'),
    path('delete_product/<int:id>/', views.delete_product, name='delete_product'),
]
