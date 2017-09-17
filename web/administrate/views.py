#!/usr/bin/env python
# coding: utf-8

import os
from datetime import datetime, timedelta

from django.core.context_processors import csrf
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.contrib import auth
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import permission_required
from django.template import RequestContext
from django.db.models import Max
from django.conf import settings as _settings

from problemset.models import Problem
from contest.models import Contest, ContestProblem
from course.models import Course
from administrate.forms import ProblemForm, CourseForm, ContestForm
from ojutility.func import printError
from handle.models import Handle

def addTag(problem, tags):
    tags = [x.strip() for x in tags.split(',')]
    for tag in tags:
        problem.tags.add(tag)
    problem.save()

def addDataFile(pid, inputfiles, outputfiles):
    print inputfiles, outputfiles
    for f in inputfiles:
        filepath = "%s/%d/%s" % (_settings.TESTDATA_DIR, pid, f.name)
        
        filehandle = open(filepath, "wb+")
        for chunk in f.chunks():
            filehandle.write(chunk)
        filehandle.close()
 
    for f in outputfiles:
        filepath = "%s/%d/%s" % (_settings.TESTDATA_DIR, pid, f.name)
        filehandle = open(filepath, "wb+")
        for chunk in f.chunks():
            filehandle.write(chunk)
        filehandle.close()

# todo: 需要添加测试数据文件夹, 如果不是超级用户，仅提示不是admin，不需要重定向到登录
#permission_required("problemset.can_add_problem", login_url = "/handle/login")
def addProblem(request):
    if not request.user.is_superuser:
        return printError('You have no permission to this page, please contact administration')

    form = ProblemForm()
    errors = []
    if request.method == "POST":
        inputfiles = request.FILES.getlist('inputfiles')
        outputfiles = request.FILES.getlist('outputfiles')
        form = ProblemForm(request.POST)
        pid = Problem.objects.all().aggregate(Max('pid'))['pid__max']
        if pid == None:
            pid = 1000
        else:
            pid = pid + 1
        if form.is_valid():
            data = form.cleaned_data
            problem = Problem(
                pid = pid,
                title = data['title'],
                problem_description = data['problem_description'],
                input_description = data['input_description'],
                output_description = data['output_description'],
                input_sample = data['input_sample'],
                output_sample = data['output_sample'],
                hint = data['hint'],
                source = data['source'],
                time_limit = data['time_limit'],
                memory_limit = data['memory_limit'],
                is_showed = True,
                creater = request.user,
            )
            problem.save()

            addTag(problem, data['tag'])

            #data_dir = OJ_DATA_DIR + str(problem.pid)
            #cmd = "mkdir " + data_dir
            #os.system(cmd)
            #sample_input_file = data_dir + '/sample.in'
            #sample_output_file = data_dir + '/sample.out'
            #f = open(sample_input_file, 'w')
            #f.write(data['input_sample'])
            #f.close()
            #f = open(sample_output_file, 'w')
            #f.write(data['output_sample'])
            #f.close()

            cmd = "mkdir %s/%d" % (_settings.TESTDATA_DIR, pid)
            os.system(cmd)
            addDataFile(pid, inputfiles, outputfiles)

            return HttpResponseRedirect("/administrate/viewproblemlist")

    context = {"form" : form, "errors": errors}
    context.update(csrf(request))
    return render_to_response("addproblem.html", context, context_instance = RequestContext(request))

def addCourse(request):
    if not request.user.is_superuser:
        return printError('You have no permission to this page, please contact administration')
    errors = []
    form = CourseForm()
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            course = Course(title = data['title'], creater = request.user)
            course.save()
            return HttpResponseRedirect('/courselist/')
    context = {'form' : form, 'errors' : errors}
    return render_to_response('addcourse.html', context, context_instance = RequestContext(request))

def hasPrivilageAddContest(user, courseid):
    course = Course.objects.filter(courseid = courseid)
    if len(course) == 0:
        return False
    course = course[0]
    return course.creater == user

def addContest(request):
    if not request.user.is_superuser:
        return printError('You have no permission to this page, please contact administration')
    form = ContestForm()
    errors = []
    courseid = 0
    if request.method == "POST":
        courseid = request.POST['courseid']
        form = ContestForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            courseid = data['courseid']
            course = get_object_or_404(Course, courseid = courseid)
            if not hasPrivilageAddContest(request.user, courseid):
                return HttpResponseRedirect("/")

            contest = Contest(
                title = data['title'],
                creater = request.user,
                start_time = data['start_time'],
                end_time = data['end_time'],
                courseid =  course
            )
            contest.save()

            problemList = data['problem_list'].split(',')
            for p in problemList:
                temp = Problem.objects.filter(pid = p)
                if len(temp) == 0:
                    return printError("problem ** %d ** is not exists" % int(p))
                relation = ContestProblem.objects.filter(cid = contest, pid = Problem.objects.get(pid = int(p)))
                if len(relation) == 0:
                    relation = ContestProblem(cid = contest, pid = Problem.objects.get(pid = int(p)))
                    relation.save()

            return HttpResponseRedirect("/courselist/course/%d" % int(courseid))

    elif request.method == 'GET':
        try:
            courseid = request.GET['courseid']
        except:
            return printError('You should add contest in course page')

        if not hasPrivilageAddContest(request.user, courseid):
            return HttpResponseRedirect("/")


    course = get_object_or_404(Course, courseid = courseid)
    context = {"form" : form, "errors": errors, 'course' : course}
    return render_to_response("addcontest.html", context, context_instance = RequestContext(request))

# todo: 需要优化数据库访问条目，如果不是超级用户，仅提示不是admin，不需要重定向到登录
# @permission_required("problemset.can_add_problem", login_url = "/handle/login")
def viewProblemlist(request, page_id):
    if not request.user.is_superuser:
        return printError('You have no permission to this page, please contact administration')
    #page_id = int(page_id)
    #if page_id <= 0: page_id = 1
    #min_pid = (page_id - 1) * 20
    #max_pid = min(page_id * 20, Problem.objects.count())
    #if min_pid > max_pid: min_pid = max_pid
    #problem = Problem.objects.filter(pid__gte = min_pid, pid__lte = max_pid).order_by("-pid")
    problemset = Problem.objects.all().order_by("-pid")
    context = {"problemset" : problemset}
    context.update(csrf(request))
    return render_to_response("viewproblemlist.html", context, context_instance=RequestContext(request))

# todo: 需要优化数据库访问条目
#@permission_required("problemset.can_add_problem", login_url = "/handle/login")
def editProblem(request, pid):
    if not request.user.is_superuser:
        return printError('You have no permission to this page, please contact administration')

    pid = int(pid)
    problem = get_object_or_404(Problem, pid = pid)
    title = problem.title
    if request.method == "GET":
        tags = problem.tags.all()
        tags = [str(x) for x in tags]
        tags = ','.join(tags)
        return render_to_response("edit.html", locals(), context_instance = RequestContext(request))
    elif request.method == "POST":
        form = ProblemForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            problem.title = data['title']
            problem.description = data['problem_description']
            problem.input_description = data['input_description']
            problem.output_description = data['output_description']
            problem.input_sample = data['input_sample']
            problem.output_sample = data['output_sample']
            problem.hint = data['hint']
            problem.time_limit = data['time_limit']
            problem.memory_limit = data['memory_limit']
            problem.source = data['source']
            problem.tags.clear()
            problem.save()
            addTag(problem, data['tag'])

            inputfiles = request.FILES.getlist('inputfiles')
            outputfiles = request.FILES.getlist('outputfiles')
            addDataFile(pid, inputfiles, outputfiles)

            return HttpResponseRedirect("/administrate/viewproblemlist/")
        else:
            return printError('form is invalid')

    context = {"pid": pid, "form": form, "title" : title}
    return render_to_response("edit.html", context, context_instance=RequestContext(request))

def viewUserlist(request):
    if not request.user.is_superuser:
        return printError('You have no permission to this page, please contact administration')

    handle = Handle.objects.all().order_by('-user')
    context = {"handle" : handle}
    return render_to_response("viewuserlist.html", context, context_instance = RequestContext(request))

def changeStatus(request, pid):
    if not request.user.is_superuser:
        return printError('You have no permission to this page, please contact administration')
    problem = get_object_or_404(Problem, pid = pid)
    problem.is_showed = not problem.is_showed
    problem.save()
    return HttpResponseRedirect("/administrate/viewproblemlist/")

def changeUserStatus(request, username):
    if not request.user.is_superuser:
        return printError('You have no permission to this page, please contact administration')
    try:
        user = User.objects.get(username = username)
        if user.is_superuser:
            return printError('You have not permission to change an Admin\' status')
        user.is_active = not user.is_active
        user.save()
    except:
        return printError('An Error Occurrence')
    return HttpResponseRedirect("/administrate/viewuserlist")

