from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from garpix_order.models import RobokassaPayment
from garpix_order.serializers import RobokassaPaymentSerializer, RobokassaResultSerializer


class RobokassaView(mixins.CreateModelMixin, mixins.ListModelMixin, GenericViewSet):
    serializer_class = RobokassaPaymentSerializer

    def get_queryset(self):
        return RobokassaPayment.objects.all()

    def get_serializer_class(self):
        if self.action == 'pay':
            return RobokassaResultSerializer
        return RobokassaPaymentSerializer

    def perform_create(self, serializer):
        return serializer.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(instance.generate_payment_link(), status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['post'])
    def pay(self, request, pk, *args, **kwargs):
        payment = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result, error = payment.pay(serializer.data)
        if result:
            return Response({'result': 'success'})
        return Response({'result': [error]})
