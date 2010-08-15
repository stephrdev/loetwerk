from django import forms
from journeyman.projects.models import Project

class RepositoryForm(forms.Form):
    name = forms.CharField(
        help_text='What\'s the name of your awesome project?')
    repository = forms.CharField(
        help_text='Please enter a valid repository url \
        (e.g. git+git://github.com/stephrdev/loetwerk.git)')

class BuildProcessForm(forms.Form):
    build_steps = forms.CharField(initial='python setup.py install',
        widget=forms.Textarea(attrs={'rows':3, 'cols':40}),
        help_text='Let\'s start off with the easy stuff, please type in all \
        the commands needed to install your package')
    test_steps = forms.CharField(initial='python setup.py test',
        widget=forms.Textarea(attrs={'rows':3, 'cols':40}),
        help_text='Now tell us how to run your tests. If you should have \
        many different test suites, just add another line.')
    dependencies = forms.CharField(required=False, initial='dependencies.txt',
        widget=forms.Textarea(attrs={'rows':3, 'cols':40}),
        help_text='Please enter a list of pip requirement files that you \
        have used to specify your dependencies')
    test_xmls = forms.CharField(required=False,
        widget=forms.Textarea(attrs={'rows':3, 'cols':40}),
        help_text='Please enter a newline separated list of paths of \
        unit test result xmls.')

class JourneyConfigOutputForm(forms.Form):
    pass

class JourneyConfigFileForm(forms.Form):
    config_file = forms.CharField(initial="journey.conf/config",
        help_text="If you leave this field blank, we will store the config \
        locally.", required=False)

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        exclude = ['active',]
