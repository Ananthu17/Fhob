from rest_framework import serializers

from hobo_user.models import PromoCode


class DiscountsSerializer(serializers.ModelSerializer):

    class Meta:
        model = PromoCode
        fields = ['id', 'promo_code', 'created_time', 'valid_from', 'valid_to',
                  'life_span', 'amount_type', 'amount', 'user_type']

    def to_representation(self, instance):
        promocode = dict()
        promocode['id'] = instance.id
        promocode['promo_code'] = instance.promo_code
        promocode['created_time'] = instance.created_time
        promocode['valid_from'] = instance.valid_from.date()
        promocode['valid_to'] = instance.valid_to.date()
        promocode['life_span'] = instance.life_span
        promocode['amount_type'] = instance.amount_type
        promocode['amount'] = instance.amount
        promocode['user_type'] = instance.user_type
        return promocode
