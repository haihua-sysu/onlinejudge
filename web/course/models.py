#/usr/bin/env python
# coding: utf-8

from django.db import models
from django.contrib.auth.models import User

from handle.models import Handle
from problemset.models import Problem

class Course(models.Model):
    courseid = models.AutoField("courseid", primary_key = True)
    title = models.CharField(max_length = 128)
    creater = models.ForeignKey(User)

    class Meta:
        ordering = ['-courseid']

class CourseRegister(models.Model):
    courseid = models.ForeignKey(Course)
    user = models.ForeignKey(User)
    verification = models.BooleanField(default = False)
