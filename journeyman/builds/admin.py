from django.contrib import admin
from journeyman.builds.models import Build, BuildStep, BuildResult

class BuildStepInline(admin.TabularInline):
    model = BuildStep
    extra = 0

class BuildResultInline(admin.TabularInline):
    model = BuildResult
    extra = 0

class BuildAdmin(admin.ModelAdmin):
    inlines = [BuildStepInline, BuildResultInline]

admin.site.register(Build, BuildAdmin)