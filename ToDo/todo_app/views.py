from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, F, Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from todo_app.forms import TaskForm, ProjectForm
from todo_app.models import Task, Project
from user_auth.forms import EditProfile

# Везде фильтруем по owner=request.user, чтобы пользователь видел и менял только своё.


def redirect_back(request, *default):
    """Вернуться на страницу из поля next (если оно безопасное), иначе на default."""
    nxt = request.POST.get('next') or request.GET.get('next')
    if nxt and url_has_allowed_host_and_scheme(nxt, allowed_hosts={request.get_host()},
                                               require_https=request.is_secure()):
        return redirect(nxt)
    return redirect(*default)


def split_tasks(tasks):
    """Разбить задачи на активные/выполненные и посчитать прогресс — общий кусок контекста."""
    tasks = list(tasks)
    active = [t for t in tasks if not t.done]
    done = [t for t in tasks if t.done]
    return {
        'active_tasks': active,
        'done_tasks': done,
        'total': len(tasks),
        'progress': round(len(done) * 100 / len(tasks)) if tasks else 0,
        'today': timezone.localdate(),
    }


# Сначала невыполненные, внутри — по сроку (без срока в конце), потом новые сверху
TASK_ORDER = ('done', F('date_due').asc(nulls_last=True), '-date_added')


# ---------- Задачи ----------

@login_required
def index(request):
    tasks = Task.objects.filter(owner=request.user, project__isnull=True).order_by(*TASK_ORDER)
    return render(request, 'index.html', split_tasks(tasks))


@login_required
def today(request):
    today_date = timezone.localdate()
    mine = Task.objects.filter(owner=request.user).select_related('project')
    # Задачи на сегодня (включая проектные) + невыполненные просроченные
    context = split_tasks(mine.filter(date_due=today_date).order_by('done', '-date_added'))
    context['overdue_tasks'] = mine.filter(date_due__lt=today_date, done=False).order_by('date_due')
    return render(request, 'today.html', context)


@login_required
def add_task(request):
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.owner = request.user
            task.save()
            messages.success(request, f'Задача «{task}» добавлена')
            return redirect_back(request, 'todo_app:tasks')
    else:
        form = TaskForm()
    return render(request, 'add_task.html', {'form': form})


@login_required
@require_POST
def toggle(request, entry_id):
    task = get_object_or_404(Task, id=entry_id, owner=request.user)
    task.done = not task.done
    task.save(update_fields=['done'])
    if task.project_id:
        return redirect_back(request, 'todo_app:taskprojects', task.project_id)
    return redirect_back(request, 'todo_app:tasks')


@login_required
@require_POST
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, owner=request.user)
    task.delete()
    messages.success(request, f'Задача «{task}» удалена')
    return redirect_back(request, 'todo_app:tasks')


# ---------- Проекты ----------

@login_required
def projects(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            messages.success(request, f'Проект «{project}» создан')
            return redirect('todo_app:projects')
    else:
        form = ProjectForm()

    projects = (Project.objects.filter(owner=request.user)
                .annotate(total=Count('tasks'), done=Count('tasks', filter=Q(tasks__done=True)))
                .order_by('-date_added'))
    for p in projects:
        p.progress = round(p.done * 100 / p.total) if p.total else 0
    return render(request, 'projects.html', {'form': form, 'projects': projects})


@login_required
def add_project(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            messages.success(request, f'Проект «{project}» создан')
            return redirect('todo_app:taskprojects', project.id)
    else:
        form = ProjectForm()
    return render(request, 'add_project.html', {'form': form})


@login_required
@require_POST
def delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id, owner=request.user)
    project.delete()  # задачи проекта удалятся каскадом
    messages.success(request, f'Проект «{project}» удалён')
    return redirect('todo_app:projects')


@login_required
def taskprojects(request, project_id):
    project = get_object_or_404(Project, id=project_id, owner=request.user)
    context = split_tasks(project.tasks.order_by(*TASK_ORDER))
    context['project'] = project
    return render(request, 'taskprojects.html', context)


@login_required
def addtaskproject(request, entry_id):
    project = get_object_or_404(Project, id=entry_id, owner=request.user)
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.owner = request.user
            task.project = project
            task.save()
            messages.success(request, f'Задача «{task}» добавлена в проект')
            return redirect('todo_app:taskprojects', project.id)
    else:
        form = TaskForm()
    return render(request, "add_taskproject.html", {'form': form, 'project': project})


# ---------- Профиль ----------

@login_required
def profile(request):
    # instance=request.user — форма редактирует существующего пользователя, а не создаёт нового
    if request.method == "POST":
        form = EditProfile(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль обновлён')
            return redirect('todo_app:profile')
    else:
        form = EditProfile(instance=request.user)

    tasks = Task.objects.filter(owner=request.user)
    total = tasks.count()
    done = tasks.filter(done=True).count()
    progress = round(done * 100 / total) if total else 0
    context = {
        'form': form,
        'tasks_total': total,
        'tasks_done': done,
        'tasks_overdue': tasks.filter(done=False, date_due__lt=timezone.localdate()).count(),
        'projects_total': Project.objects.filter(owner=request.user).count(),
        'progress': progress,
        'ring_offset': 100 - progress,  # длина окружности кольца ≈ 100
    }
    return render(request, 'profile.html', context)
