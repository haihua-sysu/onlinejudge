#!/usr/bin/env python
# coding: utf-8

from django.core.context_processors import csrf
from django.template import Context, RequestContext
from django.http import  HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.conf import settings as _settings

from datetime import datetime
from contest.models import Contest, ContestProblem
from submission.models import Submission
from course.models import CourseRegister
from ojutility.func import *
from course.views import isCourseRegister
from problemset.models import Problem
import json

def contestNotStart(contest):
    now = int(datetime.now().strftime('%s'))
    start_time = getLocalTime(contest.start_time)
    return now < start_time

def canShowContest(cid, user):
    contest = get_object_or_404(Contest, cid = cid)
    if user != contest.creater and contestNotStart(contest):
        return printError('Contest Not Start')
    if not isCourseRegister(contest.courseid, user):
        return printError('You have no privilege to view this contest')
    return True

def showContest(request, cid):
    res = canShowContest(cid, request.user)
    if res != True: return res
    contest = get_object_or_404(Contest, cid = cid)
    problem = ContestProblem.objects.filter(cid = cid)
    context = {'contest': contest, 'problem': problem}
    return render_to_response('contest.html', context, context_instance = RequestContext(request))

def showContestProblem(request, cid, pid):
    res = canShowContest(cid, request.user)
    if res != True: return res
    contest = get_object_or_404(Contest, cid = cid)
    problem = get_object_or_404(Problem, pid = pid)
    isok = get_object_or_404(ContestProblem, cid = contest, pid = problem)
    context = {'contest': contest, 'problem': problem}
    context.update(csrf(request))
    return render_to_response('contestproblem.html', context, context_instance = RequestContext(request))

def showSubmission(request, cid):
    res = canShowContest(cid, request.user)
    if res != True: return res

    contest = get_object_or_404(Contest, cid = cid)

    if not request.user.is_authenticated():
        submissionList = []
    else:
        if request.user.is_superuser:
            submissionList = Submission.objects.filter(cid = cid)
        else:
            submissionList = Submission.objects.filter(cid = cid, user = request.user)

    context = {'contest': contest, 'submissionList': submissionList}
    return render_to_response('contest_submission.html', context, context_instance = RequestContext(request))

def showProblemSubmission(request, cid, pid):
    res = canShowContest(cid, request.user)
    if res != True: return res

    contest = get_object_or_404(Contest, cid = cid)
    if not request.user.is_authenticated():
        submissionList = []
    else:
        submissionList = Submission.objects.filter(cid = cid, user = request.user, pid = pid)

    context = {'contest': contest, 'submissionList': submissionList}
    return render_to_response('contest_submission.html', context, context_instance = RequestContext(request))

def solvedCount(val):
    return val[1]

def SCORE(val):
    return val[1]

def showOIStanding(request, cid):
    res = canShowContest(cid, request.user)
    if res != True: return res

    contest = get_object_or_404(Contest, cid = cid)
    problem = ContestProblem.objects.filter(cid = cid)
    submissionList = Submission.objects.filter(cid = cid).order_by('user')

    statistics = {}
    rankList = {}
    # status == 1 mean Accepted
    for submission in submissionList:
        detail = submission.judge_detail
        try:
            detail = eval(json.loads(json.dumps(detail)))
            print detail['score']
        except:
            detail = {'score' : 0}

        score = int(detail['score'])
        user_pid = (submission.user, submission.pid)
        if statistics.has_key(user_pid):
            statistics[user_pid] = max(statistics[user_pid], score)
        else:
            statistics[user_pid] = score

    for item in statistics.items():
        if not rankList.has_key(item[0][0]):
            rankList[item[0][0]] = 0
        rankList[item[0][0]] = rankList[item[0][0]] + item[1]

    rankList = rankList.items()
    rankList.sort(key = SCORE, reverse = True)

    context = {'statistics': statistics, 'rankList': rankList, 'problem': problem, 'contest': contest}
    context.update(csrf(request))
    return render_to_response('oistanding.html', context, context_instance = RequestContext(request))

def showACMStanding(request, cid):
    res = canShowContest(cid, request.user)
    if res != True: return res

    contest = get_object_or_404(Contest, cid = cid)
    problem = ContestProblem.objects.filter(cid = cid)
    submissionList = Submission.objects.filter(cid = cid).order_by('user')

    statistics = {}
    rankList = {}
    # status == 1 mean Accepted
    for submission in submissionList:
        status = submission.status
        if status != 1: status = 0
        user_pid = (submission.user, submission.pid)
        if statistics.has_key(user_pid):
            statistics[user_pid] = statistics[user_pid] | status
        else:
            statistics[user_pid] = status

    for item in statistics.items():
        if not rankList.has_key(item[0][0]):
            rankList[item[0][0]] = 0
        if item[1] == 1:
            rankList[item[0][0]] = rankList[item[0][0]] + 1

    rankList = rankList.items()
    rankList.sort(key = solvedCount, reverse = True)

    context = {'statistics': statistics, 'rankList': rankList, 'problem': problem, 'contest': contest}
    context.update(csrf(request))
    return render_to_response('standing.html', context, context_instance = RequestContext(request))
