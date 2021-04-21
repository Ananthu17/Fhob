from import_export.resources import ModelResource

from .models import EthnicAppearance, AthleticSkill, Country, \
    GuildMembership


class EthnicAppearanceResource(ModelResource):

    class Meta:
        model = EthnicAppearance


class AthleticSkillResource(ModelResource):

    class Meta:
        model = AthleticSkill


class CountryResource(ModelResource):

    class Meta:
        model = Country


class GuildMembershipResource(ModelResource):

    class Meta:
        model = GuildMembership
