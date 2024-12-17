from .serializers import UnitSerializer, ProductSerializer, ProductStockSerializer, HistorySerializer
from rest_framework import viewsets, permissions, status, pagination
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from rest_framework import status
from .models import History, Product, ProductStock, Units
from django.db import transaction
from django.db.models import Q

class PageLimitPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class UnitViewSet(viewsets.ModelViewSet):
    queryset = Units.objects.all()
    serializer_class = UnitSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PageLimitPagination

    def get_queryset(self):
        company = self.request.user.company
        units = Units.objects.filter(company=company)

        if not units.exists():
            return Response({
                "status": False,
                "message": "No units available for this company.",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        return units

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response({
                "status": True,
                "message": "Unit created successfully.",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                "status": False,
                "message": str(e),
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response({
                "status": True,
                "message": "Unit updated successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": False,
                "message": str(e),
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response({
                "status": True,
                "message": "Unit deleted successfully.",
                "data": None
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": False,
                "message": str(e),
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PageLimitPagination

    def get_queryset(self):
        company = self.request.user.company
        query = self.request.query_params.get('q', '').strip()
        product_name = self.request.query_params.get('product_name', '').strip()

        products = Product.objects.filter(company=company)

        if query:
            products = products.filter(
                Q(product_name__icontains=query) | Q(product_type__icontains=query)
            )

        if product_name:
            products = products.filter(product_name__icontains=product_name)

        if not products.exists():
            return Response({
                "status": False,
                "message": "No products available for this company.",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        return products

    def create(self, request, *args, **kwargs):
        company = self.request.user.company
        product_name = request.data.get('product_name')
        unit_id = request.data.get('unit')

        # Check if product already exists with same name and unit for the company
        if Product.objects.filter(company=company, product_name=product_name, unit_id=unit_id).exists():
            return Response({
                "status": False,
                "message": "A product with the same name and unit already exists for this company.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Create the product using the serializer
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            product = serializer.save(company=company)

            # Use a transaction to ensure both ProductStock and History are created together
            with transaction.atomic():
                # Create product stock
                self.create_product_stock(product)

                # Create history entry
                self.create_history_record(product)

            return Response({
                "status": True,
                "message": "Product created successfully.",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                "status": False,
                "message": str(e),
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

    def create_product_stock(self, product):
        """Create a ProductStock entry for the newly created product."""
        ProductStock.objects.create(
            product=product,
            product_quantity=product.product_quantity,
            transaction_type='buy',  # Assuming initial stock is based on a 'buy' transaction
            company=product.company
        )

    def create_history_record(self, product):
        """Create an initial history entry when the product is added."""
        History.objects.create(
            product=product,
            product_quantity=product.product_quantity,
            transaction_type='buy',  # Assuming the initial transaction is 'buy'
            company=product.company
        )

    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response({
                "status": True,
                "message": "Product updated successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": False,
                "message": str(e),
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response({
                "status": True,
                "message": "Product deleted successfully.",
                "data": None
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": False,
                "message": str(e),
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)


class ProductStockViewSet(viewsets.ModelViewSet):
    queryset = ProductStock.objects.all()
    serializer_class = ProductStockSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        company = self.request.user.company
        return ProductStock.objects.filter(company=company)

    def create(self, request, *args, **kwargs):
        company = request.user.company
        product_id = request.data.get('product')  # 'product' in the request
        product_quantity = request.data.get('product_quantity')
        transaction_type = request.data.get('transaction_type')

        # Validate that the required fields are provided
        if not product_id or not product_quantity or not transaction_type:
            return Response({
                "status": False,
                "message": "Product ID, Quantity, and Transaction Type are required.",
                "data": "Null"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Fetch the product object by its ID
            product = get_object_or_404(Product, product_id=product_id, company=company)
        except ValueError:
            return Response({
                "status": False,
                "message": "Invalid Product ID.",
                "data": "Null"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate product quantity
        try:
            product_quantity = float(product_quantity)
            if product_quantity <= 0:
                return Response({
                    "status": False,
                    "message": "Product quantity must be greater than zero.",
                    "data": "Null"
                }, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({
                "status": False,
                "message": "Invalid product quantity value.",
                "data": "Null"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get or create the product stock entry for this product and company
        productstock, created = ProductStock.objects.get_or_create(product=product, company=company)

        if transaction_type.lower() == 'buy':
            # Add the quantity for 'buy' transaction
            productstock.product_quantity += product_quantity
            action = 'added'
        elif transaction_type.lower() == 'sell':
            # Check if enough stock is available for 'sell' transaction
            if productstock.product_quantity < product_quantity:
                return Response({
                    "status": False,
                    "message": "Insufficient stock for selling.",
                    "data": "Null"
                }, status=status.HTTP_400_BAD_REQUEST)
            # Subtract the quantity for 'sell' transaction
            productstock.product_quantity -= product_quantity
            action = 'subtracted'
        else:
            return Response({
                "status": False,
                "message": "Invalid transaction type.",
                "data": "Null"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Save the updated product stock
        productstock.save()

        # Create a new history record for the transaction
        History.objects.create(
            product=product,
            product_quantity=product_quantity,
            transaction_type=transaction_type,
            company=company,
        )

        return Response({
            "status": True,
            "message": f"Stock {'created' if created else 'updated'} successfully.",
            "data": {
                "product_id": product.product_id,
                "product_name": product.product_name,
                "quantity": productstock.product_quantity,
                "transaction_type": transaction_type,
                "company_id": company.id,
            }
        }, status=status.HTTP_201_CREATED)


class HistoryViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = HistorySerializer
    queryset = History.objects.all()

    def get_queryset(self):
        company = getattr(self.request.user, 'company', None)
        if not company:
            return History.objects.none()

        query = self.request.query_params.get('q', '')
        sort_by = self.request.query_params.get('sort', 'id')
        sort_order = self.request.query_params.get('order', 'desc')
        product_id = self.request.query_params.get('product', None)

        valid_sort_fields = ['id', 'product_id', 'product_name', 'product_quantity', 'updated_date']
        if sort_by not in valid_sort_fields:
            sort_by = 'id'

        if sort_order == 'desc':
            sort_by = '-' + sort_by

        history_queryset = History.objects.filter(company=company)

        if product_id:
            try:
                product_id = int(product_id)
                history_queryset = history_queryset.filter(product_id=product_id)
            except ValueError:
                raise ValidationError({"message": "Invalid Product ID."})

        if query:
            history_queryset = history_queryset.filter(product_id__product_name__icontains=query)

        return history_queryset.order_by(sort_by)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page_size = 10
        paginator = Paginator(queryset, page_size)
        page_number = request.query_params.get('page', 1)
        page_obj = paginator.get_page(page_number)

        serializer = self.get_serializer(page_obj, many=True)
        return Response({
            "status": True,
            "message": "History fetched successfully.",
            "data": serializer.data,
            "pagination": {
                "current_page": page_obj.number,
                "total_pages": paginator.num_pages,
                "has_next": page_obj.has_next(),
                "has_previous": page_obj.has_previous()
            }
        })

    def create(self, request, *args, **kwargs):
        product_id = request.data.get('product_id')
        product_quantity = request.data.get('product_quantity')
        transaction_type = request.data.get('transaction_type')

        if not product_id or not product_quantity or not transaction_type:
            return Response(
                {"error": "Product ID, Quantity, and Transaction Type are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        product = get_object_or_404(Product, id=product_id, is_active=True)

        history = History.objects.create(
            product_id=product,
            product_quantity=product_quantity,
            transaction_type=transaction_type,
            company=request.user.company
        )
        self.stock_update_hist(product, 0, '', product_quantity, transaction_type)

        return Response({"message": "History record created successfully."}, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        new_quantity = request.data.get('product_quantity')
        new_transaction_type = request.data.get('transaction_type')

        if not new_quantity or not new_transaction_type:
            return Response(
                {"error": "Quantity and Transaction Type are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            new_quantity = float(
                new_quantity)
        except ValueError:
            return Response({"error": "Quantity must be a number."},
                            status=status.HTTP_400_BAD_REQUEST)

        old_quantity = instance.product_quantity
        old_transaction_type = instance.transaction_type

        try:
            self.stock_update_hist(
                instance.product_id, old_quantity, old_transaction_type,
                new_quantity, new_transaction_type
            )
        except ValueError as e:
            return Response({"error": str(e)},
                            status=status.HTTP_400_BAD_REQUEST)

        instance.product_quantity = new_quantity
        instance.transaction_type = new_transaction_type
        instance.save()

        return Response(
            {"message": "History record and stock updated successfully."},
            status=status.HTTP_200_OK)

    def stock_update_hist(
            self, product, old_quantity, old_transaction_type, new_quantity,
            new_transaction_type
            ):
        stock, created = ProductStock.objects.get_or_create(product_id=product)

        if old_transaction_type == 'buy':
            stock.product_quantity -= old_quantity
        elif old_transaction_type == 'sell':
            stock.product_quantity += old_quantity

        if new_transaction_type == 'buy':
            stock.product_quantity += new_quantity
        elif new_transaction_type == 'sell':
            if stock.product_quantity < new_quantity:
                raise ValueError("Insufficient product stock quantity.")
            stock.product_quantity -= new_quantity

        stock.save()

