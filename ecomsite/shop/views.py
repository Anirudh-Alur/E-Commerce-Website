from django.shortcuts import render, redirect
from .models import Products,Order
from django.contrib import messages
from django.core.paginator import Paginator
# Create your views here.
 
def index(request):
    product_objects = Products.objects.all()
 
    #search code
    item_name = request.GET.get('item_name')
    if item_name != '' and item_name is not None:
        product_objects = product_objects.filter(title__icontains=item_name)
 
    #paginator code
    paginator = Paginator(product_objects,4)
    page = request.GET.get('page')
    product_objects = paginator.get_page(page)
    
    return render(request,'shop/index.html',{'product_objects':product_objects})
 
 
def detail(request,id):
    product = Products.objects.get(id=id)
    return render(request,'shop/detail.html',{'product' :product})
    
# shop/views.py

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Order

def checkout(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zipcode = request.POST.get('zipcode')
        items = request.POST.get('items')
        total = request.POST.get('total')

        order = Order(
            name=name,
            email=email,
            phone=phone,
            address=address,
            city=city,
            state=state,
            zipcode=zipcode,
            items=items,
            total=total
        )
        order.save()
        
        # ✅ Clear cart after order
        request.session['cart'] = {}
        
        return redirect('order_success')  # redirect to success view

    return render(request, "shop/checkout.html")


def order_success(request):
    return render(request, "shop/success.html")
