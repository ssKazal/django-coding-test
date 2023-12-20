from django.views import generic
from django.db.models import Q

from product.models import Product, ProductVariant, Variant


class CreateProductView(generic.TemplateView):
    template_name = "products/create.html"

    def get_context_data(self, **kwargs):
        context = super(CreateProductView, self).get_context_data(**kwargs)
        variants = Variant.objects.filter(active=True).values("id", "title")
        context["product"] = True
        context["variants"] = list(variants.all())

        # If updating an existing product, pass the product ID to the template
        product_id = self.kwargs.get("product_id")
        context["product_id"] = product_id
        return context


class ProductListView(generic.ListView):
    template_name = "products/list.html"
    model = Product
    context_object_name = "products"
    paginate_by = 5  # Set the number of items per page

    def get_queryset(self):
        queryset = Product.objects.all()

        title = self.request.GET.get("title")
        variant = self.request.GET.get("variant")
        price_from = self.request.GET.get("price_from")
        price_to = self.request.GET.get("price_to")
        date = self.request.GET.get("date")

        # Apply filters to queryset based on form inputs
        if title:
            queryset = queryset.filter(title__icontains=title)

        if variant:
            queryset = queryset.filter(productvariant__variant_title=variant).distinct()
            print(queryset)

        if price_from:
            queryset = queryset.filter(
                Q(productvariantprice__price__gte=float(price_from))
            ).distinct()

        if price_to:
            queryset = queryset.filter(
                Q(productvariantprice__price__lte=float(price_to))
            ).distinct()

        if date:
            queryset = queryset.filter(created_at__date=date).distinct()

        return queryset

    def get_context_data(self, **kwargs):
        context = super(ProductListView, self).get_context_data(**kwargs)

        # Get distinct product variant titles for each variant
        variant_titles_by_variant = {}
        for variant in Variant.objects.all():
            variant_titles = (
                ProductVariant.objects.filter(variant=variant)
                .values_list("variant_title", flat=True)
                .distinct()
            )
            variant_titles_by_variant[variant.title] = variant_titles

        context["variant_titles_by_variant"] = variant_titles_by_variant

        return context
