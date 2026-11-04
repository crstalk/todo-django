from django.conf import settings
from django.db import models

# Create your models here.
class Project(models.Model):
    # settings.AUTH_USER_MODEL, а не User: так модель сама подхватит нашего user_auth.User
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    date_added = models.DateTimeField(auto_now_add=True)  # аттрибут в скобках приказывает dj ставить нынынешнюю дату

    def __str__(self):
        return self.name

class Task(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    date_added = models.DateTimeField(auto_now_add=True)# аттрибут в скобках приказывает dj ставить нынынешнюю дату
    date_due = models.DateField(null=True, blank=True)
    done = models.BooleanField(default=False)
    project = models.ForeignKey(Project,on_delete=models.CASCADE, related_name='tasks',null=True,blank=True)

    def __str__(self):
        return self.name
