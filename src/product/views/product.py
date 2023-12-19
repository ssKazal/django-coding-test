from django.views import generic

from product.models import Product, Variant


class CreateProductView(generic.TemplateView):
    template_name = "products/create.html"

    def get_context_data(self, **kwargs):
        context = super(CreateProductView, self).get_context_data(**kwargs)
        variants = Variant.objects.filter(active=True).values("id", "title")
        context["product"] = True
        context["variants"] = list(variants.all())
        return context


class ProductListView(generic.ListView):
    template_name = "products/list.html"
    model = Product
    context_object_name = 'products'
    paginate_by = 5  # Set the number of items per page

    def get_queryset(self):
        return Product.objects.all()
