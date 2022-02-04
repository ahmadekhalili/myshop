from rest_framework import serializers

from shop.models import Product
from shop.categories_set import categories_tree
from cart.cart import Cart
from orders.models import Order
from users.models import User

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'



class ContextUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

def serialize_cart(request):
    cart = Cart(request)
    final_cart = []
    for item in cart:
        product = item['product']
        item['product'] = ProductSerializer(product).data      #many=True is dont need because we give him in eny loop one product,   before putting .data:  Object of type ProductSerializer is not JSON serializable
        final_cart.append(item)
    return final_cart                                                     #return list of dictioneries

def context_serialize(user, request):                                     #cart and user must sent to user in every view(like web)
    path = request.path.replace('/','@')  
    if not user.is_authenticated:
        return {'user':{},                                                
                'cart':serialize_cart(request),
                'path':path,
                'categories_tree':list(categories_tree().items())}
    
    return {'user':ContextUserSerializer(user).data,
            'cart':serialize_cart(request),
            'path':path,
            'categories_tree':list(categories_tree().items())}            



class OrerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["first_name", "last_name", "email", "address", "postal_code", "city"]







