from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UnitViewSet, ProductViewSet, ProductStockViewSet, HistoryViewSet

router = DefaultRouter()
router.register(r'units', UnitViewSet, basename='units')
router.register(r'products', ProductViewSet, basename='products')
router.register(r'product_stock', ProductStockViewSet, basename='product-stock')
router.register(r'history', HistoryViewSet)

urlpatterns = [
    path('', include(router.urls)),

]