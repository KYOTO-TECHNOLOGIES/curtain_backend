from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import Customer
from .serializers import CustomerSerializer


class CustomerViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Customer.objects.all().order_by('-created_at')
    serializer_class = CustomerSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        search = self.request.query_params.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(phone__icontains=search) |
                Q(email__icontains=search)
            )
        
        return queryset
    
    @action(detail=False, methods=['get'], url_path='lookup')
    def lookup(self, request):
        phone = request.query_params.get('phone')
        email = request.query_params.get('email')
        
        if not phone and not email:
            return Response({
                'error': 'Please provide either phone or email parameter.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        customer = None
        if phone:
            customer = Customer.objects.filter(phone=phone).first()
        if not customer and email:
            customer = Customer.objects.filter(email__iexact=email).first()
        
        if customer:
            serializer = self.get_serializer(customer)
            return Response({
                'found': True,
                'customer': serializer.data
            })
        
        return Response({
            'found': False,
            'message': 'Customer not found.'
        }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['post'], url_path='create-or-get')
    def create_or_get(self, request):
        phone = request.data.get('phone')
        email = request.data.get('email')
        
        customer = None
        if phone:
            customer = Customer.objects.filter(phone=phone).first()
        if not customer and email:
            customer = Customer.objects.filter(email__iexact=email).first()
        
        if customer:
            serializer = self.get_serializer(customer)
            return Response({
                'created': False,
                'customer': serializer.data
            })
        
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            customer = serializer.save(created_by=request.user)
            return Response({
                'created': True,
                'customer': CustomerSerializer(customer).data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)