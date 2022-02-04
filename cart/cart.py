from django.contrib.sessions.backends.db import SessionStore
from django.shortcuts import get_object_or_404
from decimal import Decimal

from django.conf import settings
from shop.models import Product
from shop import categories_set
from .models import SesKey
        
class Cart(object):

    def __init__(self, request):
        self.request = request
        if self.request.user.is_authenticated:
            ob = SesKey.objects.get(user=self.request.user)     #SesKey created with post_save signal.
            if ob.ses_key:
                self.session = SessionStore(session_key=ob.ses_key)      
                self.cart_session_auth = (True, True)
            else:                                               #in first add product of a user(in intir of its age).
                self.session = request.session                  #request.session is authentication session(that in logout use for cart too). SessionStore(session_key=ob.ses_key is cart authentication
                self.cart_session_auth = (False, True)
        else:
            self.session = request.session
            self.cart_session_auth = (False, False)
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:                                            #in first ading product for unauthenticated user, request.session has data butit is cached data and it is not eny database session and has not eny session id to sen to user but in second runing cart after first, program come here and because  request.session has dont dont come to this and so dont false modified and so in saving session in database will create so for unauthenticated user. session id will create after second acctess to class cart!  
            cart = self.session[settings.CART_SESSION_ID] = {}  #eny changing self.session will affect request.sessio(mutable)
            self.session.modified = False                       #dont create session table for every user visiting page. but dont affect after statements.
        self.cart = cart
        
    def add(self, product_id, quantity=1, update_quantity=False):
        product_id = str(product_id)
        product = get_object_or_404(Product, id=product_id)         #for id, str/int is dont diff here
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': quantity, 'price': str(product.price)}
        else:
            if update_quantity:
                self.cart[product_id]['quantity'] = quantity
            else:
                self.cart[product_id] = {'quantity': quantity, 'price': str(product.price)}       
        self.save()
    
    def save(self):

        self.session[settings.CART_SESSION_ID] = self.cart                      #if self.session is authentication session, modify-save will done here.                                         
        if self.cart_session_auth[0]:                                           #self.session is cart session and need .save for saving. user also login and have ses_key too.         
            self.session.save()
        elif not self.cart_session_auth[0] and self.cart_session_auth[1]:       #self.session is authentication session, and login
            s = SessionStore()
            s[settings.CART_SESSION_ID] =  self.session[settings.CART_SESSION_ID]
            s.create()
            del self.session[settings.CART_SESSION_ID]
            ob = SesKey.objects.get(user=self.request.user)
            ob.ses_key=s.session_key
            ob.save()
            
    def remove(self, product_id):
        product_id = str(product_id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        product_ids = self.cart.keys()
        for key in self.cart:
            item = self.cart[key].copy()             #item = self.cart[key] is mutable so every change in item, affect self.cart and self.session and self.request!!!!
            product = Product.objects.get(id=int(key))
            item['product'] = product
            item['price'] = int(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_products_numbers(self):
        i = 0
        for item in self.cart.values():
            i +=1
        return i
            
    def get_total_price(self):
        return sum(Decimal(item['price'])*item['quantity'] for item in self.cart.values())
    
    def clear(self):
        self.session[settings.CART_SESSION_ID] = {}
        self.session.save()




