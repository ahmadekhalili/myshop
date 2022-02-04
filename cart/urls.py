from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_detail, name='cart_detail'),
    path('add/<product_id>/', views.cart_add, name='cart_add'),
    path('fingers/', views.set_fingers, name='set_fingers'),
    path('remove/<product_id>/<path>/', views.cart_remove, name='cart_remove'),
]


