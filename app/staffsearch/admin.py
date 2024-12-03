from django.contrib import admin
from .models import Profile, Institute, Department, Directorate, Keyword, Banner, Root, Search
from django.utils.html import format_html
from .tasks import get_profiles
from django.contrib import messages


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'profile', 'department', 'visible')
    list_filter = ('department',)
    list_editable = ('visible', )
    search_fields = ('last_name', 'first_name', 'department__name')

    def profile(self, obj):
        return format_html("<a href='{url}', target='_blank'>Click for profile</a>", url=obj.url)

class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'institute')

    #def institute(self, obj):
        #return obj.institute.name
    list_editable = ('institute',)
    search_fields = ('name', 'institute__name',)

class KeywordAdmin(admin.ModelAdmin):
    list_display = ('keyword', 'score', 'frequency', 'visible')
    list_editable = ('visible',)
    search_fields = ('keyword',)

class RootAdmin(admin.ModelAdmin):
    list_display = ('url','active')
    actions = ["admin_get_profiles"]

    @admin.action(description="Get Profiles From Root")
    def admin_get_profiles(moduleadmin, request, queryset):
        if request.user.is_staff:
            root_urls = [x.url for x in queryset]
            for url in root_urls:
                print("do nothing")
                get_profiles.delay(url)
            messages.info(request, "Getting Profiles!")


class SearchAdmin(admin.ModelAdmin):
    list_display = ('keywords', 'created_at')
    readonly_fields = ['created_at']



admin.site.register(Profile, ProfileAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Institute)
admin.site.register(Keyword, KeywordAdmin)
admin.site.register(Banner)
admin.site.register(Search, SearchAdmin)
admin.site.register(Root, RootAdmin)
