from django.db import models
from handle.models import Handle
from problemset.models import Problem
from django.contrib.auth.models import User

class Submission(models.Model):
    sid = models.AutoField('sid', primary_key = True)
    user = models.ForeignKey(User)
    pid = models.ForeignKey(Problem, "pid")
    cid = models.IntegerField(default = 0)

    code = models.TextField()
    language = models.IntegerField(default = 0)
    status = models.IntegerField(default = 0)
    run_time = models.IntegerField(default = 0)
    judge_result = models.CharField(max_length = 128, default = 'Pending')
    judge_detail = models.TextField() #json filed
    memory = models.IntegerField(default = 0)
    code_length = models.IntegerField(default = 0)
    submited_time = models.DateTimeField()

    def __unicode__(self):
        return self.pid.title

    class Meta:
        ordering = ['-sid']
