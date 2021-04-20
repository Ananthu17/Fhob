from allauth.account.adapter import DefaultAccountAdapter
from .models import Country


class CustomUserAccountAdapter(DefaultAccountAdapter):

    def save_user(self, request, user, form, commit=True):
        """
        Saves a new `User` instance using information provided in the
        signup form.
        """
        from allauth.account.utils import user_field

        user = super().save_user(request, user, form, False)
        user_field(user, 'first_name', request.data.get('first_name', ''))
        user_field(user, 'middle_name', request.data.get('middle_name', ''))
        user_field(user, 'last_name', request.data.get('last_name', ''))
        user_field(user, 'email', request.data.get('email', ''))
        user_field(user, 'password1', request.data.get('password1', ''))
        user.save()
        return user


class CustomIndieProUserAdapter(DefaultAccountAdapter):

    def save_user(self, request, user, form, commit=True):
        """
        Saves a new `User` instance using information provided in the
        signup form.
        """
        from allauth.account.utils import user_field

        country_id = request.data.get('country','')
        guild_membership_id = request.data.get('guild_membership_id','')

        user = super().save_user(request, user, form, False)
        user_field(user, 'first_name', request.data.get('first_name', ''))
        user_field(user, 'middle_name', request.data.get('middle_name', ''))
        user_field(user, 'last_name', request.data.get('last_name', ''))
        user_field(user, 'email', request.data.get('email', ''))
        user_field(user, 'password1', request.data.get('password1', ''))
        user_field(user, 'phone_number', request.data.get('phone_number', ''))
        user_field(user, 'date_of_birth', request.data.get(
            'date_of_birth', ''))
        user_field(user, 'address', request.data.get('address', ''))
        user_field(user, 'membership', request.data.get('membership', ''))
        user.save()
        if guild_membership_id is not None:
            for item in guild_membership_id:
                user.guild_membership.add(item)
        if country_id is not None:
            country = Country.objects.get(pk=country_id)
            user.country = country
            user.save()
        return user
