from django.contrib import admin
from .models import Category, Product, Images


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug':('name',)}

class ImagesInline(admin.TabularInline):
    model = Images
    extra = 4
    
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'category', 'price', 'stock', 'available', 'created','updated']   #'images' must not be here(error)
    list_filter = ['available', 'created', 'updated', 'category__name']
    list_editable = ['price', 'stock', 'available']
    prepopulated_fields = {'slug':('name',)}
    inlines = [ImagesInline]
    
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Images)
