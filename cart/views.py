from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from shop.models import Product
from .cart import Cart
from .forms import CartAddProductForm
from django.http import HttpResponse
#CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
    
@require_POST                                         #prevent side effect(get method..).
def cart_add(request, product_id):
    cart = Cart(request)
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data                        #product_id is str but dont matter.
        cart.add(product_id=product_id, quantity=cd['quantity'], update_quantity=cd['update'])    #cd['quantity'] is int but how is it because: coerce=int ? request.data['quantity'] is rest/views/CartDetail is string
    return redirect('cart:cart_detail')


def set_fingers(request):                                  #fingers are datas like quantity,color or other and this func refresh fingers on cart form products. also update product(price...)(supose user 10 min stay in cart and next click to order and in that 10 min new price coming to taht prodoct!!
    cart = Cart(request)
    cart2 = Cart(request)                                  #if user cart in below loop, iter erro will arise. if we define cart2 like: cart2 = cart error will rise too becase cart2 and cart is same object pointing in ram.
    for item in cart2:
        product = item['product']
        quantity = request.POST.get(str(product.id))           #when product quantity is 0 this variable will be None,   careful quantity is str   
        if product.stock>0 and quantity:
            cart.add(product_id=product.id, quantity=int(quantity), update_quantity=True)        
        else:
            cart.remove(product.id)
    if not request.user.is_authenticated:
        return redirect('login')                           #anomios user must can update/change its products quantity and etc...) so we redirect him is last set_fingers.    users:login dont means.(it is created by auth app not users)
    return redirect('orders:order_create')

    
def cart_remove(request, product_id, path):
    cart = Cart(request)
    cart.remove(product_id)
    path = path.replace('@', '/')
    return redirect(path)
        
def cart_detail(request):
    cart = Cart(request)
    return render(request, 'cart/detail.html', {'cart':Cart(request), 'range':range(0,21)})
