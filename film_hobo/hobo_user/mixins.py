from .serializers import ProjectSerializer
from django.db.models.constants import LOOKUP_SEP
import operator
from functools import reduce
from django.db import models
from rest_framework.compat import distinct
from rest_framework.settings import api_settings
from .models import CustomUser

class SegregatorMixin():
    def project_segregator(self, project):
        context = {}
        context["scenes"] = self.project_to_json(
                            project.filter(format="SCH").order_by('-id'))
        context["top_scenes"] = self.project_to_json(project.filter(
                                     format="SCH").order_by('-rating'))
        context["filims"] = self.project_to_json(project.filter(
                            format="SHO").order_by('-id'))
        context["top_filims"] = self.project_to_json(project.filter(
                                     format="SHO").order_by('-rating'))
        return context

    def showcase_segregator(self, project):
        context = {}
        context["top_scenes"] = self.project_to_json(
            project.filter(format="SCH").filter(rating__gte=4)
            .order_by('-likes')[:10]
        )
        context["top_shorts"] = self.project_to_json(
            project.filter(format="SHO").filter(rating__gte=4)
            .order_by('-likes')[:10]
        )
        context["new_scenes"] = self.project_to_json(
            project.filter(format="SCH").order_by('-id')
        )
        context["new_shorts"] = self.project_to_json(
            project.filter(format="SHO").order_by('-id')
        )
        return context

    def pilot_segregator(self, project):
        context = {}
        context["new_scenes"] = self.project_to_json(
                            project.filter(format="PIL").order_by('-id'))
        context["top_scenes"] = self.project_to_json(project.filter(
                                     format="PIL").order_by('-rating'))
        context["new_shorts"] = self.project_to_json(project.filter(
                            format="FTR").order_by('-id'))
        context["top_shorts"] = self.project_to_json(project.filter(
                                     format="FTR").order_by('-rating'))
        return context
        return context

    def project_to_json(self, project):
        project_dict = {}
        for item in project:
            project_dict["A"+str(item.id)] = ProjectSerializer(item).data
        return project_dict


class SearchFilter():
    # The URL query parameter used for the search.
    search_param = api_settings.SEARCH_PARAM
    template = 'rest_framework/filters/search.html'
    lookup_prefixes = {
        '^': 'istartswith',
        '=': 'iexact',
        '@': 'search',
        '$': 'iregex',
    }
    search_title = ('Search')
    search_description = ('A search term.')

    def get_search_fields(self, view, request):
        """
        Search fields are obtained from the view, but the request is always
        passed to this method. Sub-classes can override this method to
        dynamically change the search fields based on request content.
        """
        return getattr(view, 'search_fields', None)

    def get_search_terms(self, request):
        """
        Search terms are set by a ?search=... query parameter,
        and may be comma and/or whitespace delimited.
        """
        params = request.query_params.get(self.search_param, '')
        params = params.replace('\x00', '')  # strip null characters
        params = params.replace(',', ' ')
        return params.split()

    def construct_search(self, field_name):
        lookup = self.lookup_prefixes.get(field_name[0])
        if lookup:
            field_name = field_name[1:]
        else:
            lookup = 'icontains'
        return LOOKUP_SEP.join([field_name, lookup])

    def must_call_distinct(self, queryset, search_fields):
        """
        Return True if 'distinct()' should be used to query the given lookups.
        """
        for search_field in search_fields:
            opts = queryset.model._meta
            if search_field[0] in self.lookup_prefixes:
                search_field = search_field[1:]
            # Annotated fields do not need to be distinct
            if isinstance(queryset, models.QuerySet) and search_field in queryset.query.annotations:
                continue
            parts = search_field.split(LOOKUP_SEP)
            for part in parts:
                field = opts.get_field(part)
                if hasattr(field, 'get_path_info'):
                    # This field is a relation, update opts to follow the relation
                    path_info = field.get_path_info()
                    opts = path_info[-1].to_opts
                    if any(path.m2m for path in path_info):
                        # This field is a m2m relation so we know we need to call distinct
                        return True
                else:
                    # This field has a custom __ query transform but is not a relational field.
                    break
        return False

    def find_user(self, search_terms, queryset):
        for item in CustomUser.objects.all():
            if item.get_full_name() == " ".join(search_terms):
                return queryset.filter(creator=item.id)

    def filter_queryset(self, request, queryset, view):
        search_fields = self.get_search_fields(view, request)
        search_terms = self.get_search_terms(request)

        user = self.find_user(search_terms, queryset)
        if user:
            return user

        if not search_fields or not search_terms:
            return queryset

        orm_lookups = [
            self.construct_search(str(search_field))
            for search_field in search_fields
        ]

        base = queryset
        conditions = []
        for search_term in search_terms:
            queries = [
                models.Q(**{orm_lookup: search_term})
                for orm_lookup in orm_lookups
            ]
            conditions.append(reduce(operator.or_, queries))
        queryset = queryset.filter(reduce(operator.and_, conditions))

        if self.must_call_distinct(queryset, search_fields):
            # Filtering against a many-to-many field requires us to
            # call queryset.distinct() in order to avoid duplicate items
            # in the resulting queryset.
            # We try to avoid this if possible, for performance reasons.
            queryset = distinct(queryset, base)
        return queryset
