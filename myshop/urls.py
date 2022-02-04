from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from django.urls import include, re_path
from shop import views

urlpatterns = [       
    path('', views.index, name='index'),
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')), 
    path('shop/', include('shop.urls', namespace='shop')),
    path('cart/', include('cart.urls', namespace='cart')),
    path('orders/', include('orders.urls', namespace='orders')),
    path('zarinpal/', include('zarinpal.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('auth/', include('rest_framework.urls')),                      #must dont put in rest app(error)
    path('rest/', include('rest.urls')), 
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
