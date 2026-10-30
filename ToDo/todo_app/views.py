from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from todo_app.forms import TaskForm, ProjectForm, TaskpForm
from todo_app.models import Element, Projects, TaskProject
from django.views.decorators.http import require_POST


# Create your views here.

def index(request):
    tasks = Element.objects.all()
    context = {'tasks': tasks}
    return render(request, 'index.html', context)


def add_task(request):
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.save()
            return redirect('todo_app:tasks')
    else:
        form = TaskForm()
        print("форма создана")
    context = {'form': form}
    return render(request, 'add_task.html', context)


def today(request):
    return render(request, 'today.html')


def profile(request):
    return render(request, 'profile.html')


def projects(request):
    projects = Projects.objects.all()
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('todo_app:projects')
    else:
        form = ProjectForm()
    context = {'form': form, 'projects': projects}
    return render(request, 'projects.html', context)


@require_POST
def delete_task(request, task_id):
    task = get_object_or_404(Element, id=task_id)
    task.delete()
    messages.success(request, f'Задача "{task}" успешно удалена!')
    return redirect('todo_app:tasks')


def add_project(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('todo_app:projects')
    else:
        form = ProjectForm()
    context = {'form': form}
    return render(request, 'add_project.html', context)


def taskprojects(request, project_id):
    project = get_object_or_404(Projects, id=project_id)

    entries = project.taskproject.all()
    context = {'project': project, 'entries': entries}
    return render(request, 'taskprojects.html', context)


@require_POST
def toggle(request, entry_id):
    task = get_object_or_404(TaskProject, id=entry_id)
    task.done = not task.done
    task.save()
    return redirect('todo_app:taskprojects', task.project_id)  # возвращаемся в проект этой задачи


def addtaskproject(request, entry_id):
    project = get_object_or_404(Projects, id=entry_id)
    if request.method == "POST":
        form = TaskpForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.project = project
            task.save()
            return redirect('todo_app:taskprojects', project.id)
    else:
        form = TaskpForm()
    context = {'form': form, 'project': project}

    return render(request, "add_taskproject.html", context)