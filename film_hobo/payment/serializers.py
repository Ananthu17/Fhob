from rest_framework import serializers

from hobo_user.models import PromoCode


class DiscountsSerializer(serializers.ModelSerializer):

    class Meta:
        model = PromoCode
        fields = ['id', 'promo_code', 'created_time', 'valid_from', 'valid_to',
                  'life_span', 'amount_type', 'amount', 'user_type']

    def validate_amount(self, obj):
        if (self.__dict__['_kwargs']['data']['amount_type'] == 'percentage'):
            if (obj >= 0) and (obj <= 100):
                return obj
            else:
                raise serializers.ValidationError("please enter a valid "
                                                  "percentage value between"
                                                  " 0 and 100")
        else:
            return obj

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
