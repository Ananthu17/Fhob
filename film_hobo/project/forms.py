from django import forms
from hobo_user.models import Project
from bootstrap_datepicker_plus import DateTimePickerInput


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
