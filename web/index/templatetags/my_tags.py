from django import template

from datetime import datetime
from submission.models import Submission
from problemset.models import Problem
from stars.models import Star
from django.contrib import auth
from ojutility.func import *
import json

register = template.Library()

@register.simple_tag
def user_handle_url(username):
    return '<a href="/handle/profile/%s"><span class="label label-info">%s</span></a>' % (username, username)

@register.simple_tag
def problemtag(pid):
    html = ''
    problem = Problem.objects.filter(pid = pid)[0]
    for tag in problem.tags.all():
        html += '<a href="/problemset/tag/%s"><span class="label label-info pull-right" style="margin-left:5px">%s</span></a>\n' % (tag, tag)
    return html

@register.simple_tag
def active(request, pattern):
    import re
    if re.search(pattern, request.path):
        return 'active'
    return ''

@register.simple_tag
def judge_result_label(judge_result):
    if judge_result == 'Accepted':
        return 'label label-success'
    if judge_result == 'Pending':
        return 'label label-primary'
    if judge_result == 'Compiled Error':
        return 'label label-warning'
    if judge_result == 'Judging':
        return 'label label-default'
    return 'label label-danger'

@register.simple_tag
def transTime(src_format, des_format, data):
    t = int(data) * 1.0
    if src_format == 'ms':
        t /= 1000
    if des_format == 's':
        return t
    if des_format == 'ms':
        t *= 1000
    return t

@register.simple_tag
def programming_language(lang_type):
    lang_type = int(lang_type)
    if lang_type == 0: return 'Pascal'
    if lang_type == 1: return 'C++'
    return 'Unknown'

@register.simple_tag
def contestCounter(cid, pid, countType):
    if countType == 'solved':
        return Submission.objects.filter(cid = cid, pid = pid, status = 1).count()
    elif countType == 'submited':
        return Submission.objects.filter(cid = cid, pid = pid).count()

    return 0

@register.simple_tag
def contestStatus(cid, start_time, end_time):
    cur_time = int(datetime.now().strftime('%s'))
    start_time = getLocalTime(start_time)
    end_time = getLocalTime(end_time)
    print cid, start_time, end_time, cur_time
    if cur_time < start_time:
        return 'Pending'
    elif cur_time > end_time:
        return 'Ended'
    else:
        return 'Running'

@register.simple_tag
def contestStatusLabel(cid, start_time, end_time):
    cur_time = int(datetime.now().strftime('%s'))
    start_time = getLocalTime(start_time)
    end_time = getLocalTime(end_time)
    print cid, start_time, cur_time, end_time

    if cur_time < start_time:
        return '<span class="label label-primary">Pending</span>'
    elif cur_time > end_time:
        return '<span class="label label-success">Ended</span>'
    else:
        return '<span class="label label-danger">Running</span>'

@register.simple_tag
def getArrayElement(array, index):
    return array[index]

# see contest/views.showStanding
@register.simple_tag
def getStatus(usersolved, problem, statistics):
    key = (usersolved[0], problem.pid)
    if not statistics.has_key(key):
        return 0
    else:
        return statistics[key]
    return 0

@register.simple_tag
def starStatus(request, pid):
    starstatus = "glyphicon glyphicon-star-empty"
    if not request.user.is_authenticated():
        return starstatus
    pid = Problem.objects.get(pid = pid)
    item = Star.objects.filter(user = request.user, pid = pid)
    if len(item) != 0:
        item = item[0]
        if item.value == 1: starstatus = "glyphicon glyphicon-star"
    return starstatus

@register.simple_tag
def judge_score(judge_detail):
    score = 0
    try:
        x = eval(json.loads(json.dumps(str(judge_detail))))
        score = x['score']
    except:
        pass
    return score

@register.simple_tag
def getUserTitle(username):
    try:
        user = auth.models.User.objects.get(username = username)
        if user.is_superuser:
            return 'Admin'
        else:
            return 'Normal User'
    except:
        return 'NULL'

@register.simple_tag
def getUserStatus(username):
    try:
        user = auth.models.User.objects.get(username = username)
        if user.is_active or user.is_superuser:
            return '<span class="label label-success">Enable</span>'
        else:
            return '<span class="label label-warning">Unable</span>'
    except:
        return '<span class="label label-warning">Unable</span>'

@register.simple_tag
def currentServerTime():
    return datetime.now()
