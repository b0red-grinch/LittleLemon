'''
from django.shortcuts import render

from django.db import IntegrityError

from .models import Book
from django.views.decorators.csrf import csrf_exempt



from rest_framework import status 
from rest_framework.decorators import api_view
from rest_framework.views import APIView
'''

from django.http import JsonResponse
from django.forms.models import model_to_dict

from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response 
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.decorators import api_view, renderer_classes
from .models import MenuItem, Category, Cart, Order, OrderItem
from .serializers import MenuItemSerializer, CategorySerializer, CartSerializer, OrderSerializer, OrderItemsSerializer
from django.core.paginator import Paginator, EmptyPage
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import permission_classes, throttle_classes
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from .throttles import TenCallsPerMinute

from django.contrib.auth.models import User, Group


@api_view()
@renderer_classes([TemplateHTMLRenderer])
def menu(request): 
    items = MenuItem.objects.all()
    serialized_item = MenuItemSerializer(items, many=True)
    return Response({'data': serialized_item.data}, template_name='menu-items.html')

#class MenuItemView(generics.ListCreateAPIView):
#    queryset = MenuItem.objects.all()
#    serializer_class = MenuItemSerializer

class SingleMenuItemView(generics.RetrieveUpdateAPIView, generics.DestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle, AnonRateThrottle])
def menu_items(request):
    if (request.method =='GET'):
        items = MenuItem.objects.select_related('category').all()
        category_name = request.query_params.get('category')
        to_price = request.query_params.get('to_price')
        search = request.query_params.get('search')
        ordering = request.query_params.get('ordering')
        perpage = request.query_params.get('perpage', default=2)
        page = request.query_params.get('page', default=1)
        if category_name:
            items = items.filter(category__title=category_name)
        if to_price: 
            items = items.filter(price__lte=to_price)
        if search:
            items = items.filter(title__startswith=search)
        if ordering: 
            ordering_fields = ordering.split(",")
            items = items.order_by(*ordering_fields)
        paginator = Paginator(items,per_page=perpage)
        try: 
            items = paginator.page(number=page)
        except EmptyPage:
            items = []
        serialized_item = MenuItemSerializer(items, many=True)
        return Response(serialized_item.data)
    
    
    elif request.method == 'POST': 
        if request.user.has_perm("littlelemonAPI.add_menuitem"):
            serialized_item = MenuItemSerializer(data = request.data)
            serialized_item.is_valid(raise_exception=True)
            serialized_item.save()
            return Response(serialized_item.validated_data, status.HTTP_201_CREATED)
        return Response("Only Managers can create items", status.HTTP_403_FORBIDDEN)

@api_view(['GET', 'PUT', 'DELETE','PATCH'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle, AnonRateThrottle])
def single_item(request, pk):
    item = get_object_or_404(MenuItem, pk=pk)
    if request.method == 'GET':
        serialized_item = MenuItemSerializer(item)
        return Response(serialized_item.data)
    
    elif request.method == 'POST':
        if request.user.has_perm("littlelemonAPI.add_menuitem"):
            serialized_item = MenuItemSerializer(data = request.data)
            serialized_item.is_valid(raise_exception=True)
            serialized_item.save()
            return Response(serialized_item.validated_data, status.HTTP_201_CREATED)
        return Response("Forbidden", status.HTTP_403_FORBIDDEN)
    
    elif request.method == 'PUT' or 'PATCH':
        if request.user.has_perm("littlelemonAPI.change_menuitem"):
            serialized_data = MenuItemSerializer(item, data = request.data)
            serialized_data.is_valid(raise_exception=True)
            serialized_data.save()
            return Response(serialized_data.data, status.HTTP_201_CREATED)
        return Response("Forbidden", status.HTTP_403_FORBIDDEN)

    elif request.method == 'DELETE':
        if request.user.has_perm("LittlelemonAPI.delete_menuitem"):
            item.delete()
            return Response("deleted",status.HTTP_200_OK)
        else: 
            return Response("Only Managers can delete a menu item", status.HTTP_403_FORBIDDEN)
            
class CategoriesView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer 
    
'''
class MenuItemView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    ordering_fields = ['price', 'inventory']
    filterset_fields = ['price', 'inventory']
    search_fields = ['category__title']
'''
    
@api_view()
@permission_classes([IsAuthenticated])
@throttle_classes([TenCallsPerMinute])
def manager_view(request):
    if request.user.groups.filter(name='manager').exists():
        return(Response({ "message": "Only Manager Should See THIS" }))
    else:
        return Response({"message":"You Are Not Authorized"}, 403)
    
@api_view()
@throttle_classes([AnonRateThrottle])
def throttle_check(request):
    return(Response({"message": "successful"}))

@api_view()
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def throttle_check_auth(request):
    return(Response({"message": "message for logged in users only"}))

@api_view(['GET','POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
@throttle_classes([UserRateThrottle, AnonRateThrottle])
def managers(request):
        if request.method == "GET":
#            if request.user.has_perm("LittlelemonAPI.view_user"):
                return Response(User.objects.all().values())
            
        if request.method == "POST":
            if request.user.has_perm("LittlelemonAPI.add_user"):
                username = request.data['username']
                user = get_object_or_404(User, username=username)
                if user:
                    manager = Group.objects.get(name='manager')
                    manager.user_set.add(user)
                    return Response({"message": "added!"})
                return Response({"message": "error"}, status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle, AnonRateThrottle])
def managers_delete_view(request, username):
            if request.method == "DELETE": 
                if request.user.has_perm("LittlelemonAPI.delete_user"):
                    user = get_object_or_404(User, username=username)
                    if user: 
                        manager = Group.objects.get(name='manager')
                        manager.user_set.remove(user)
                        return(Response({"message": "removed"}))
                    return Response("404 - Not found ")
                
@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle, AnonRateThrottle])
def cart(request):
    if request.method == "GET":
        if request.user.has_perm("littlelemonAPI.view_cart"):
            cart_items = Cart.objects.all().filter(user=request.user).values()
            serialized_cart = CartSerializer(cart_items, many=True)
            return Response(serialized_cart.data, status=status.HTTP_200_OK)
    
    elif request.method == "POST": 
        if request.user.has_perm("littlelemonAPI.add_cart"): 
            #menu_item = MenuItem.objects.all().filter(request.data("menu_item_id"))
            user_id = request.user.id
            menuitem_id = request.data['menuitem_id']
            quantity = request.data['quantity']
            unit_price = request.data['unit_price']
            price = request.data['price']
            
            cartSerializer = CartSerializer(data = {'user_id': user_id, 'menuitem_id': menuitem_id, 'quantity': quantity, 'unit_price': unit_price, 'price':price})
            cartSerializer.is_valid(raise_exception=True)
            cartSerializer.save()
            return Response(cartSerializer.validated_data, status.HTTP_201_CREATED)
        else:
            return Response("You don't have access", status.HTTP_401_UNAUTHORIZED)
        
    elif request.method == "DELETE":
        if request.user.has_perm('littlelemonAPI.delete_cart'):
            cart_items = Cart.objects.all().filter(user=request.user)
            
            for cart_item in cart_items:
                cart_item.delete()
                
            return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle, AnonRateThrottle])
def order(request):
    if request.method == 'GET': 
        serialized_order = OrderItemsSerializer(data=OrderItem.objects.all(), many=True)
        serialized_order.is_valid()
        order_items = serialized_order.data
        
        
        if request.user.groups.filter(name='delivery crew').exists():
            filtered_list = []
            for item in order_items: 
                if item['order']['delivery_crew']: 
                    filtered_list.append(item)
            return Response(filtered_list, status=status.HTTP_200_OK)
        
        elif request.user.groups.filter(name='manager').exists():
            return Response(order_items, status=status.HTTP_200_OK)
        
        elif request.user.groups.filter(name='customer').exists():
            customer_order = []
            for item in order_items: 
                if item['order']['user']['id'] == request.user.id:
                    customer_order.append(item)
            return Response(customer_order, status=status.HTTP_200_OK)
            
        else:
                return Response("User group not found")
                orderItem = OrderItem.objects.all().values().filter(order__user=request.user)
                serialized_order = OrderItemsSerializer(orderItem, many=True)
                return Response(serialized_order.data, status=status.HTTP_200_OK)
    
    if request.method == 'POST':
        user = request.user.id
        total = request.data['total']
        date = request.data['date']
        serialized_order = OrderSerializer(data={ 'user_id': user, 'total': total, 'date': date})
        serialized_order.is_valid(raise_exception=True)
        serialized_order.save()
        order_id = serialized_order.data['id']
        
        cart_items = Cart.objects.all().values().filter(user=request.user)
        serialized_cart = CartSerializer(cart_items.values(), many=True)

        for item in serialized_cart.data: 
            item['order_id'] = order_id
            
        serialized_order_items = OrderItemsSerializer(data=serialized_cart.data, many=True)
        serialized_order_items.is_valid(raise_exception=True)
        serialized_order_items.save()
        
        for cart_item in cart_items:
            cart_item.delete()

        return Response(serialized_order_items.data, status=status.HTTP_201_CREATED)
    
    return Response(status=status.HTTP_404_NOT_FOUND)
    

@api_view(['GET', 'PUT', 'DELETE', 'PATCH'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle, AnonRateThrottle])
def single_order(request, pk):
#   order = get_object_or_404(Order, pk=pk)
    if request.method == 'GET': 
        order = OrderItem.objects.all().filter(order_id = pk)
        if request.method == 'GET':
            serialized_order = OrderItemsSerializer(order, many=True)
            return Response(serialized_order.data)
        
    if request.method == 'PUT':
        if request.user.has_perm('littlelemonAPI.change_order'):
            new_order = request.data
            order = get_object_or_404(Order, id=pk)
            serialized_order = OrderSerializer(order, data=new_order, partial=True)
            serialized_order.is_valid(raise_exception=True)
            serialized_order.save()
            return Response(serialized_order.data, status.HTTP_201_CREATED)
        return Response("Forbidden: ", status.HTTP_403_FORBIDDEN)
            
    if request.method == 'DELETE':
        if request.user.has_perm('littlelemonAPI.delete_order'):
            order = get_object_or_404(Order, id=pk)
            order.delete()
            return Response(status.HTTP_204_NO_CONTENT)
        return Response(status.HTTP_404_NOT_FOUND)
    
    if request.method == 'PATCH':
        if request.user.groups.filter(name='delivery crew').exists():
            new_order = request.data
            if hasattr(new_order,'delivery_crew_id'):
                return Response("Only managers can update assigned delivery crew", status=status.HTTP_403_FORBIDDEN)
            
            else: 
                order = get_object_or_404(Order, id=pk)
                serialized_order = OrderSerializer(order, data=new_order, partial=True)
                serialized_order.is_valid(raise_exception=True)
                serialized_order.save()
                return Response(serialized_order.data, status.HTTP_201_CREATED)

        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
            
            
            
        
        

            
    
'''
@csrf_exempt
def books(request):
    if request.method == 'GET':
        books = Book.objects.all().values()
        return JsonResponse({"books": list(books)})
    elif request.method == 'POST':
        title = request.POST.get('title')
        author = request.POST.get('author')
        price = request.POST.get('price')
        book = Book(title = title, author = author, price = price)
        
        try: 
            book.save()
        except IntegrityError: 
            return JsonResponse({'error': 'true', 'message': 'required field missing'}, status=400)
        return JsonResponse(model_to_dict(book), status=201)


@api_view(['POST'])
def books(request):
    return Response('List of the books', status=status.HTTP_200_OK)
            
class BookList(APIView):
    def get(self, request):
        author = request.GET.get('author')
        if (author): 
            return Response({"message":"List of the books by " + author}, status.HTTP_200_OK)
            
        return Response({"message":"List of the books"}, status.HTTP_200_OK)
        
    def post(self, request):
        payload = request.data.get("title")
        return Response({"title": payload}, status.HTTP_201_CREATED)

class Book(APIView):
    def get(self, request, pk):
        return Response({"message":"single book with id " + str(pk)}, status.HTTP_200_OK)
    
    def put(self, request, pk): 
        return Response({"title":request.data.get("title")}, status.HTTP_200_OK)
        
'''
