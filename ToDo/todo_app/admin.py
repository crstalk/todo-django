from django.contrib import admin

from todo_app.models import Element, Projects, TaskProject

# Register your models here.

admin.site.register(Element)
admin.site.register(Projects)
admin.site.register(TaskProject)
