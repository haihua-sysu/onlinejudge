from django.shortcuts import render_to_response
from django.template import RequestContext

def _printError(request, errormsg):
    context = {'errormsg' : errormsg}
    return render_to_response('errormsg.html', context, context_instance = RequestContext(request))

def _printMessage(request, message):
    context = {'message' : message}
    return render_to_response('message.html', context, context_instance = RequestContext(request))

def _isRunningContest(contest):
    now = datetime.now()
    start_time = contest.start_time.replace(tzinfo = None)
    end_time = contest.end_time.replace(tzinfo = None)
    return start_time <= now and now <= end_time

def _isRunningContestProblem(pid):
    contestlist = [x.cid for x in ContestProblem.objects.filter(pid = pid)]
    for contest in contestlist:
        if isRunningContest(contest):
            return True

    return False


