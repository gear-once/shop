from django.shortcuts import render
from .models import OrderItem, Order
from .forms import OrderCreateForm
from cart.cart import Cart
from django.shortcuts import redirect, get_object_or_404

from django.contrib.admin.views.decorators import staff_member_required

from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa


def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        if len(cart) > 0:
            form = OrderCreateForm(request.POST)
            if form.is_valid():

                order = form.save()
                for item in cart:
                    OrderItem.objects.create(order=order,
                                             product=item['product'],
                                             price=item['price'],
                                             quantity=item['quantity'])
                # clear the cart
                cart.clear()

        else:
            return redirect("/")

        return render(request,
                      'orders/order/created.html',
                      {'order': order})
    else:
        form = OrderCreateForm()
    return render(request,
                  'orders/order/create.html',
                  {'cart': cart, 'form': form})


@staff_member_required
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request,
                  'admin/orders/order/detail.html',
                  {'order': order})


def render_pdf_view(request, order_id):
    template_path = 'orders/order/pdf.html'
    order = get_object_or_404(Order, id=order_id)
    context = {'order': order}
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename=order_{order.id}.pdf'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
        html, dest=response)
    # if error then show some funny view
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response
