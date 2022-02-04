from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('searches/', views.searchProduct, name='product_search'),
    path('about-us/', views.aboutUs, name='about_us'),
    path('categories/', views.product_selects_views, name='product_list_by_category'),
    path('<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),
]
