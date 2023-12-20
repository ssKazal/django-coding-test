from django.urls import include, path

from product.views.product import CreateProductView, ProductListView
from product.views.variant import VariantView, VariantCreateView, VariantEditView

app_name = "product"

urlpatterns = [
    # Variants URLs
    path("variants/", VariantView.as_view(), name="variants"),
    path("variant/create", VariantCreateView.as_view(), name="create.variant"),
    path("variant/<int:id>/edit", VariantEditView.as_view(), name="update.variant"),

    # Products URLs
    path("create/", CreateProductView.as_view(), name="create.product"),
    path('update/<int:product_id>/', CreateProductView.as_view(), name='update.product'),
    path("list/", ProductListView.as_view(), name="list.product"),

    # Api URLs
    path("api/", include(("product.api.urls", "product"), namespace="api")),
]
