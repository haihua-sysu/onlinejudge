#!/usr/bin/env python
# coding: utf-8

from django.core.context_processors import csrf
from django.template import Template, Context, RequestContext
from django.shortcuts import render
from handle.models import Handle
from django.shortcuts import render_to_response

def showRank(request):
    ranklist = Handle.objects.all().order_by('-solved')
    context = {'ranklist': ranklist}
    context.update(csrf(request))
    return render_to_response('ranklist.html', context, context_instance = RequestContext(request))

