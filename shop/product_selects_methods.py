from django.shortcuts import get_object_or_404
from random import sample
import ast

from .models import Product, Category
from orders.models import Order, OrderItem
from .categories_set import categories_tree, categories_tree_fa, categories_tree_reverse, categories_tree_searches, fullcats_list


#return some products that related to product argument.
def random_products(product):
    category_tree = categories_tree()
    reverse_tree = categories_tree_reverse()
    L = [i for i in category_tree[reverse_tree[product.category.slug]]]#list of category slugs related to protect.example product:lg L=[all categories related to phone]
    related_products = Product.objects.filter(category__slug__in=L)
    try:
        products_random = sample(list(related_products), 4)
    except:
        products_random = product
    try:
        iter(products_random)
    except:
        products_random = [products_random]
    return products_random


#return list like[quantity, product] sorted by its sells(low to hight)    
def bestSellingProducts(products=None):                                    #for optimizing we can do this function work in periodicly times and saves resault(in hard(server)), so if 2 prodoct added in our site we dont run this func and serch 1 milion products again, we just serch and update this 2 prodoct against other 1 milion product. so serching periodic sims better than, every user request get and search 1 bilios again and user wait for you!!!!
    quantities = 0
    LL = []
    if not products:     #products=None
        return None
    for product in products:
        quantities = 0
        for orderitem in product.order_items.all():
            quantities += orderitem.quantity
        LL.append([quantities, product.id])
    LL.sort() #sort by using first element of list(quantities) from low to hight.
    L = []
    for i in LL:
        L.append(Product.objects.get(id=i[1]))      
    return L

    
def searchEngine(search_case):
    products = []
    products_searched = []
    roots = [(key,categories_tree_searches()[key]) for key in categories_tree_searches()]                #like: [('phone', ['گوشي', 'موبايل', 'تلفن']), ('laptop', ['لپ تاپ', 'لب تاپ'])]
    cats = [(L[0][0],L[0][1]) for key in categories_tree_fa() for L in categories_tree_fa()[key]]        #like:[('ال جي','lg'), ..]             

    for root in roots:                                 #search_case that will return from this func: search_case='phone' or 'تلفن' or 'ال جي' or 'lg' will return products. roots is smaller than cats so its beter roots process first.
        if root[0]==search_case:            
            for cat in categories_tree()[root[0]]:
                products += Product.objects.filter(category__slug=cat)
            return products            
        for i in root[1]:
            if i==search_case: 
                for cat in categories_tree()[root[0]]:
                    products += Product.objects.filter(category__slug=cat)                
                return products
    
    for L in cats:
        if L[0]==search_case or L[1]==search_case:
            products = Product.objects.filter(category__slug=L[1])
            return products
        
#befor here is for single-word serach_cases that directly point to main cat or sub cat(en or pr)
    mark1, mark2 = '', ''
    for L in cats:                                                                #example: search_case='phoneasd' or 'تلفن شسي' or 'گوشي ال جي' or 'lg g5 red 64gig' will fill products for after processing.  in here cats has priority to roots(unlike previous), sopuse statement like:گوشي موبايل so موبايل should process first instead of گوشي
        if L[0] in search_case:                           #here search_case in L[0] dont means, supose user type "ا", so here is: 'ا' in 'ال جي' will return true!!!            
            products = Product.objects.filter(category__slug=L[1])
            mark = L[0]
        elif L[1] in search_case:
            products = Product.objects.filter(category__slug=L[1])
            mark = L[1]            
    if not products:                                        
        for root in roots:                                 
            if root[0] in search_case:        #english root
                for cat in categories_tree()[root[0]]:
                    products += Product.objects.filter(category__slug=cat)
                    mark2 = root[0]
            if not products: 
                for i in root[1]:            #that root, in its persian(for example if root[0]='phone'here we search in root[1]=['گوشي', 'موبايل', 'تلفن'](scope is true)
                    if i in search_case:
                        mark2 = i
                        for cat in categories_tree()[root[0]]:
                            products += Product.objects.filter(category__slug=cat)
                            
    if not products:
        products = Product.objects.all()
        products_searched = None
    else:
        products_searched = list(products)               #products_searched=products is query set and have not .index or otherthing!!if we used products for editing or changig in below, we must use here products.copy()
        if mark1:
            search_case = search_case.replace(mark1, '')
        if mark2:
            search_case = search_case.replace(mark2, '')
    L1, L2 = [], []
    for product in products:
        i = 0
        for search_case_word in search_case.lower().split():                    #lower() for pr characters dont raise error(skip it).
            if search_case_word in product.name.lower() or search_case_word in product.category.slug:             #search_case_word in product.category.slug is like: sa in samsung           
                i+= 1
        if i>0:
            L1.append(product)
            L2.append(i)
    if not L1:
        for product in products:
            i = 0
            for search_case_word in search_case.lower().split():                    #lower() for pr characters dont raise error(skip it).
                if search_case_word in product.header.lower():               
                    i+= 1
            if i>0:
                L1.append(product)
                L2.append(i)
    if L1:
        L2_maxes_index, j, mx = [], -1, max(L2)
        for i in L2:
            j +=1
            if i == mx:
                L2_maxes_index.append(j)     
    if products_searched and L1:
        products = [L1[index] for index in L2_maxes_index]
        for product in products:
            if product not in products_searched:
                products_searched = [product, *products_searched]
            else:                              #if one product searched and assign to products_searched, and in some line lower again product searched and assign to L1[max] so this product has 2 priority and sure it is our best choice and must be first item in out list.(it chicen 2 time)
                del products_searched[products_searched.index(product)]          
                products_searched = [product, *products_searched]
    elif L1:
        products = [L1[index] for index in L2_maxes_index]
        products_searched = [*products]    #products_searched must be list
    return products_searched


def products_main_cat(request):
    cat_tree = categories_tree()
    cat_tree_fa = categories_tree_fa() 
    products=[]
    for key in cat_tree:
        if key in request.GET:
            for cat in cat_tree[key]:
                category = get_object_or_404(Category, slug=cat)
                products += Product.objects.filter(category=category)
                for key in cat_tree_fa:
                    for L in cat_tree_fa[key]:
                        if L[0][1] == cat:
                            L[1]=cat
    return (products,cat_tree_fa)                            

def products_side_cat(request):
    products = []
    categories_tree_f = categories_tree_fa()    
    for key in categories_tree_f:
        for touple_counter in categories_tree_f[key]:
            if touple_counter[0][1] in request.GET:
                products += Product.objects.filter(category__slug=touple_counter[0][1])
                touple_counter[1] = touple_counter[0][1]
    return (products, categories_tree_f)    

def listProductByCat(request):                            #products_side_cat + products_main_cat
    p = products_main_cat(request)
    if p[0]:
        return p
    return products_side_cat(request)


def listProductByPrice(products, request=None):            #you cant put request=None first. see: https://stackoverflow.com/questions/24719368/syntaxerror-non-default-argument-follows-default-argument/39942121
    if request.GET.get('mn'):                      #list by ranged price
        mn, mx = int(request.GET['mn']), int(request.GET['mx'])    #product by ranged price
        if products:
            return [product for product in products if product.price>=mn and product.price<=mx]            
        else:
            products = None
            

def ProductPriceBySelect(products, request=None):            #you cant put request=None first. see: https://stackoverflow.com/questions/24719368/syntaxerror-non-default-argument-follows-default-argument/39942121                     
    if products:
        price_id = [[product.price, product.id] for product in products]
        price_id.sort()     
        products = [Product.objects.get(id=i[1]) for i in price_id]          #products in argument will change with this statement, but sims this dont heart, because in next call func listProductByPrice we assign another prodoct and also we dont use default for example products=None           
        return products
    else:
        return None


#return (prouct of that page user want, number of pages, current page number)
def select_page(products, page):
    if products!=None and len(products)>12:                #if products=None,this statment: if len(products)>=12 will raise error.   in regular url like http://127.0.0.1:8000/shop/categories/phone/ page=None
        page = int(page) if page else 1
        
        products2=[]
        page_numbers = len(products)//12+1 if len(products)%12!=0 else len(products)//12            #for example if len(products)=23 pages=2 and if len(products)=24 pages=2
        page_pocket = page//5+1 if page%5!=0 else page//5               #current page_pocket                                       #masalan agar page 7 bashad, page_pocket=2 ke yani ma dar dovomin packat as paghaieman hastim.(packet: page 5 taii)
        if page_numbers>page_pocket*5 and page_pocket>1:                                            #for example supose user is in page=7 and  page_numbers=8(all our pages), so we dont need to gouping to next(11 to 15).    page_pocket must above 1 to dont apear problem in:(page_pocket-1)*5-1.
            group = [(page_pocket-1)*5, page_pocket*5+1]                                          #example,  page=13 so page_pocket=3, so for next target we must driven to page:16 and for previous,  page:9
            pages = range(group[0]+1, group[1])                                                   #from group[0]+1 to group[1]-1 but care in range last doont process sogroup[1]-1+1
        elif page_numbers>page_pocket*5:        
            group = [1, 6]
            pages = range(1, group[1])
        elif page_pocket>1:                                  #our last page for example in under 16 and so need to just backwarding(like from page 13 going to 9) but dont need going next(page 16)            
            group = [(page_pocket-1)*5, page_numbers]
            pages = range(group[0]+1, page_numbers+1)
        else:
            group = ["", ""]                                 #need to don go anywhere(blank links)
            pages = range(1, page_numbers+1)
        p = page*12
        for i in range(p-12,p):                              #example: page:2 p:24 range(12,24)(12 to 23)
            try:
                products2.append(products[i])
            except:
                return (products2, pages, page, group)        #supose user want page 2 and we have 14 product so in for i in range(12, 23): after 2 loop(12, 13) our product will end and for example products[14] will error.
        return (products2, pages, page, group)       #page_numbers:2 so loop 1,2 that implement with range(1,3)       

    else:
        return (products, 0, None, ["", ""])                  #group is not defind in this scope!!!  (we dont display eny pages button when products in under 12)


def GET_made(request,search_case):                                                         #important: get['cat'] is for category selected from main menu or sidebar.   get['select_cat']  is for <select> that is for besselling,newest.... and this field needs data from  get['cat'] and get['price_side'] but, get['price_side'] that used for price side  and  note note this price side bar only need data get['cat'] (and dont need select data(get['select_cat'])) and in last, pages that need all datas(cat, select, and price side)    
    get = {}
    get['cat'] = [cat for cat in fullcats_list() if cat in request.GET]                                   #for example: get['side_cat'] in http://127.0.0.1:8000/shop/categories/?phone=  is ['phone']  and in: http://127.0.0.1:8000/shop/categories/?samsung= is like:  ['samsung']
    get['select_cat'] = request.GET['slct'] if request.GET.get('slct') else ''                            #0    1     2    3
    get['side_price'] =  [request.GET['mx'],request.GET['mn']] if request.GET.get('mn')!=None else ''      #request.get come from side_price is somthing like(max in first): <QueryDict: {'mx': ['10000000'], 'mn': ['0']}>          if request.GET.get('mn') is encorect because when mn is 0 will egnore this statement.
    get['search'] = search_case if search_case else ''
    return get                                                                                       



