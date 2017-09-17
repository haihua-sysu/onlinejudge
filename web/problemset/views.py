from django.core.context_processors import csrf
from django.template import Template, Context
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required, permission_required
from django.template import RequestContext
from django.contrib.auth.models import User
from django.contrib import auth


from stars.models import Star, Note
from problemset.models import Problem
from ojutility.func import *

@login_required(login_url = '/handle/login/')
def index(request):
    problemset = Problem.objects.filter(is_showed = True)
    return render_to_response('show_problemset.html', locals(), context_instance = RequestContext(request))

@login_required(login_url = '/handle/login/')
def show_problem(request, pid):
    problem = get_object_or_404(Problem, pid = pid, is_showed = True)
    context = {'problem': problem}
    context.update(csrf(request))
    return render_to_response('show_problem.html', context, context_instance=RequestContext(request))

@login_required(login_url = '/handle/login/')
def show_tagproblem(request, tag):
    problemset = Problem.objects.filter(tags__name__in=[tag])
    context = {'problemset': problemset}
    print len(problemset)
    return render_to_response('show_problemset.html', context, context_instance = RequestContext(request))

@login_required(login_url = '/handle/login/')
def show_problemset(request, page_id):
    problemset = Problem.objects.filter(is_showed = True)
    context = {'problemset': problemset}
    return render_to_response('show_problemset.html', context, context_instance = RequestContext(request))

@login_required(login_url = '/handle/login/')
def star_problem(request, pid):
    problem = get_object_or_404(Problem, pid = pid, is_showed = True)
    #user = auth.get_user(request)
    item = Star.objects.filter(user = request.user, pid = problem)
    if len(item) == 0:
        item = Star(user = request.user, pid = problem, value = 1)
    else:
        item = item[0]
        item.value = 1 - item.value
    item.save()
    return HttpResponseRedirect("/problemset/")

@login_required(login_url = '/handle/login/')
def show_star(request):
    star = Star.objects.filter(user = request.user, value = 1)
    problemset = [p.pid for p in star]
    context = {'problemset': problemset}
    return render_to_response('show_problemset.html', context, context_instance = RequestContext(request))

@login_required(login_url = '/handle/login/')
def note(request, pid):
    pid = get_object_or_404(Problem, pid = pid)
    note = Note.objects.filter(user = request.user, pid = pid)
    if len(note) == 0:
        note = Note(user = request.user, pid = pid, content = "")
    else:
        note = note[0]

    if request.method == "GET":
        if isRunningContestProblem(pid):
            return printError('you can not view this note because of running contest problem')

        context = {'note' : note}
        return render_to_response('note.html', context, context_instance = RequestContext(request))
    elif request.method == "POST":
        note.content = request.POST['note']
        note.save()
        return HttpResponseRedirect("/problemset/")

    return HttpResponseRedirect("/problemset/")
