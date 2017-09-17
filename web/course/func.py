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

def ErrorURLReverse(errormsg):
    return reverse('errmsg.views.printError', args = [errormsg])
