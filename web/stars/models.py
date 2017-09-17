from django.db import models
from problemset.models import Problem
from django.contrib.auth.models import User

class Star(models.Model):
    user = models.ForeignKey(User)
    pid = models.ForeignKey(Problem)
    value = models.IntegerField(default = 0)

#should add to problem
class Note(models.Model):
    user = models.ForeignKey(User)
    pid = models.ForeignKey(Problem)
    content = models.TextField(blank = True)
