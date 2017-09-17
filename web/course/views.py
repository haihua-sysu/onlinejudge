#!/usr/bin/env python
# coding: utf-8

from django.core.context_processors import csrf
from django.template import Context, RequestContext
from django.http import  HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

from datetime import datetime
from contest.models import Contest, ContestProblem
from submission.models import Submission
from course.models import Course, CourseRegister
from ojutility.func import *
from handle.models import User

# course must be Course Object
def isCourseRegister(course, user):
    if user == course.creater: return True
    info = CourseRegister.objects.filter(courseid = course, user = user)
    if len(info) == 0: return False
    return info[0].verification

def registerCourse(request, courseid):
    course = get_object_or_404(Course, courseid = courseid)
    reg = CourseRegister.objects.filter(courseid = course, user = request.user)
    if len(reg) == 0:
        reg = CourseRegister(courseid = course, user = request.user)
        reg.save()
        return printMessage('Register success, please contact the course manager ** %s ** to accept your register request' % course.creater)
    else:
        if reg[0].verification:
            return printMessage('You had accepted by course manager ** %s **' % course.creater)
        else:
            return printMessage('Please wait for miniute, or contact the course manager ** %s **' % course.creater)

    return printMessage('Register success, please contact the course manager ** %s ** to accept your register request' % course.creater)

def viewRegisterList(request, courseid):
    course = get_object_or_404(Course, courseid = courseid)
    if request.user != course.creater:
        return printError('You have no privilege to view the register list')
    reglist = CourseRegister.objects.filter(courseid = course)
    context = {'course' : course, 'reglist' : reglist, 'is_courseManager' : course.creater == request.user}
    return render_to_response('registerlist.html', context, context_instance = RequestContext(request))

def regManager(request, courseid):
    course = get_object_or_404(Course, courseid = courseid)
    if request.user != course.creater:
        return printError('You have no privilege to view the register list')
    if request.method == 'GET':
        try:
            opt = request.GET['opt']
            user = get_object_or_404(User, username = request.GET['user'])
            print opt, user, opt == 'accept'
            info = CourseRegister.objects.filter(courseid = course, user = user)[:1][0]
            info.verification = opt == 'accept'
            info.save()
            return HttpResponseRedirect('/courselist/course/%d/registerlist/' % int(courseid))
        except:
            return printError('Unknown Error')

    return printError('No POST method implement')

def showCourseList(request):
    courselist = Course.objects.all()
    context = {'courselist': courselist}
    return render_to_response('courselist.html', context, context_instance = RequestContext(request))

def showCourse(request, courseid):
    course = get_object_or_404(Course, courseid = courseid)
    if not isCourseRegister(course, request.user):
        return printError('Please register the course and contact the course manager ** %s **' % course.creater)

    is_courseManager = request.user == course.creater
    contestlist = Contest.objects.filter(courseid = courseid)
    context = {'course' : course, 'contestlist' : contestlist, 'is_courseManager' : is_courseManager}
    return render_to_response('course.html', context, context_instance = RequestContext(request))
