from django import forms
from hobo_user.models import Project
from .models import Sides
from .models import Audition
from bootstrap_datepicker_plus import DateTimePickerInput
from ckeditor_uploader.widgets import CKEditorUploadingWidget


class VideoSubmissionLastDateForm(forms.ModelForm):

    class Meta:
        model = Project
        fields = ('last_date', )

        widgets = {
            'last_date': DateTimePickerInput(format='%Y-%m-%d'),
        }

    def __init__(self, *args, **kwargs):
        super(VideoSubmissionLastDateForm, self).__init__(*args, **kwargs)
        self.fields['last_date'].widget.attrs['id'] = 'last_date'


class SubmitAuditionForm(forms.ModelForm):
    i_agree = forms.BooleanField(widget=forms.CheckboxInput())

    class Meta:
        model = Audition
        fields = ('name', 'agent_name', 'agent_email', 'location',
                  'video_type', 'video_url')

    def __init__(self, *args, **kwargs):
        super(SubmitAuditionForm, self).__init__(*args, **kwargs)
        self.fields['name'].required = True
        self.fields['location'].required = True
        self.fields['video_type'].required = True
        self.fields['video_url'].required = True


class AddSidesForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorUploadingWidget())

    class Meta:
        model = Sides
        fields = ('scene_1', 'scene_2', 'scene_3')