from django.urls import path

from .views import ProductViewSet


urlpatterns = [
    path("create/", ProductViewSet.as_view({"post": "create"}), name="create_product"),
]
