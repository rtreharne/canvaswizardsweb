from django.contrib import admin

from .models import Module, Programme, Rule, Pathway

class ModuleAdmin(admin.ModelAdmin):
    list_display = ('code', 'title', 'semester', 'prereq', 'level', 'credits', 'compulsory', 'practical', 'year')
    list_filter = ('semester', 'level', 'credits', 'compulsory', 'practical')
    search_fields = ('code', 'title')
    ordering = ('code',)
    list_editable = ('compulsory', 'practical',)

    # Create a prerequisite field build from the prerequisites (code only)
    def prereq(self, obj):
        return ", ".join([p.code for p in obj.prerequisites.all()])
    
    def prereq_for(self, obj):
        return ", ".join([p.code for p in obj.requisite_for.all()])
    
    # Set the column name
    prereq.short_description = 'Prerequisites'

class ProgrammeAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'visible')
    list_filter = ('visible',)
    search_fields = ('title', 'slug')
    ordering = ('title',)
    list_editable = ('visible',)

class RuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'programme', 'year')
    list_filter = ('programme', 'year')
    search_fields = ('title', 'description')
    ordering = ('title',)

class PathwayAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'programme', 'url')
    list_filter = ('programme',)
    search_fields = ('title', 'description')
    ordering = ('title',)


admin.site.register(Module, ModuleAdmin)
admin.site.register(Programme, ProgrammeAdmin)
admin.site.register(Rule, RuleAdmin)
admin.site.register(Pathway, PathwayAdmin)
