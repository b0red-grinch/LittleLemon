from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from . import views 

urlpatterns = [
   path('menu-items/', views.menu_items),
   path('menu-items/<int:pk>', views.single_item),
   path('cart/menu-items/', views.cart),
   path('orders/', views.order),
   path('orders/<int:pk>', views.single_order),
#   path('menu-items/<int:pk>', views.SingleMenuItemView.as_view()),
   path('menu', views.menu), 
   path('category', views.CategoriesView.as_view()),
   #path('menu-items/', views.MenuItemView.as_view()),
   path('secret/', views.manager_view),
   path('api-token-auth', obtain_auth_token),
   path('throttle-check/', views.throttle_check),
   path('throttle-check-auth/', views.throttle_check_auth),
   path('groups/manager/users/', views.managers),
   path('groups/manager/users/<str:username>/', views.managers_delete_view)
   # path('books', views.books),
   #path('books/', views.BookList.as_view()),
   #path('books/<int:pk>', views.Book.as_view())
]