#!/usr/bin/env python
# coding: utf-8

from django import forms
from django.core.exceptions import ValidationError

from problemset.models import Problem

YES_OR_NO = (('True', 'YES',), ('False', 'NO',),)

# todo: 添加css
class ProblemForm(forms.Form):
    title = forms.CharField(widget = forms.TextInput())
    time_limit = forms.IntegerField()
    memory_limit = forms.IntegerField()
    tag = forms.CharField(widget = forms.TextInput(), required = False)
    problem_description = forms.CharField(widget = forms.Textarea())
    input_description = forms.CharField(widget = forms.Textarea(), required = False)
    output_description = forms.CharField(widget = forms.Textarea(), required = False)
    input_sample = forms.CharField(widget = forms.Textarea())
    output_sample = forms.CharField(widget = forms.Textarea())
    hint = forms.CharField(widget = forms.Textarea(), required = False)
    source = forms.CharField(required = False)


def validate_problemlist(problem_list):
    problem_list = problem_list.split(',')
    for val in problem_list:
        if not val.isdigit():
            raise ValidationError('problem id must be non-negative integer split by english comma')

    for val in problem_list:
        print val
        p = Problem.objects.filter(pid = int(val))
        if len(p) == 0: raise ValidationError('some problems not in problemlist')

class ContestForm(forms.Form):
    courseid = forms.IntegerField()
    title = forms.CharField(max_length = 128)
    start_time = forms.DateTimeField()
    end_time = forms.DateTimeField()
    problem_list = forms.CharField(max_length = 128, validators = [validate_problemlist])

class CourseForm(forms.Form):
    title = forms.CharField(max_length = 128)
