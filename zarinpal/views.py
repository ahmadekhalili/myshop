from zeep import Client
from django.shortcuts import redirect, render
from django.http import HttpResponse
from cart.cart import Cart

MERCHANT = 'XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX'
client = Client('https://sandbox.zarinpal.com/pg/services/WebGate/wsdl')
description = "توضیحات مربوط به تراکنش را در این قسمت وارد کنید"  # Required
email = 'email@example.com'  # Optional
mobile = '09123456789'  # Optional

CallbackURL = 'http://127.0.0.1:8000/zarinpal/verify/' # Important: need to edit for realy server.

def send_request(request):
    cart = Cart(request)
    global amount                                       #must global
    amount = cart.get_total_price()
    result = client.service.PaymentRequest(MERCHANT, amount, description, email, mobile, CallbackURL)
    if result.Status == 100:
        return redirect('https://sandbox.zarinpal.com/pg/StartPay/' + str(result.Authority))
    else:
        return HttpResponse('Error code: ' + str(result.Status))

def verify(request):  
    cart = Cart(request)
    if request.GET.get('Status') == 'OK':
        global amount
        amount = cart.get_total_price()
        result = client.service.PaymentVerification(MERCHANT, request.GET['Authority'], amount)
        if result.Status == 100:
            for item in cart:                
                item['product'].stock -= int(item['quantity'])
                item['product'].save()
            cart.clear()
            message = 'عملیات با موفقیت به اتمام رسیده و خرید شما انجام شد. کد پیگیری: '
            return render(request, 'zarinpal/Transaction-messages.html', {'RefID':result.RefID, 'message':message})
        elif result.Status == 101:
            message = 'عملیات پرداخت انجام شده است.'
            cart.clear()                                    #may occur somthims(tested)
            return render(request, 'zarinpal/Transaction-messages.html', {'status':str(result.Status), 'message':message})
        else:
            message = 'عمليات پرداخت ناموفق.'
            return render(request, 'zarinpal/Transaction-messages.html', {'status':str(result.Status), 'message':message})      
    else:
        message = 'عمليات پرداخت ناموفق يا توسط کاربر لغو شده است.'
        return render(request, 'zarinpal/Transaction-messages.html', {'status':str(result.Status), 'message':message})


