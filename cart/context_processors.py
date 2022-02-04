from .cart import Cart
from shop.categories_set import categories_tree


def cart(request):
    path = request.path.replace('/','@')                                  #path used in header.html. header.html is file that used in most page(by {% include 'shop/header.html' %}) so it is not only for one specific view(that we difend it in render fun of that view), so it need defind in contect_procesor.  in func cart_remove we have one variable (path) that is like:@cart@ that optain from header.html link that user click so if path variable was somthig like its original like /cart/ eny slash in url was one seperate url and we cant save serveral url on one variable(path) so in future if we want add more complicate pages that have this remove button, we see problem
    return {'cart':Cart(request),
            'path':path,
            'categories_tree':list(categories_tree().items())}                          #used in header.html
