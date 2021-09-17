from .serializers import ProjectSerializer


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

    def project_to_json(self, project):
        project_dict = {}
        for item in project:
            project_dict[item.id] = ProjectSerializer(item).data
        return project_dict
