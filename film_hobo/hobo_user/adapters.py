from allauth.account.utils import user_field
from allauth.account.adapter import DefaultAccountAdapter
from .models import Country, BetaTesterCodes


class CustomUserAccountAdapter(DefaultAccountAdapter):

    def save_user(self, request, user, form, commit=True):
        """
        Saves a new `User` instance using information provided in the
        signup form.
        """
        beta_user = request.data.get('beta_user', '')
        beta_user_code_id = request.data.get('beta_user_code', '')
        user = super().save_user(request, user, form, False)
        user_field(user, 'first_name', request.data.get('first_name', ''))
        user_field(user, 'middle_name', request.data.get('middle_name', ''))
        user_field(user, 'last_name', request.data.get('last_name', ''))
        user_field(user, 'email', request.data.get('email', ''))
        user_field(user, 'password1', request.data.get('password1', ''))
        user_field(user, 'beta_user_end', request.data.get('beta_user_end', ''))
        if beta_user is not None:
            user.beta_user = beta_user
            user.save()
        if beta_user_code_id is not None:
            beta_user_code = BetaTesterCodes.objects.get(pk=beta_user_code_id)
            user.beta_user_code = beta_user_code
            user.save()
        user.save()
        return user


class CustomIndieProUserAdapter(DefaultAccountAdapter):

    def save_user(self, request, user, form, commit=True):
        """
        Saves a new `User` instance using information provided in the
        signup form.
        """

        country_id = request.data.get('country', '')
        beta_user = request.data.get('beta_user', '')
        beta_user_code_id = request.data.get('beta_user_code', '')
        guild_membership_id = request.data.get('guild_membership_id', '')

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
        user_field(user, 'beta_user_end', request.data.get('beta_user_end', ''))
        user.save()
        if guild_membership_id is not None:
            for item in guild_membership_id:
                user.guild_membership.add(item)
        if beta_user is not None:
            user.beta_user = beta_user
            user.save()
        if beta_user_code_id is not None:
            beta_user_code = BetaTesterCodes.objects.get(pk=beta_user_code_id)
            user.beta_user_code = beta_user_code
            user.save()
        if country_id is not None:
            country = Country.objects.get(pk=country_id)
            user.country = country
            user.save()
        return user


class CustomCompanyUserAccountAdapter(DefaultAccountAdapter):

    def save_user(self, request, user, form, commit=True):
        """
        Saves a new comapny `User` instance using information provided in the
        signup form.
        """
        country_id = request.data.get('country', '')
        beta_user = request.data.get('beta_user', '')
        beta_user_code_id = request.data.get('beta_user_code', '')

        user = super().save_user(request, user, form, False)
        user_field(user, 'first_name', request.data.get('first_name', ''))
        user_field(user, 'middle_name', request.data.get('middle_name', ''))
        user_field(user, 'last_name', request.data.get('last_name', ''))
        user_field(user, 'email', request.data.get('email', ''))
        user_field(user, 'password1', request.data.get('password1', ''))
        user_field(user, 'phone_number', request.data.get('phone_number', ''))
        user_field(user, 'date_of_birth', request.data.get('date_of_birth', ''))
        user_field(user, 'address', request.data.get('address', ''))
        user_field(user, 'company_name', request.data.get('company_name', ''))
        user_field(
            user, 'company_address', request.data.get('company_address', ''))
        user_field(
            user, 'company_website', request.data.get('company_website', ''))
        user_field(
            user, 'company_phone', request.data.get('company_phone', ''))
        user_field(
            user, 'title', request.data.get('title', ''))
        user_field(
            user, 'membership', request.data.get('membership', ''))
        user_field(
            user, 'beta_user_end', request.data.get('beta_user_end', None))
        user_field(
            user, 'company_type', request.data.get('company_type', ''))
        user.save()

        if country_id is not None:
            country = Country.objects.get(pk=country_id)
            user.country = country
            user.save()
        if beta_user is not None:
            user.beta_user = beta_user
            user.save()
        if beta_user_code_id is not None:
            beta_user_code = BetaTesterCodes.objects.get(pk=beta_user_code_id)
            user.beta_user_code = beta_user_code
            user.save()
        return user
