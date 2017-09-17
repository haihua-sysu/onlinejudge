from django import forms
from django.core.exceptions import ValidationError

from problemset.models import Problem
from contest.models import Contest

def validate_pid(pid):
    try: pid = int(pid)
    except:
        raise ValidationError('pid must be an integer')
    p = Problem.objects.filter(pid = pid)
    if not p:
        raise ValidationError('the problem is not exists')

def validate_cid(cid):
    try: cid = int(cid)
    except:
        raise ValidationError('no such conetst')
    if cid != 0:
        cid = Contest.objects.filter(cid = cid)
        if not cid:
            raise ValidationError('no such contest')

class SourceCodeForm(forms.Form):
    cid = forms.IntegerField(validators = [validate_cid])
    pid = forms.IntegerField(validators = [validate_pid])
    code = forms.CharField(widget = forms.Textarea)
    language = forms.CharField()
