from ojutility import *
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from datetime import datetime
from django.conf import settings as _settings
from datetime import datetime, tzinfo,timedelta

from contest.models import ContestProblem

def printError(errormsg):
    return redirect(reverse('ojutility.views._printError', args = [errormsg]))

def printMessage(message):
    return redirect(reverse('ojutility.views._printMessage', args = [message]))

def isRunningContest(contest):
    now = int(datetime.now().strftime('%s'))
    start_time = getLocalTime(contest.start_time)
    end_time = getLocalTime(contest.end_time)
    return start_time <= now and now <= end_time

def isRunningContestProblem(pid):
    contestlist = [x.cid for x in ContestProblem.objects.filter(pid = pid)]
    for contest in contestlist:
        if isRunningContest(contest):
            return True

    return False

def getLocalTime(time):
    return int(time.strftime('%s')) + 8 * 60 * 60
