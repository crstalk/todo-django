from django.db import models

# Create your models here.

class Element(models.Model):
    name = models.CharField(max_length=100)
    date_added = models.DateTimeField(auto_now_add=True)
    data_due = models.DateField(null=True, blank=True)
    done = models.BooleanField(default=False)
    # аттрибут в скобках приказывает dj ставить нынынешнюю дату
    def __str__(self):
        return self.name

class Projects(models.Model):
    name = models.CharField(max_length=100)
    date_added = models.DateTimeField(auto_now_add=True)  # аттрибут в скобках приказывает dj ставить нынынешнюю дату


class TaskProject(models.Model):
    project = models.ForeignKey(Projects, on_delete=models.CASCADE,related_name='taskproject')
    name = models.CharField(max_length=100)
    done = models.BooleanField(default=False)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'taskprojects'
    def __str__(self):
        return self.name