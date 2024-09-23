from rest_framework import serializers 
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from .models import MenuItem, Category, Cart, Order, OrderItem
from django.contrib.auth.models import User
import bleach



class UserSerializer(serializers.ModelSerializer):
    class Meta: 
        model = User 
        fields = '__all__'

class DeliveryCrewSerializer(serializers.ModelSerializer): 
    class Meta: 
        model = User
        fields = '__all__'
        
class CategorySerializer(serializers.ModelSerializer):
    class Meta: 
        model = Category 
        fields = ['id', 'title']


class MenuItemSerializer(serializers.ModelSerializer):
    #price = serializers.DecimalField(max_digits=6, decimal_places=2, min_value=2)
    
    category_id = serializers.IntegerField(write_only=True)
    category = CategorySerializer(read_only=True)
    
    #def validate(self,attrs):
    #    attrs['title'] = bleach.clean(attrs['title'])
    #    if (attrs['price'] < 2 ): 
    #        raise serializers.ValidationError('Price should not be less than 2.00')
    #    if (attrs['inventory']<0):
    #        raise serializers.ValidationError('Stock cannot be negative')
    #    return super().validate(attrs)
    
    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.price = validated_data.get('price', instance.price)
        instance.category_id = validated_data.get('category_id', instance.category_id)
        instance.featured = validated_data.get('featured', instance.featured)
        instance.save()
        return instance 
        
    class Meta:
        model = MenuItem 
        fields = [ 'id', 'title', 'price', 'featured', 'category', 'category_id' ]
        depth = 1
        #validators = [
        #    UniqueTogetherValidator(
        #        queryset=MenuItem.objects.all(),
        #        fields=['title', 'price']
        #    )
        #]
        
        extra_kwargs = { 
                       'title' : {
                           'validators': [
                               UniqueValidator(
                                   queryset=MenuItem.objects.all()
                               )
                           ]
                       },
                       'price': { 'min_value': 2}, 
                    #   'inventory': { 'min_value': 0},
        }
        
class CartSerializer(serializers.ModelSerializer):
    menuitem_id = serializers.IntegerField()
    menuitem = MenuItemSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True, required =True)
    user = UserSerializer(read_only=True)
    
    class Meta: 
        model = Cart 
        fields = ['id', 'user_id', 'user', 'menuitem_id', 'menuitem', 'quantity', 'unit_price', 'price']
        depth = 1
        
class OrderSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(write_only=True)
    user = UserSerializer(read_only=True)
    delivery_crew_id = serializers.IntegerField(write_only=True)
    delivery_crew = DeliveryCrewSerializer(read_only=True, required=False)
    status = serializers.BooleanField(required=False)
    
    def update(self, instance, validated_data):
        instance.delivery_crew_id = validated_data.get('delivery_crew_id', instance.delivery_crew_id)
        instance.status = validated_data.get('status', instance.status)
        instance.user_id = validated_data.get('user_id', instance.user_id)
        instance.save()
        return instance 
    
    class Meta:
        model = Order
        fields = ['id', 'user', 'user_id', 'delivery_crew_id', 'delivery_crew', 'status', 'total', 'date']

class OrderItemsSerializer(serializers.ModelSerializer):
    order = OrderSerializer(read_only=True)
    order_id = serializers.IntegerField(write_only=True)
    menuitem_id = serializers.IntegerField(write_only=True)
    menuitem = MenuItemSerializer(read_only=True)
    
    
    
    class Meta: 
        model = OrderItem 
        fields = ['id', 'order', 'order_id', 'menuitem', 'menuitem_id', 'quantity', 'unit_price', 'price']
        depth = 1
    