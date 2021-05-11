from rest_framework import serializers

from hobo_user.models import PromoCode


class DiscountsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromoCode
        fields = ['id', 'promo_code', 'created_time', 'valid_from', 'valid_to',
                  'life_span', 'amount_type', 'amount', 'user_type']
