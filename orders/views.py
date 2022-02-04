from __future__ import absolute_import, unicode_literals
from django.shortcuts import render, redirect

from shop.models import Product
from .models import OrderItem, Order
from .forms import OrderCreateForm
from .tasks import order_created
from cart.cart import Cart

def order_create(request):
    cart = Cart(request)
    user = request.user
    if user.is_authenticated:
        if request.POST:                                           #when with redirect come to order_create(from set_fingers..) this dont run(its get method)
            form = OrderCreateForm(request.POST)
            if form.is_valid():
                pre_order = form.save(commit=False)     #order_pre is order without its user yani pish order(ke baiad kamel shavad)
                pre_order.user = request.user           #form henghame save shodan(form.save()) ba che model objecti car mikonad?sopuse: ob1 = form.save()(means when you run form.save() its create ob1 of Order. ba form.save(commit=False) on object ra bedast avordim(bedune ejade vagheii on dar databaase va admin page va...(pas bedune hich validation error rasing) dar khat bad be on object userash ra dadim hal on object user darad va form, ba form.save() mitavanad on object ra kamel konad. (chon khude form .user nadasht)
                order = form.save()
                for item in cart:
                    OrderItem.objects.create(order=order,                         #Order: dar yek saferesh masalan ba 4 kala be adress babaii in 4 item, OrderItems, va on yek sefaresh, Order ast ke momken ast dar sefaresh badi bekhaham be adress minaii va be name yek kase digar(baradar, pedarbozorg ....) sefaresh bedaham chand orderitem ra.
                                             product=item['product'],
                                             price=item['price'],
                                             quantity=item['quantity'])
                #Launch asynchronous task
                #order_created.delay(order.id)
                #return render(request, 'orders/order/created.html', {'order':order})
                return redirect('zarinpal:request')               
        else:                                              #get method
            if user.orders.all():
                last_order = user.orders.all()[len(user.orders.all())-1]
                form = OrderCreateForm(instance=last_order) #select last order of user
            else:
                form = OrderCreateForm(instance=user)
        return render(request, 'orders/order/create.html',
                      {'cart':cart, 'form':form})
    else:                                                         #we dont need it but is for assurance
        return render(request, 'orders/order/exception.html')        


def productsOrdered(request):
    orderitems = []
    products = []
    for order in request.user.orders.all():
        orderitems += order.items.all()
        for orderitem in order.items.all():
            products += [orderitem.product]
            
    return render(request, 'orders/order/products-ordered.html',
                  {'zip_orderitems':zip(orderitems, products)})


