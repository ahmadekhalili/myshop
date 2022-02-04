from django.contrib.sessions.backends.db import SessionStore
from django.shortcuts import render, redirect
from django.conf import settings
from rest_framework import authentication
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from zeep import Client                                             #zeep pakage(not django or python)

from .serializers import ProductSerializer, context_serialize, OrerSerializer
from cart.cart import Cart
from shop.models import Product
from shop.categories_set import categories_tree, categories_tree_fa
from shop.product_selects_methods import random_products, bestSellingProducts, searchEngine, listProductByCat, listProductByPrice


class ProductsLists(APIView):                                                               #index
    def get(self, request):
        names = ['iPhone 8 Plus (Product) Red', 'V30s Thinq', 'Galaxy Note 9']    
        products = Product.objects.filter(available=True)
        vije_products = [products.get(name=name) for name in names]
        new_products = products[:12]  
        best_selling = bestSellingProducts(Product.objects.all())[ :-5:-1]
        all_products = [vije_products, new_products, best_selling]
        all_products_txt = ['vijeproducts',  'newproducts', 'bestselling']                  #orders of all_products_txt, depend on all_products.

        serializers = {}
        for products, txt in zip(all_products, all_products_txt):
            serializers[txt] = ProductSerializer(products, many=True).data
        return Response({**context_serialize(request.user, request), **serializers})    #is like {'cart':..., 'user':..., 'zip_bestselling':..., 'zip_newproducts':..., 'zip_vijeproducts':...}     

class CartDetail(APIView):                          #cart_add+cart_detail
    def post(self, request, **kwargs):
        sessionid = request.META.get('HTTP_SESSIONID')                                      #for anomious user in api, unlike broser that send sessionid auto and load request.session here we must do handy.
        if sessionid:                                                                       #if sessionid is wrong/fake django create new SessionStor() 
            request.session = SessionStore(session_key = sessionid)                         #if this not provide, for every anomios request from api, django will create a session. (because in first request made a session and in response create it, but in next request forget it(sessionid unlike broser no sent) so again made session and in response create another. but here just save(in response and cart.py in one session(SessionStore(sessionid)                                       
        cart = Cart(request)       
        product_id = self.kwargs['product_id']
        if product_id != 'None':                                                                                 #in url we have not bool(None) value, all is str.  if product_id='None' just is product_detail else cart_add+cart_detail.
            update_quantity = True if request.data.get('update_quantity')=='True' else False
            cart.add(product_id, int(request.data['quantity']), update_quantity) 
        if request.user.is_authenticated:                                                                      #range(21) is oject not list numbers.
            return Response({**context_serialize(request.user, request), 'range':list(range(21))})             #dont need send sessionid. session will optain with user
        else:
            request.session.save()                                                                             #save auth session, for creating them(and obtain key).
            return Response({**context_serialize(request.user, request), 'range':list(range(21)), 'sessionid':request.session.session_key})               #session configurations need sessionid

class FingersSet(APIView):                                                                   #django implement(default)
    def post(self, request):
        cart = Cart(request)
        cart2 = Cart(request) 
        for item in cart2:
            product = item['product']
            quantity = request.data[str(product.id)]                                         #careful quantity is str   
            if product.stock>0:
                cart.add(product_id=product.id, quantity=int(quantity), update_quantity=True)
            else:
                cart.remove(product.id)
        return redirect('rest:order_create')

class CartRemove(APIView):
    def get(self, request, **kwargs):
        cart = Cart(request)
        cart.remove(self.kwargs['product_id'])
        request._request.method='POST'                                          #you can put post method instead of get(for CartRemove) and remove thease two line.
        request._request.POST={}
        return CartDetail().dispatch(request._request, product_id=None)         #this is like redirect to CartDetail,   we just give request to class and next, initial/setup our class, and class will decision for outpute,from our request, that here choice post method.


class OrderCreate(APIView):                                                     #you can test succesful redirecting(from cart_detail to order_create) by SessionAuthentication setting in settings and test with browser, but note when redirect, browser url dont show redirected url, but its real redirect and recive data of target view.
    def get(self, request):
        return Response(context_serialize(request.user, request))               #important: user redirect to OrderForm and come to this get, and after return, recive data and clint side make desicion that request.user is {} so raise authentication error for cliet. else(user authenticat) clint show OrerSerializer form(clint know OrerSerializer fields(ourself create front) and dont need sent its fields or etc...). 
                                                                                #context_serialize is like context_processors in django(must send for every page(its data use in header)
    def post(self, request):
        if not request.user.is_authenticated:
            return Response(context_serialize(request.user, request))           #in clint side proper error should populate. 
        serializer = OrerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)                                           #request._request.method = 'POST' ,   for merging request and verify in myshop/zarinpal here post in request and get verify.
            request._request.POST = request.POST                                         #without this error will raise. request._request.POST must be our real post data(data that we post in here(order_create)
            return zarinpal_request_verify(request._request)                             #return ZarinpalRequestVerify().dispatch(request._request) 
        else:
            return Response({**context_serialize(request.user, request), **serializer.errors})


@api_view(['GET', 'POST'])
#@authentication_classes([authentication.TokenAuthentication, authentication.SessionAuthentication])
@permission_classes([permissions.IsAuthenticated])
def zarinpal_request_verify(request):                 #with APIView dont work zarinpal
    cart = Cart(request)
    MERCHANT = 'XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX'
    description = "توضیحات مربوط به تراکنش را در این قسمت وارد کنید"
    email = request.user.email
    mobile = request.user.phone if request.user.phone else None
    CallbackURL = 'http://127.0.0.1:8000/rest/zarinpal/request_verify/'      #its better ourself generate CallbackURL(to clint).
    global amount
    amount = cart.get_total_price()                                          #client.service.PaymentRequest and redirect('https://sandbox.zarinpal.com/pg/StartPay/' + str(result.Authority)) must do in clint.

    if request.method == 'GET':
        client = Client('https://sandbox.zarinpal.com/pg/services/WebGate/wsdl')     #here user is in our application so need to context_serialize(unline method post of this class) 
        if request.GET.get('Status') == 'OK':
            result = client.service.PaymentVerification(MERCHANT, request.GET['Authority'], amount)
            if result.Status == 100:
                for item in cart:                
                    item['product'].stock -= 1
                    item['product'].save()
                cart.clear()
                message = 'عملیات با موفقیت به اتمام رسیده و خرید شما انجام شد. کد پیگیری: '
                return Response({**context_serialize(request.user, request), 'RefID':result.RefID, 'message':message})
            elif result.Status == 101:
                message = 'عملیات پرداخت انجام شده است.'
                cart.clear()                                                #may need somthims.
                return Response({**context_serialize(request.user, request), 'status':str(result.Status), 'message':message})
            else:
                message = 'عمليات پرداخت ناموفق.'
                return Response({**context_serialize(request.user, request), 'status':str(result.Status), 'message':message})      
        else:
            message = 'عمليات پرداخت ناموفق يا توسط کاربر لغو شده است.'
            return Response({**context_serialize(request.user, request), 'status':str(result.Status), 'message':message})

    if request.method == 'POST':                       #here user is not in our application(it is in zarinpal page) so dont need to context_serialize                                  
        return Response({'MERCHANT':MERCHANT, 'description':description, 'email':email, 'mobile':str(mobile), 'CallbackURL':CallbackURL, 'amount':amount})    
        #'mobile':mobile raise error(phone is dont jason serializable.)
            

