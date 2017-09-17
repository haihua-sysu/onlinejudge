from django.template import Template, Context
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth.models import Permission
from django.contrib.auth.models import User

def index(request):
	user = request.user
	return render_to_response('index.html', locals())

# Create your views here.
