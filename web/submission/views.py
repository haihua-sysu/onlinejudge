#!/usr/bin/env python
# coding: utf-8
from django.core.context_processors import csrf
from django.template import Template, Context, RequestContext
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from submission.models import Submission
from submission.forms import SourceCodeForm
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.utils import timezone

from ojutility.func import *
from problemset.models import Problem
from handle.models import Handle
from contest.models import Contest, ContestProblem
import json, base64

@login_required(login_url = '/handle/login/')
def submission(request, page_id):
    #page_id = int(page_id)
    #if page_id <= 0: page_id = 1
    #min_sid = (page_id - 1) * 20
    #max_sid = min(page_id * 20, Submission.objects.count())
    #submissionList = Submission.objects.all()[min_sid : max_sid]
    #return render_to_response('submission.html', locals())

    submissionList = Submission.objects.filter(cid = 0)
    context = {'submissionList': submissionList}
    context.update(csrf(request))
    return render_to_response('submission.html', context, context_instance = RequestContext(request))

def _get_solved_submission(pid):
    submission = Submission.objects.filter(cid = 0, pid = pid, status = 1).order_by('run_time', 'memory')
    return submission 

def _get_user_submission(pid, user):
    submission = Submission.objects.filter(cid = 0, pid = pid, user = user)
    return submission 

def showSubmission(request, submissionList):
    context = {'submissionList' : submissionList}
    return render_to_response('submission.html', context, context_instance = RequestContext(request))

def problemSolvedSubmission(request, pid):
    submissionList = _get_solved_submission(pid)
    return showSubmission(request, submissionList)

def problemSubmission(request, pid):
    submissionList = Submission.objects.filter(cid = 0, pid = pid)
    return showSubmission(request, submissionList)

@login_required(login_url = '/handle/login/')
def userSubmission(request, pid):
    submissionList = _get_user_submission(pid, request.user)
    return showSubmission(request, submissionList)

@login_required(login_url = '/handle/login/')
def viewsource(request, sid):
    submission = get_object_or_404(Submission, sid = sid)
    if not request.user.is_superuser and (submission.cid == 0 and isRunningContestProblem(submission.pid)):
        return printError('you can not view this source because of running contest problem')

    if not request.user.is_superuser and submission.user != request.user:
        return printError('you have no privilege to view this source code')

    return render_to_response('viewsource.html', locals())

@login_required(login_url = '/handle/login/')
def viewdetail(request, sid):
    submission = get_object_or_404(Submission, sid = sid)
    if submission.user != request.user and not request.user.is_superuser:
        return printError('you have no privilege to view this judge detail')

    try:
        detail = eval(json.loads(json.dumps(submission.judge_detail)))
    except:
        detail = {}

    sid = submission.sid
    if detail.has_key('allres'):
        alldetails = detail['allres']
    else:
        alldetails = {}
    if detail.has_key('score'):
        score = detail['score']
    else:
        score = 0
    if detail.has_key('message'):
        compile_message = base64.b64decode(detail['message']).replace('\n', '<br/>')
    return render_to_response('viewdetail.html', locals())


# todo: 提交代码的时候在对应用户的submited_count + 1
@login_required(login_url = '/handle/login/')
def submitcode(request):
    if request.method == 'POST':
        source_code = SourceCodeForm(request.POST)
        if source_code.is_valid():
            data = source_code.cleaned_data
            cid =int(data['cid'])
            if cid != 0:
                contest = get_object_or_404(Contest, cid = cid)
                now = timezone.now()
                st = contest.start_time
                ed = contest.end_time
                print now, st, ed
                if st > now:
                    return printError('Contest Not Start')
                if now > ed:
                    return printError('Contest alreadly finished')

            submission = Submission(
                user = request.user,
                cid = data['cid'],
                pid_id = data['pid'],
                code = data['code'],
                language = data['language'],
                submited_time = datetime.now(),
                status = 0,
                judge_result = 'Pending',
                code_length = len(data['code'])
            )
            submission.code_length = len(submission.code)
            submission.save()

            problem = Problem.objects.get(pid = data['pid'])
            problem.submited += 1
            problem.save()

            user = Handle.objects.get(user = request.user)
            user.submited += 1
            user.save()

            if int(data['cid']) != 0:
                return HttpResponseRedirect('/contest/' + str(data['cid']) + '/submission')

    return HttpResponseRedirect('/submission/1')
