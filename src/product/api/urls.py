from django.urls import path

from .views import ProductViewSet


urlpatterns = [
    path("create/", ProductViewSet.as_view({"post": "create"}), name="create_product"),
    path("details/<int:pk>/", ProductViewSet.as_view({"get": "details"}), name="details_product"),
    path("update/<int:pk>/", ProductViewSet.as_view({"put": "update"}), name="update_product"),
]
