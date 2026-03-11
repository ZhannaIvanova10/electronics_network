from rest_framework import serializers
from .models import NetworkNode, Contact, Product

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'email', 'country', 'city', 'street', 'house_number']

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'model', 'release_date']

class NetworkNodeSerializer(serializers.ModelSerializer):
    contact = ContactSerializer()
    products = ProductSerializer(many=True, read_only=True)
    product_ids = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=Product.objects.all(),
        source='products',
        write_only=True
    )
    supplier_id = serializers.PrimaryKeyRelatedField(
        queryset=NetworkNode.objects.all(),
        source='supplier',
        allow_null=True,
        required=False
    )

    class Meta:
        model = NetworkNode
        fields = [
            'id', 'name', 'level', 'contact', 'products', 'product_ids',
            'supplier_id', 'debt', 'created_at'
        ]
        read_only_fields = ['debt', 'created_at', 'level']

    def create(self, validated_data):
        contact_data = validated_data.pop('contact')
        products_data = validated_data.pop('products', [])
        
        contact = Contact.objects.create(**contact_data)
        network_node = NetworkNode.objects.create(contact=contact, **validated_data)
        network_node.products.set(products_data)
        
        return network_node
    def update(self, instance, validated_data):
        contact_data = validated_data.pop('contact', None)
        products_data = validated_data.pop('products', None)
        
        if contact_data:
            contact_serializer = ContactSerializer(instance.contact, data=contact_data)
            if contact_serializer.is_valid():
                contact_serializer.save()
        
        if products_data is not None:
            instance.products.set(products_data)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance
