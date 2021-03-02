from rest_framework import mixins, generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Customer, User, Business, Visit
from .serializers import CustomerSerializer, UserSerializer, BusinessSerializer, VisitSerializer


class CustomerCreate(mixins.CreateModelMixin,
                     APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.create(validated_data=request.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.error_messages, status=status.HTTP_400_BAD_REQUEST)


class CustomerList(mixins.ListModelMixin,
                   generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class CustomerDetail(mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     generics.GenericAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    lookup_field = 'user__email'

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class BusinessCreate(mixins.CreateModelMixin,
                     APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = BusinessSerializer(data=request.data)
        if serializer.is_valid():
            serializer.create(validated_data=request.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.error_messages, status=status.HTTP_400_BAD_REQUEST)


class BusinessList(mixins.ListModelMixin,
                   generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class BusinessDetail(mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     generics.GenericAPIView):
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer
    lookup_field = 'user__email'

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs,)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)






class VisitCreate(mixins.CreateModelMixin,
                     APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = VisitSerializer(data=request.data)
        if serializer.is_valid():
            serializer.create(validated_data=request.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.error_messages, status=status.HTTP_400_BAD_REQUEST)


class VisitDetail(mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     generics.GenericAPIView):
    queryset = Visit.objects.all()
    serializer_class = VisitSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    #def put(self, request, *args, **kwargs):
    #    return self.update(request, *args, **kwargs)

    # def delete(self, request, *args, **kwargs):
    #     return self.destroy(request, *args, **kwargs)