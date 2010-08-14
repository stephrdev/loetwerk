from django.contrib import admin
from journeyman.builds.models import Build, BuildStep

class BuildStepInline(admin.StackedInline):
    model = BuildStep
    extra = 0

class BuildAdmin(admin.ModelAdmin):
    inlines = [BuildStepInline,]

admin.site.register(Build, BuildAdmin)