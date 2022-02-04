from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from . import views

app_name = 'rest'

urlpatterns = [
    path('', views.ProductsLists.as_view(), name='index'),
    path('cart_detail/<product_id>/', views.CartDetail.as_view(), name='cart_detail'),
    path('cart_fingers/', views.FingersSet.as_view(), name='cart_fingers'),
    path('cart_remove/<product_id>/', views.CartRemove.as_view(), name='cart_remove'),
    path('order/create/', views.OrderCreate.as_view(), name='order_create'),
    path('zarinpal/request_verify/', views.zarinpal_request_verify),
    path('api-token-auth/', obtain_auth_token),      #creating user(sign up) must done in web.
]

