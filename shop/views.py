from django.shortcuts import render, get_object_or_404, render_to_response
from datetime import datetime
from random import sample
from django.conf import settings
import ast

from .models import Category, Product
from .forms import IndexCartAddProductForm
from cart.forms import CartAddProductForm
from .categories_set import categories_tree, categories_tree_fa
from .product_selects_methods import random_products, bestSellingProducts, searchEngine, listProductByCat, products_main_cat, products_side_cat, listProductByPrice, ProductPriceBySelect, select_page, GET_made



def index(request):
    now = datetime.now()
    names = ['iPhone 8 Plus (Product) Red', 'V30s Thinq', 'Galaxy Note 9'] #special product lists 
    products = Product.objects.filter()
    vije_products = [products.get(name=name) for name in names]
    new_products = products[:12]  #in model.py, Product definded ordering by time
    best_selling = bestSellingProducts(Product.objects.all())[ :-5:-1] #-1 yani ro be aghab shomaresh kon list ra pas dar shoroee harekat, az akhar list shoro mikonad pas [ :-2:-1]yani az akhar list ta sare -2(khode shomare -2 nemishavad, pas akharin ozv ra midahad
    #we delete IndexCartAddProductForm because that form in loop prorduct many input fields that have same id natuarly like <input type="hidden" name="quantity" value="1" id="id_quantity"> that some id with same value is warning in chrome inspect/console.(supose 20 input point to one label!!!!)            
    return render(request, 'shop/product/index.html', {'now':now,                                    
                  'vije_products':vije_products,                                    
                  'new_products':new_products,
                  'best_selling':best_selling})



def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug) 
    related_products = random_products(product) #4 random products
    cart_product_form = CartAddProductForm(initial={'quantity':'1'})
    root = [(key,fa_key,L[0][1],L[0][0]) for key,fa_key in zip(categories_tree(), categories_tree_fa()) for L in categories_tree_fa()[fa_key] if L[0][1]==product.category.slug]              #product.category__slug is false here, it is for query is difference fro this(like related_query_name and related_name)for example: Product.objects.filter(category__slug=..)
    return render(request, 'shop/product/detail.html',
                  {'cart_product_form': cart_product_form,
                   'root': root[0],                                                     #root is like: [('phone', 'گوشی موبايل', 'samsung', 'سامسونگ')]
                   'product': product,
                   'related_products':related_products})


#popuse of here is optain and showing products, so for that we have two way: one, user send us category and we easy query and optain that product(like shop/categories/samsung/) and showing that to user. second if category=None and user dont send eny category?? how we find that products? it post to us in like url shop/categories/
#<form> here is like: <form action="{% url 'shop:product_list_by_category' %}" method="get">    form without action will default to current url and default method is get.
def product_selects_views(request,search_case=None): #if products=None, empty categories of products dont be shown.
    categoriesTreeFa = categories_tree_fa()             #we dont use categoriesTreeFa just for reading, (assigning, adding editing)   
    selector = None
    products = listProductByCat(request)[0]               #categories sidebar and categories menu     #categories sidebar,   {% cycle '1' '2' '3' '4' '5' '6' %} means you can defin six subject like:  گوشي موبايل           لپ تاپ           دوربين ديجيتال            هدفون رو گوشي و تو گوشی    ,  we cuold design somthing like cat0=samsung for cat menu, and cat0=samsung&cat1=lg for cat sidebar(that was mor logac) but samsung&lg have less character
    categoriesTreeFa = listProductByCat(request)[1]
    if search_case:
        products = searchEngine(search_case)
    
    if request.GET.get('mx'):              #price sidebar
        products = listProductByPrice(products, request)
        
    if request.GET.get('slct'):            #categories select,       
        if request.GET.get('slct')=='0':
            products = ProductPriceBySelect(products)            #sort by price(dropdown menu)
            selector = '0x'
        elif request.GET.get('slct')=='1':         
            products = ProductPriceBySelect(products) 
            if products:
                products = products[::-1]
            selector = '1x'
        elif request.GET.get('slct')=='2':
            products = bestSellingProducts(products)[::-1]         
            selector = '2x'
        elif request.GET.get('slct')=='3':
            selector = '3x'
       
    root = [(key,fa_key) for key,fa_key in zip(categories_tree(), categories_tree_fa()) if key in request.GET]       #if cant find eny thing, python comprehensive will assign [] to root.
    if not root:
        root = [(key,fa_key,L[0][1],L[0][0]) for key,fa_key in zip(categories_tree(), categories_tree_fa()) for L in categories_tree_fa()[fa_key] if L[0][1] in request.GET]              #product.category__slug is false here, it is for query is difference fro this(like related_query_name and related_name)for example: Product.objects.filter(category__slug=..)
    if not root:
        root = [None]
    
    prs_pgs_crnt_gr = select_page(products, request.GET.get('page'))                       #care request.GET will override in searchProduct and may lost some data!!! prs_pgs_crnt_gr=products_pages_current_group
    return  render(request,
                  'shop/product/category.html',
                  {'selector':selector,
                   'root':root[0],
                   'categoriesTreeFa':categoriesTreeFa,
                   'prs_pgs_crnt_gr':prs_pgs_crnt_gr,                   #important: if products is None, in template django ignore eny error raise related to products statement, for example if products=None and we have: {% for i in products %}{{product.name}}{% endfor %} so django dont raise iterator error for us and ignore that block completly, and for another example if {% for i in products %}<p>{{product.name}}</p>{% endfor %} and in view.py we have products=[1,2,3],  {{i.name}} dont raise error and django replace blank for that so <p></p> will print.
                   'GET':GET_made(request,search_case)})                   


def searchProduct(request):
    search_case2 = request.GET['search'] #use get because with post, when user refresh searched page, get error(post data lost but in get url isn ot lost and present in url)
    search_case = ''
    pr_letters = ['آ','ا','ب','پ','ت','ث','ج','چ','ح','خ','د','ذ','ر','ز','ژ','س','ش','ص','ض','ط','ظ','ع','غ','ف','ق','ک','گ','ل','م','ن','و','ه','ی'] #dont enter letters in python api(its words is arabic... and is incorect) i input in  setmark searchbar and then copy it in python.

    for i in search_case2:
        try:
            i.encode(encoding='ascii')
            search_case += i                
        except:
            if i in pr_letters:
                search_case += i
    if len(search_case)<50:
        return product_selects_views(request,search_case)     



def aboutUs(request):
    return render(request, 'shop/about-us.html')
