from django.db import models
from django.core.exceptions import ValidationError

from users.models import User
from shop.models import Product


def validate_postal_code(date):
    if len(date) != 10:
        raise ValidationError("کد پستي ده رقمي")
    
class Order(models.Model):
    user = models.ForeignKey(User, related_name='orders', on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    address = models.CharField(max_length=250)
    postal_code = models.CharField(max_length=20, validators=[validate_postal_code])
    city = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)
    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return 'Order {}'.format(self.id)

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=0)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return '{}'.format(self.id)

    def get_cost(self):
        return self.price * self.quantity   
    
'''
class Order:         
    User                            in example akh we have field: orders that have all Order created with that User.
    OrderItems(like [1, 3, 5 ])     in foreign key field, we just save id(but django get and query that id and hands over to us that table/object)
    ProfileOrder(first_name, last_name, email, address, postal_code, city)
    create
    update
    paid
#order has paid, means after completing every buying process  <order object>.paid should be True (customer paided), so for every buying we must create an order (to show us that buy has paided or not!) but problem is:
#in Order, instead of saving address, name, address, postal_code.... of Order in database in every buying , (that this fields is same in every Order) we implement this fields on OrderProfle so because of that,    address, name, postal_code .... just saved in database in limited number(for example <OrderProfile (1)>) and for every order we created for example Order1, Order2, Order4.. we just referec to OrderProfile1 and so we just create one time this fields(address, name..) in multiple Orders.
create, update, paid must explicity defind for Order
'''
