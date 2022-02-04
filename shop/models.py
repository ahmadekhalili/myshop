from django.db import models
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, db_index=True, unique=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
            return self.name

    def get_absolute_url(self):
        return reverse('shop:product_list_by_category', args=[self.slug])

        
class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, db_index=True)
    description = models.TextField(blank=True)
    header = models.CharField(max_length=400)
    meta_title = models.TextField(blank=True, default='')
    meta_description = models.TextField(blank=True, default='')
    alt = models.CharField(max_length=200, blank=True, default='')
    price = models.DecimalField(max_digits=10, decimal_places=0)
    stock = models.PositiveIntegerField()
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ('-created',)
        index_together = (('id', 'slug'),)    #this statement,  will make fill slug just in input form, for example if in cmd you just point to name, without slug, slug will be blank!! in creation of object(so  do more tahghigh for index_together)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product_detail', args=[self.id, self.slug])
    def save(self, *args, **kwargs):
        if self.stock == 0:
            self.available = False
        else:
            self.available = True                           #supose product finished(available get False) and after sec, get ready, so when product get ready your product available will kept False  and you must True it handy whent ever product finished-ready,  if this statment wasnt.
        super(Product, self).save(*args, **kwargs)                     #if you use Product as parent(likke class A(Product)), so in class A if you use .save() this super(Prduct, self) in A, call parent of Product(instead parent of A) and keep conection to parent of Product(neccery for saving process)

class Images(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/%Y/%m/%d', blank=True)

    

