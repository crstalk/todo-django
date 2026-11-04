from todo_app.models import Task


def active_tasks_count(request):
    """Количество невыполненных задач — для бейджа в навбаре."""
    if not request.user.is_authenticated:
        return {}
    return {'active_tasks_count': Task.objects.filter(owner=request.user, done=False).count()}
