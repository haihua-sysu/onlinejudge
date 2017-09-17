from django.db import models
from django.contrib.auth.models import User
from taggit.managers import TaggableManager

class Handle(models.Model):
    #include username, password, email, priviledge, is_enabled, register_time(date_joined), last_time_login
    user = models.ForeignKey(User, unique = True)
    signature = models.CharField(max_length = 128, blank = True)
    #enable = models.BooleanField(default = True)
    solved = models.IntegerField(default = 0)
    submited = models.IntegerField(default = 0)
    realname = models.CharField(max_length = 64, blank = True)
    headurl = models.CharField(max_length = 256)
    school = models.CharField(max_length = 128, blank = True)
    grade = models.CharField(max_length = 128, blank = True)
    #reg_time = models.DateField(blank = True)

    def __unicode__(self):
        return self.user.username
