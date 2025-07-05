from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.http import HttpResponse, Http404, FileResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from .models import Products, Order
import json
import uuid
import os


def index(request):
    product_objects = Products.objects.all()

    # Search
    item_name = request.GET.get('item_name')
    if item_name:
        product_objects = product_objects.filter(title__icontains=item_name)

    # Pagination
    products = Products.objects.all().order_by('id')
    paginator = Paginator(product_objects, 4)
    page = request.GET.get('page')
    product_objects = paginator.get_page(page)

    return render(request, 'shop/index.html', {'product_objects': product_objects})


def detail(request, id):
    product = get_object_or_404(Products, id=id)
    return render(request, 'shop/detail.html', {'product': product})


def generate_pdf(template_src, context_dict, filename):
    template = get_template(template_src)
    html = template.render(context_dict)
    filepath = os.path.join("media/invoices", filename)

    # Ensure directory exists
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, "wb") as f:
        pisa_status = pisa.CreatePDF(html, dest=f)
    return pisa_status.err == 0, filepath


def checkout(request):
    if request.method == "POST":
        # Get all form data
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zipcode = request.POST.get('zipcode')
        items_json = request.POST.get('items')
        total = float(request.POST.get('total') or 0)

        # Save order
        order = Order(
            name=name,
            email=email,
            phone=phone,
            address=address,
            city=city,
            state=state,
            zipcode=zipcode,
            items=items_json,
            total=total
        )
        order.save()

        # Generate PDF filename
        filename = f"invoice_{uuid.uuid4().hex}.pdf"
        items = json.loads(items_json)

        cart_items = []
        for item_id, details in items.items():
            cart_items.append({
                'name': details[1],
                'quantity': details[0],
                'unit_price': details[2],
                'total_price': details[3],
            })

        context = {
            'order': order,
            'cart_items': cart_items,
        }

        # Generate and save PDF
        success, filepath = generate_pdf('shop/order_invoice.html', context, filename)
        if success:
            pdf_url = f"/media/invoices/{filename}"
        else:
            pdf_url = None

        # Clear the cart session
        request.session['cart'] = {}

        return render(request, 'shop/success.html', {'order': order, 'pdf_url': pdf_url})

    return render(request, 'shop/checkout.html')


def order_success(request):
    return render(request, "shop/success.html")


def generate_invoice(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        raise Http404("Order not found")

    items = json.loads(order.items)

    cart_items = []
    for item_id, details in items.items():
        cart_items.append({
            'name': details[1],
            'quantity': details[0],
            'unit_price': details[2],
            'total_price': details[3],
        })

    context = {
        'order': order,
        'cart_items': cart_items,
    }

    filename = f"invoice_{order_id}.pdf"
    filepath = os.path.join("media/invoices", filename)

    # Create directory if missing
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    # Generate PDF if it doesn't exist
    if not os.path.exists(filepath):
        success, _ = generate_pdf('shop/order_invoice.html', context, filename)
        if not success:
            return HttpResponse("Error generating invoice PDF.", status=500)

    # Serve the PDF file
    return FileResponse(open(filepath, 'rb'), content_type='application/pdf')
