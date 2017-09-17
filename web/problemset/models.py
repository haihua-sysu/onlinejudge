from django.db import models
from handle.models import Handle
from django.contrib.auth.models import User
from taggit.managers import TaggableManager

class Problem(models.Model):
    pid = models.IntegerField(unique = True)

    title = models.CharField(max_length = 64)
    problem_description = models.TextField()
    input_description = models.TextField()
    output_description = models.TextField()
    input_sample = models.TextField()
    output_sample = models.TextField()
    hint = models.TextField(blank = True)
    source = models.CharField(max_length = 64, blank = True)
    tags = TaggableManager()
    solved = models.IntegerField(default = 0)
    submited = models.IntegerField(default = 0)

    time_limit = models.IntegerField(default = 1000)
    memory_limit = models.IntegerField(default = 32767)

    creater = models.ForeignKey(User)
    is_showed = models.BooleanField(default = False)
    is_contestproblem = models.BooleanField(default = False)

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ['pid']
