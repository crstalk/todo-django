from django.urls import path
from . import views

app_name = "todo_app"

urlpatterns = [
    path("", views.index, name="tasks"),
    path("today/", views.today, name="today"),
    path("add/", views.add_task, name="add_task"),
    path('profile/', views.profile, name = 'profile'),
    path('projects/', views.projects, name = 'projects'),
    path('delete_task/<int:task_id>', views.delete_task, name = 'delete_task'),
    path('add_project/', views.add_project, name='add_project'),
    path('taskprojects/<int:project_id>', views.taskprojects, name='taskprojects'),
    path("toggle/<int:entry_id>", views.toggle, name="toggle"),
    path("addtaskproject/<int:entry_id>", views.addtaskproject, name="addtaskproject")]