from import_export import resources

from .models import InitialIntrestedUsers


class InitialIntrestedUsersResource(resources.ModelResource):

    class Meta:
        model = InitialIntrestedUsers

    def dehydrate_designation(self, initialintresteduser):
        """
        function to return designation title from designation_id
        """
        destnations = []
        for designation in initialintresteduser.designation.values():
            destnations.append(designation['title'])
            final_string = ", ".join(destnations)
        return final_string
