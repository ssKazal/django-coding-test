from rest_framework import serializers
from product.models import Product, ProductImage, ProductVariant, ProductVariantPrice


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "title", "sku", "description"]


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "product", "file_path"]


class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ["id", "variant_title", "variant", "product"]


class ProductVariantPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariantPrice
        fields = [
            "id",
            "product_variant_one",
            "product_variant_two",
            "product_variant_three",
            "price",
            "stock",
            "product",
        ]
