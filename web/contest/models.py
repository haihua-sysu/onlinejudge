#/usr/bin/env python
# coding: utf-8

from django.db import models
from django.contrib.auth.models import User

from handle.models import Handle
from problemset.models import Problem
from course.models import Course

# 需要修改时间和模式那一块
# OI model
class Contest(models.Model):
    cid = models.AutoField("cid", primary_key = True)
    title = models.CharField(max_length = 128)
    creater = models.ForeignKey(User)
    courseid = models.ForeignKey(Course)

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ['-cid']

class ContestProblem(models.Model):
    cid = models.ForeignKey(Contest)
    pid = models.ForeignKey(Problem)
