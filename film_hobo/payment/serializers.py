from rest_framework import serializers

from hobo_user.models import PromoCode


class DiscountsSerializer(serializers.ModelSerializer):
    valid_from = serializers.SerializerMethodField(source='get_valid_from')
    valid_to = serializers.SerializerMethodField(source='get_valid_to')

    class Meta:
        model = PromoCode
        fields = ['id', 'promo_code', 'created_time', 'valid_from', 'valid_to',
                  'life_span', 'amount_type', 'amount', 'user_type']

    def get_valid_from(self, obj):
        return obj.valid_from.date()

    def get_valid_to(self, obj):
        return obj.valid_to.date()
