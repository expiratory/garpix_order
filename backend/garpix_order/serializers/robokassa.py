from rest_framework import serializers

from garpix_order.models import RobokassaPayment


class RobokassaPaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = RobokassaPayment
        fields = ('title', 'order', 'amount',)


class RobokassaResultSerializer(serializers.Serializer):
    OutSum = serializers.FloatField(required=True)
    SignatureValue = serializers.CharField(required=True)
