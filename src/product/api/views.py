import os
import json
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from product.models import (
    Product,
    ProductImage,
    Variant,
    ProductVariant,
    ProductVariantPrice,
)
from .serializers import (
    ProductSerializer,
    ProductVariantSerializer,
    ProductVariantPriceSerializer,
)


class ProductViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

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

    @action(detail=True, methods=["get"])
    def details(self, request, pk=None):
        product = Product.objects.filter(id=pk).first()
        if not product:
            return Response({"error": "Product not found"}, status=400)

        data = {}
        data["product_details"] = ProductSerializer(product).data

        # Format product variant data for display update page
        variants = product.productvariant_set.values_list(
            "variant__id", flat=True
        ).distinct()
        product_variants = []
        for variant in variants:
            tags = product.productvariant_set.filter(variant__id=variant).values_list(
                "variant_title", flat=True
            )
            product_variants.append({"option": variant, "tags": tags})

        data["product_variants"] = product_variants

        # Format product variant price data for display update page
        product_variant_price_data = []
        product_variant_prices = product.productvariantprice_set.all()
        for product_variant_price in product_variant_prices:
            title = ""
            if product_variant_price.product_variant_one:
                title = f"{product_variant_price.product_variant_one.variant_title}/"
            if product_variant_price.product_variant_two:
                title = (
                    title
                    + f"{product_variant_price.product_variant_two.variant_title}/"
                )
            if product_variant_price.product_variant_three:
                title = (
                    title
                    + f"{product_variant_price.product_variant_three.variant_title}/"
                )

            product_variant_price_data.append(
                {
                    "title": title,
                    "price": product_variant_price.price,
                    "stock": product_variant_price.stock,
                }
            )

        data["product_variant_prices"] = product_variant_price_data

        return Response(data)

    def update(self, request, pk=None):
        product = Product.objects.get(pk=pk)

        if not product:
            return Response({"error": "Product not found"}, status=400)

        # Update Product Details
        product_details_data = json.loads(request.data.get("product_details"))
        product_serializer = ProductSerializer(
            instance=product, data=product_details_data
        )
        product_serializer.is_valid(raise_exception=True)
        product_serializer.save()

        # Save Product Image
        product_image_data = request.FILES.get("product_image")
        if product_image_data:
            # Save image to FileSystemStorage and get the file path
            image_save_location = os.path.join(settings.MEDIA_ROOT, "product-image/")
            # Initialize FileSystemStorage with the target folder
            fs = FileSystemStorage(location=image_save_location)
            filename = fs.save(f"{product_image_data.name}", product_image_data)
            saved_image_path = settings.MEDIA_URL + filename

            # If already exists then update otherwise create new one
            existing_image = ProductImage.objects.filter(product=product).first()
            if existing_image:
                existing_image.file_path = image_save_location
            else:
                product_image = ProductImage(file_path=saved_image_path)
                product_image.product = product
                product_image.save()

        # Update Product Variants
        product_variants_data = json.loads(request.data.get("product_variants"))
        ProductVariant.objects.filter(product=product).delete() # Delete Previous data

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

        # Update Product Variant Prices
        product_variant_prices_data = json.loads(
            request.data.get("product_variant_prices")
        )
        ProductVariantPrice.objects.filter(product=product).delete() # Delete Previous data

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
                    variant_title=variant_title, product=product
                ).first()
                product_variant_price_instance_data[field_name] = (
                    variant_obj.id if variant_obj else None
                )

            product_variant_price_serializer = ProductVariantPriceSerializer(
                data=product_variant_price_instance_data
            )
            product_variant_price_serializer.is_valid(raise_exception=True)
            product_variant_price_serializer.save()

        return Response({"message": "Product updated successfully"})
