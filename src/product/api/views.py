import os
import json
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from product.models import ProductImage, Variant, ProductVariant
from .serializers import (
    ProductSerializer,
    ProductVariantSerializer,
    ProductVariantPriceSerializer,
)


class ProductViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]
    http_method = ["POST"]

    def create(self, request):
        product_details_data = json.loads(request.data.get("product_details"))
        product_image_data = request.data.get("product_image")
        product_variants_data = json.loads(request.data.get("product_variants"))
        product_variant_prices_data = json.loads(
            request.data.get("product_variant_prices")
        )

        # Save Product
        product_serializer = ProductSerializer(data=product_details_data)
        product_serializer.is_valid(raise_exception=True)
        product = product_serializer.save()

        # Save ProductImage
        if product_image_data:
            # Save image to FileSystemStorage and get the file path
            image_save_location = os.path.join(settings.MEDIA_ROOT, "product-image/")
            # Initialize FileSystemStorage with the target folder
            fs = FileSystemStorage(location=image_save_location)
            filename = fs.save(f"{product_image_data.name}", product_image_data)
            saved_image_path = settings.MEDIA_URL + filename

            # Create ProductImage instance
            product_image = ProductImage(file_path=saved_image_path)
            product_image.product = product
            product_image.save()

        # Save ProductVariants
        if product_variants_data:
            for variant_data in product_variants_data:
                variant_title_list = variant_data.get("tags", [])
                option_id = variant_data.get("option")

                variant_object = Variant.objects.filter(id=option_id).first()

                if variant_object:
                    for variant_title in variant_title_list:
                        variant_data = {
                            "variant_title": variant_title,
                            "variant": variant_object.id,
                            "product": product.id,
                        }

                        variant_serializer = ProductVariantSerializer(data=variant_data)
                        variant_serializer.is_valid(raise_exception=True)
                        variant_serializer.save()

        # Save Product Variant Prices
        if product_variant_prices_data:
            for product_variant_price_data in product_variant_prices_data:
                variants = product_variant_price_data.get("title").split("/")
                variants = variants[: len(variants) - 1]
                price = product_variant_price_data.get("price")
                stock = product_variant_price_data.get("stock")

                product_variant_price_instance_data = {
                    "price": price,
                    "stock": stock,
                    "product": product.id,
                }

                product_variant_price_type = [
                    "product_variant_one",
                    "product_variant_two",
                    "product_variant_three",
                ]

                for i, field_name in enumerate(product_variant_price_type):
                    variant_title = variants[i] if i < len(variants) else None
                    variant_obj = ProductVariant.objects.filter(
                        variant_title=variant_title
                    ).first()
                    product_variant_price_instance_data[field_name] = (
                        variant_obj.id if variant_obj else None
                    )

                product_variant_price_serializer = ProductVariantPriceSerializer(
                    data=product_variant_price_instance_data
                )
                product_variant_price_serializer.is_valid(raise_exception=True)
                product_variant_price_serializer.save()

        return Response({"message": "Product saved successfully"})
