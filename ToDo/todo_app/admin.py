from django.contrib import admin

from todo_app.models import Task, Project


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'project', 'date_due', 'done', 'date_added')
    list_filter = ('done', 'date_due', 'owner')
    list_editable = ('done',)
    search_fields = ('name',)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'date_added')
    search_fields = ('name',)
