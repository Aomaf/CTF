# -*- encoding: utf-8 -*-

from django.shortcuts import render
from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from .models import Challenge, Contestant, Submission, Competition, Reference, Group
from django.db.models import Sum
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from django.contrib.auth.hashers import check_password
from datetime import datetime, timezone
from django.contrib import messages
import json, os, shutil, traceback

def __isMaintenanceMode(request):
    maintenance = False     # flag maintenance
    if request.user:
        check = User.objects.filter(id=request.user.id)
        if check and len(check)>=1:
            user = check.first()
            if maintenance == True and user.is_superuser: return False
    return maintenance

def index(request):
    try: return render(request, 'home/index.html')
    except:
        print(traceback.format_exc())
        if __isEnabledErrorPage: return HttpResponseRedirect('/pages')
        
@login_required(login_url="/login/")
def dashboard(request):
    try:
        user_ = User.objects.get(id=request.user.id)
        if __isMaintenanceMode(request) == True: return HttpResponseRedirect('home/construction.html')
        if __isNotValidProfile(user_) == True and not user_.is_superuser and not user_.is_staff:
            return HttpResponseRedirect('/pageuser')
        
        check = Contestant.objects.filter(user_id = request.user.id)
        if len(check) <= 0:
            if user_.is_superuser or user_.is_staff: Contestant.objects.create(user_id = request.user.id, is_user = False)
            else: Contestant.objects.create(user_id = request.user.id, is_user = True)
        cont = Contestant.objects.get(user_id = request.user.id)
        users1 = Contestant.objects.filter(is_user = True, user_scoreL1__gte = 1).order_by('-user_scoreL1').distinct()
        users2 = Contestant.objects.filter(is_user = True, user_scoreL2__gte = 1).order_by('-user_scoreL2').distinct()
        users3 = Contestant.objects.filter(is_user = True, user_scoreL3__gte = 1).order_by('-user_scoreL3').distinct()
        users4 = Contestant.objects.filter(is_user = True, user_scoreL4__gte = 1).order_by('-user_scoreL4').distinct()
        users5 = Contestant.objects.filter(is_user = True, user_scoreL5__gte = 1).order_by('-user_scoreL5').distinct()

        # personal stats
        params_user = {}
        params_user['user_submits'] = Submission.objects.filter(Q(contestant = cont) & Q(status = 1)).count()
        params_user['user_attempts'] = Submission.objects.filter(Q(contestant = cont) & ~Q(status = -1)).aggregate(sum=Sum('counter'))
        params_user['user_passed'] = Submission.objects.filter(contestant = cont, sum_result__gte=60).count()
        params_user['user_hundreds'] = Submission.objects.filter(contestant = cont, sum_result=100.0).count()
        params_user['user_ninetys'] = Submission.objects.filter(Q(contestant = cont) & Q(sum_result__gte=90) & Q(sum_result__lte=99)).count()
        params_user['user_eightys'] = Submission.objects.filter(Q(contestant = cont) & Q(sum_result__gte=80) & Q(sum_result__lte=89)).count()
        params_user['user_seventys'] = Submission.objects.filter(Q(contestant = cont) & Q(sum_result__gte=70) & Q(sum_result__lte=79)).count()
        params_user['user_sixtys'] = Submission.objects.filter(Q(contestant = cont) & Q(sum_result__gte=60) & Q(sum_result__lte=69)).count()
        max = 0
        if params_user['user_hundreds']>max: max = params_user['user_hundreds']
        if params_user['user_ninetys']>max: max = params_user['user_ninetys']
        if params_user['user_eightys']>max: max = params_user['user_eightys']
        if params_user['user_seventys']>max: max = params_user['user_seventys']
        if params_user['user_sixtys']>max: max = params_user['user_sixtys']
        
        # general stats
        params_general = {}
        params_general['hundreds'] = Submission.objects.filter(sum_result=100).count()
        params_general['ninetys'] = Submission.objects.filter(Q(sum_result__gte=90) & Q(sum_result__lte=99)).count()
        params_general['eightys'] = Submission.objects.filter(Q(sum_result__gte=80) & Q(sum_result__lte=89)).count()
        params_general['seventys'] = Submission.objects.filter(Q(sum_result__gte=70) & Q(sum_result__lte=79)).count()
        params_general['sixtys'] = Submission.objects.filter(Q(sum_result__gte=60) & Q(sum_result__lte=69)).count()
        params_general['all_submits'] = Submission.objects.filter(status = 1).count()
        params_general['all_solutions'] = Submission.objects.filter(Q(sum_result__gte=60)).count()
        params_general['full_solutions'] = Submission.objects.filter(sum_result=100).count()
        
        html_template = loader.get_template('home/dashboard.html')
        return HttpResponse(html_template.render({'segment': 'dashboard','users1': users1, 'users2': users2, 'users3': users3, 'users4': users4, 'users5': users5, 'params_user': params_user,'params_general':params_general, 'max': max}, request))
    except:
        print(traceback.format_exc())
        if __isEnabledErrorPage: return HttpResponseRedirect('/pages')    

def viewChallenges(request):
    try:
        if __isMaintenanceMode(request) == True: return HttpResponseRedirect('home/construction.html')
                
        challengeList = Challenge.objects.filter(Q(belongsToEvent__isnull=True) & ~Q(level='Placement'))
        nonContestants = Contestant.objects.filter(~Q(is_user = 1))
        nonContestants_ids = list(map(lambda x: x.id, nonContestants))
        for obj in challengeList:
            check = Submission.objects.filter(Q(challenge_id = obj.id) & Q(status=1)).exclude(contestant_id__in = nonContestants_ids).count()
            obj.submissions = check
            check = Submission.objects.filter(Q(challenge_id = obj.id) & Q(sum_result__gte=60)).exclude(contestant_id__in = nonContestants_ids).count()
            obj.passed = check
        levels = __getLevelList(with_p=False)
        belongsTo = None

        if request.method == "POST" and request.POST.get('level_select') != 'All':
            belongsTo = request.POST.get('level_select')
            challengeList = Challenge.objects.filter(Q(belongsToEvent__isnull=True) & Q(level=belongsTo))
            html_template = loader.get_template('home/challenges.html')
            return HttpResponse(html_template.render({'segment': 'challenges', 'challenges': challengeList, 'levels':levels,'belongsTo':belongsTo}, request))
        else:
            html_template = loader.get_template('home/challenges.html')
            return HttpResponse(html_template.render({'segment': 'challenges', 'challenges': challengeList, 'levels':levels}, request))
        
    except:
        print(traceback.format_exc())
        if __isEnabledErrorPage: return HttpResponseRedirect('/pages')

@login_required(login_url="/login/")
def addChallenge(request):
    try:
        user = User.objects.filter( Q(id=request.user.id) & ( Q(is_superuser=1) | Q(is_staff=1)))
        if len(user)>=1: user = user.first() 
        
        if user:
            try:
                start_date = end_date = None
                if request.method == "POST":
                    title = request.POST.get('title')
                    level = request.POST.get('level')
                    event = request.POST.get('event')
                    start_date = end_date = belongsTo = None
                    if event != 'None':
                        belongsTo = Competition.objects.get(title = str(event))
                        level = None
                        
                    # check if there are dates specificed for the challange
                    if start_date == None: start_date = request.POST.get('start_date')
                    if end_date == None: end_date = request.POST.get('end_date')
                    
                    # in case of event, the challange takes same dates as event
                    if belongsTo:
                        if start_date == None and belongsTo.start_date: start_date = belongsTo.start_date
                        if end_date == None and belongsTo.end_date: end_date = belongsTo.end_date

                    if start_date == None: start_date = datetime.now(timezone.utc)
                    if end_date == None: end_date = datetime.now(timezone.utc)
                        
                    description = request.POST.get('description')
                    ltr = 0
                    if request.POST.get('english_align') == 'ltr': ltr = 1
                    type = request.POST.get('type')
                    code = request.POST.get('code')
                    solve = request.POST.get('solve')
                    references = request.POST.get('references')
                    width = request.POST.get('width')
                    height = request.POST.get('height')
                    if width=='': width = 0
                    if height=='': height = 0

                    if (start_date and end_date):
                        adch = Challenge(title=title, level=level, start_date=start_date, end_date=end_date, description=description,
                                          type=type, code=code, solve=solve, references=references, width=width, height=height, alignment=ltr, belongsToEvent = belongsTo)
                    else:
                        adch = Challenge(title=title, level=level, description=description, type=type,
                                          code=code, solve=solve, references=references, width=width, height=height, alignment=ltr)
                    adch.save()

                    idch = Challenge.objects.all().first()
                    
                    if request.POST.get('mainFile') != '' or request.POST.get('mainFilePy') != '' or request.POST.get('mainFileCpp') != '':
                        try:
                            # prepare containing directory
                            dirs = 'files' + os.sep + str(idch.id)
                            if os.path.exists(dirs): shutil.rmtree(dirs)
                            
                            if request.POST.get('mainFile') != '':
                                minFile = request.FILES['mainFile']
                                filename = request.FILES['mainFile'].name
                                dirs = 'files' + os.sep + str(idch.id) + os.sep + 'Java'
                                os.makedirs(dirs)
                                fs = FileSystemStorage(location=dirs)
                                fs.save(filename, minFile)
                                filepath = dirs + os.sep + filename
                                idch.filepath = filepath
                            if request.POST.get('mainFilePy') != '':
                                minFile = request.FILES['mainFilePy']
                                filename = request.FILES['mainFilePy'].name
                                dirs = 'files' + os.sep + str(idch.id) + os.sep + 'Python'
                                os.makedirs(dirs)
                                fs = FileSystemStorage(location=dirs)
                                fs.save(filename, minFile)
                                filepath = dirs + os.sep + filename
                                idch.filepathPy = filepath
                            if request.POST.get('mainFileCpp') != '':
                                minFile = request.FILES['mainFileCpp']
                                filename = request.FILES['mainFileCpp'].name
                                dirs = 'files' + os.sep + str(idch.id) + os.sep + 'Cpp'
                                os.makedirs(dirs)
                                fs = FileSystemStorage(location=dirs)
                                fs.save(filename, minFile)
                                filepath = dirs + os.sep + filename
                                idch.filepathCpp = filepath
                            idch.save()
                        except:
                            print(traceback.format_exc())
                            idch.save()

                    if request.POST.get('minImage') != '':
                        try:
                            dirs = 'apps' + os.sep + 'static' + os.sep + 'assets' + os.sep + 'images' + os.sep + str(idch.id)
                            if os.path.exists(dirs): shutil.rmtree(dirs)
                            os.makedirs(dirs)
                            minImage = request.FILES['minImage']
                            myImagename = request.FILES['minImage'].name
                            fs = FileSystemStorage(location=dirs)
                            fs.save(myImagename, minImage)
                            file = str(idch.id)+ os.sep +myImagename
                            idch.attachment = file
                            idch.save()
                        except:
                            print(traceback.format_exc())
                            idch.save()
     
                    messages.success(request, 'تم انشاء التحدي بنجاح')
                    if idch.belongsToEvent: return HttpResponseRedirect("/competitions")
                    else: return HttpResponseRedirect("/challenges")
                else:
                    # prepare some data for the adding form
                    competitionList = Competition.objects.all().order_by('-start_date') # put latest event first
                    competitionList.group_by = ['title']
                    context = {'levels':__getLevelList(True), 'pTypes':__getProblemTypes(), 'competitionList':competitionList}
                    html_template = loader.get_template('home/addChallenge.html')
                    return HttpResponse(html_template.render(context, request))
            except:
                print(traceback.format_exc())
                if __isEnabledErrorPage: return HttpResponseRedirect('/pages')
        else:
            return HttpResponseRedirect('/challenges')
    except:
        print(traceback.format_exc())
        if __isEnabledErrorPage: return HttpResponseRedirect('/pages')

@login_required(login_url="/login/")
def editChallenge(request, viewc):
    try:
        user = User.objects.filter( Q(id=request.user.id) & ( Q(is_superuser=1) | Q(is_staff=1)))
        if len(user)>=1: user = user.first()
        
        ch = Challenge.objects.get(id=viewc)
        if user:
                if request.method == "POST" and request.POST.get('Delete').upper() == 'DELETE':
                    Submission.objects.filter(challenge=ch).delete() # perhaps archive is better
                    ch.delete()
                    dirs1 = 'files' + os.sep + str(viewc)
                    dirs2 = 'apps' + os.sep + 'static' + os.sep + 'assets' + os.sep + 'images' + os.sep + str(viewc)
                    try:
                        if os.path.exists(dirs1): shutil.rmtree(dirs1)
                        if os.path.exists(dirs2): shutil.rmtree(dirs2)
                    except: print(traceback.format_exc())
                elif request.method == "POST" and request.POST.get('title') != '' and Challenge.objects.get(id=viewc):
                    ch = Challenge.objects.get(id=viewc)
                    title = request.POST.get('title')
                    level = request.POST.get('level')
                    description = request.POST.get('description')
                    ltr = 0
                    if request.POST.get('english_align') == 'ltr': ltr = 1
                    event = request.POST.get('event')
                    start_date = end_date = belongsTo = None
                    
                    if event != 'None':
                        belongsTo = Competition.objects.get(title = str(event))
                        level = None
                    
                    # check if there are dates specificed for the challange
                    if start_date == None: start_date = request.POST.get('start_date')
                    if end_date == None: end_date = request.POST.get('end_date')
                    
                    # in case of event, the challange takes same dates as event if not set yet
                    if belongsTo:
                        if start_date == None and belongsTo.start_date: start_date = belongsTo.start_date
                        if end_date == None and belongsTo.end_date: end_date = belongsTo.end_date

                    if start_date == None: start_date = datetime.now(timezone.utc)
                    if end_date == None: end_date = datetime.now(timezone.utc)
                    
                    type = request.POST.get('type')
                    references = request.POST.get('references')
                    width = request.POST.get('width')
                    height = request.POST.get('height')
                    
                    ch.title = title
                    ch.level = level
                    ch.description = description
                    if start_date: ch.start_date = start_date
                    if end_date: ch.end_date = end_date
                    
                    if belongsTo: ch.belongsToEvent = belongsTo
                    else: ch.belongsToEvent = None
                    
                    ch.alignment = ltr
                    ch.type = type
                    ch.references = references
                    ch.width = width
                    ch.height = height
                    ch.save()

                    idch = Challenge.objects.get(id=viewc)
                    
                    # prepare containing directory
                    if request.POST.get('mainFile') != '':
                        minFile = request.FILES['mainFile']
                        __updateTestFile(idch, minFile, "Java")
                        idch.save()
                                
                    if request.POST.get('mainFilePy') != '':
                        minFile = request.FILES['mainFilePy']
                        __updateTestFile(idch, minFile, "Python")
                        idch.save()
                                
                    if request.POST.get('mainFileCpp') != '':
                        minFile = request.FILES['mainFileCpp']
                        __updateTestFile(idch, minFile, "Cpp")
                        idch.save()
                    
                    if request.POST.get('minImage') != '':
                        dirs = 'apps' + os.sep + 'static' + os.sep + 'assets' + os.sep + 'images' + os.sep + str(idch.id)
                        if os.path.exists(dirs): shutil.rmtree(dirs)
                        os.makedirs(dirs)
                        minImage = request.FILES['minImage']
                        myImagename = request.FILES['minImage'].name
                        fs = FileSystemStorage(location=dirs)
                        fs.save(myImagename, minImage)
                        file = str(idch.id)+ os.sep +myImagename
                        idch.attachment = file
                        idch.save()
                else:
                    # prepare for editing
                    competitionList = Competition.objects.all().order_by('-start_date') # put latest event first
                    competitionList.group_by = ['title']
                    context = {'ch': ch, 'levels':__getLevelList(True), 'pTypes':__getProblemTypes(), 'competitionList':competitionList}
                    html_template = loader.get_template('home/editChallenge.html')
                    return HttpResponse(html_template.render(context, request))
                
                # end posting update
                messages.success(request, 'تم تعديل التحدي بنجاح')
                if ch.belongsToEvent: return HttpResponseRedirect('/competitions')
                else: return HttpResponseRedirect('/challenges')
        else:
            if __isEnabledErrorPage: return HttpResponseRedirect('/pages')
    except:
        print(traceback.format_exc())
        if __isEnabledErrorPage: return HttpResponseRedirect('/pages')

@login_required(login_url="/login/")
def viewChallenge(request, viewc):
    try:
        user = User.objects.get(id=request.user.id)
        if __isMaintenanceMode(request) == True: return HttpResponseRedirect('home/construction.html')
        if __isNotValidProfile(user) == True and not user.is_superuser and not user.is_staff: 
            return HttpResponseRedirect('/pageuser')
        cont = Contestant.objects.get(user_id = user.id)
        ch = Challenge.objects.get(id = viewc)
        asGroup = False
        group = None
        if ch.belongsToEvent:
            check = Group.objects.filter(Q(event_id = ch.belongsToEvent_id) & (Q(user1 = user) | Q(user2 = user) |Q(user3 = user) |Q(user4 = user) |Q(user5 = user)))
            if check.count()>=1:
                asGroup = True
                group = check.first()
        
        if asGroup and group:
            submit = Submission.objects.filter(challenge = ch, group_id = group.id)
            if len(submit)>= 1: submit = submit.first()
            else: submit = Submission.objects.create(challenge = ch, group_id = group.id, view_date = datetime.now(timezone.utc), level = ch.level)
        else: 
            submit = Submission.objects.filter(challenge = ch, contestant = cont)
            if len(submit)>= 1: submit = submit.first()
            else: submit = Submission.objects.create(challenge = ch, contestant = cont, view_date = datetime.now(timezone.utc), level = ch.level)
        
        allowJava = allowPy = allowCpp = False
        if ch.filepath: allowJava = True
        if ch.filepathPy: allowPy = True
        if ch.filepathCpp: allowCpp = True
        
        disableCh = False
        if request.method == "POST":            
            if ch.belongsToEvent != None and ch.belongsToEvent.is_hackathon == 1:
                solve = None
                if request.POST.get('solve'): solve = request.POST.get('solve')
                if submit.result != 100:
                    if solve.strip('\"') == ch.code.strip('\"'):
                        submit.result = 100
                        submit.sum_result = 100
                    else:
                        submit.result = 0
                        submit.sum_result = 0
                    submit.status = 1
                    count = submit.counter
                    submit.counter = count + 1
                    solve_date = str(datetime.now(timezone.utc))
                    view_date = str(submit.view_date)
                    # update note with time solved
                    tS = solve_date[:-7]
                    tV = view_date[:-7]
                    tS = datetime.strptime(tS, '%Y-%m-%d %H:%M:%S.%f') # submission time
                    tV = datetime.strptime(tV, '%Y-%m-%d %H:%M:%S.%f') # view time
                    diff = tS - tV # ts always greater than tv
                    diff = str(diff.total_seconds())
                    submit.diff = diff
                else: solve_date = submit.solve_date
            else:
                language = request.POST.get('language')
                solve = '-'
                myfile = request.FILES['myfile']
                myfilename = request.FILES['myfile'].name
                dirs = 'files' + os.sep + str(ch.id) + os.sep + language + os.sep + str(cont.id) + '_' + str(submit.counter)
                if os.path.exists(dirs): shutil.rmtree(dirs)
                os.makedirs(dirs)
                fs = FileSystemStorage(dirs)
                fs.save(myfilename, myfile)
                filepath = dirs + os.sep + myfilename
                submit.filepath = filepath
                submit.language = language
                submit.status = 0 # reset for checking    
                solve_date = str(datetime.now(timezone.utc))
            
            submit.contestant = cont
            if asGroup: submit.group = group
            submit.user_solve = solve
            submit.solve_date = solve_date
            submit.save()
            
            ch.save()
            return HttpResponseRedirect("/submissions")
        
        # displaying challenge to user
        if ch.belongsToEvent:
            # view challenge that belongs to hackathon or competition
            currentTime = datetime.now(timezone.utc)
            if (ch.end_date != None and currentTime > ch.end_date) or (ch.start_date != None and ch.start_date > currentTime): disableCh = True
            if group==None: disableCh = True
        elif ch.level == 'Level 1' or ch.level == 'Level 2' or ch.level == 'Level 3' or ch.level == 'Level 4' or ch.level == 'Level 5':
            passed = False # by contradiction
            pending = False # by contradiction
            Exit = False
            while not Exit:
                if ch.level == 'Level 1':
                    # no need to check anything
                    passed = True
                    break
                elif ch.level == 'Level 2':
                    # must pass level 1 with full mark or placement between 0 and 20
                    try:
                        checking = Submission.objects.filter(Q(contestant = cont) & Q(level="Level 2") & Q(result__gte=60))
                        if len(checking) >= 1:                            
                            passed = True
                            break
                        checking = Submission.objects.filter(contestant=cont, level="Placement").order_by('-result')
                        if len(checking) >= 1 and checking[0].result >= 20:
                            passed = True
                            break
                        checking = Submission.objects.filter(contestant = cont, result=100, level="Level 1")
                        if len(checking) >= 1:
                            passed = True
                            break
                        checking = Submission.objects.filter(contestant = cont, status = 0, level = "Level 2", challenge = ch)
                        if len(checking) >= 1:
                            pending = True
                            break
                        break
                    except: break
                elif ch.level == 'Level 3':
                    # must pass level 2 with full mark or placement between 40 and 59
                    try:
                        checking = Submission.objects.filter(Q(contestant = cont) & Q(level="Level 3") & Q(result__gte=60))
                        if len(checking) >= 1:
                            passed = True
                            break
                        checking = Submission.objects.filter(contestant = cont, level="Placement").order_by('-result')
                        if len(checking) >= 1 and checking[0].result >= 40:
                            passed = True
                            break
                        checking = Submission.objects.filter(contestant = cont, result=100, level="Level 2")
                        if len(checking) >= 1:
                            passed = True
                            break
                        checking = Submission.objects.filter(contestant = cont, status=0, level="Level 3", challenge = ch)
                        if len(checking) >= 1:
                            pending = True
                            break
                        break
                    except: break
                elif ch.level == 'Level 4':
                    # must pass level 3 with full mark or placement between 60 and 79
                    try:
                        checking = Submission.objects.filter(Q(contestant = cont) & Q(level="Level 4") & Q(result__gte=60))
                        if len(checking) >= 1:
                            passed = True
                            break
                        checking = Submission.objects.filter(contestant = cont, level="Placement").order_by('-result')
                        if len(checking) >= 1 and checking[0].result >= 60:
                            passed = True
                            break
                        checking = Submission.objects.filter(contestant = cont, result=100, level="Level 3")
                        if len(checking) >= 1:
                            passed = True
                            break
                        checking = Submission.objects.filter(contestant = cont, status=0, level="Level 4", challenge = ch)
                        if len(checking) >= 1:
                            pending = True
                            break
                        break
                    except: break
                elif ch.level == 'Level 5':
                    # must pass level 4 with full mark or placement between 80 and 100
                    try:
                        checking = Submission.objects.filter(Q(contestant = cont) & Q(level="Level 5") & Q(result__gte=60))
                        if len(checking) >= 1:
                            passed = True
                            break
                        checking = Submission.objects.filter(contestant = cont, level="Placement").order_by('-result')
                        if len(checking) and checking[0].result >= 80:
                            passed = True
                            break
                        checking = Submission.objects.filter(contestant = cont, result=100, level="Level 4")
                        if len(checking):
                            passed = True
                            break
                        checking = Submission.objects.filter(contestant = cont, status=0, level="Level 5", challenge = ch)
                        if len(checking) >= 1:
                            pending = True
                            break
                        break
                    except: break
                break
            if not passed or pending:
                return render(request, "home/challenge.html", {'ch': ch, 'disableCh':True})
        elif ch.level == 'Placement': return render(request, "home/challenge.html", {'ch': ch,'allowJava': allowJava, 'allowPy': allowPy, 'allowCpp': allowCpp})
        return render(request, "home/challenge.html", {'ch': ch, 'disableCh':disableCh,'allowJava': allowJava, 'allowPy': allowPy, 'allowCpp': allowCpp, 'group':group})
    except:
        print(traceback.format_exc())
        return HttpResponseRedirect('/challenges')
    
def viewEvents(request):
    try:
        if __isMaintenanceMode(request) == True: return HttpResponseRedirect('home/construction.html')
        user = None        
        if request.user:
            user = User.objects.filter(id = request.user.id)
            if user != None and len(user)>=1: user = user.first()
            else: user = None
            if user != None and __isNotValidProfile(user) == True and not user.is_superuser and not user.is_staff:
                return HttpResponseRedirect('/pageuser')

        currentTime = datetime.now(timezone.utc)
        events = Competition.objects.filter(Q(end_date__gt=currentTime)).order_by('-start_date')
        if user != None:
            for e in events:
                check = Group.objects.filter(Q(event_id = e.id) & (Q(user1=user)|Q(user2=user)|Q(user3=user)|Q(user4=user)|Q(user5=user)))
                if len(check)>=1: e.registered = check.first().id
                else: e.registered = None
                
        oldevents = Competition.objects.filter(Q(end_date__lte=currentTime)).order_by('-start_date')
        
        context = {'segment': 'competitions', 'events': events, 'oldevents': oldevents, 'currentTime': currentTime}
        html_template = loader.get_template('home/competitions.html')
        return HttpResponse(html_template.render(context, request))
    except:
        print(traceback.format_exc())
        if __isEnabledErrorPage: return HttpResponseRedirect('/pages')

@login_required(login_url="/login/")
def addEvent(request):
    try:
        user = User.objects.filter( Q(id=request.user.id) & ( Q(is_superuser=1) | Q(is_staff=1)))
        if len(user)>=1: user = user.first() 
        
        if user:
            if request.method == 'POST' and request.POST.get('title') != '':
                title = request.POST.get('title')
                eventType = request.POST.get('type')
                startDate = request.POST.get('startDate')
                endDate = request.POST.get('endDate')
                description = request.POST.get('description')
                obj = None
                if startDate == None or startDate == '': startDate = datetime.now(timezone.utc)
                if endDate == None or endDate == '': endDate = datetime.now(timezone.utc)
                
                ltr = 0
                if request.POST.get('english_align') == 'ltr': ltr = 1
                
                if eventType == 'Competition':
                    obj = Competition(title=title, start_date=startDate, end_date=endDate, description=description, alignment = ltr)
                elif eventType == 'Hackathon':
                    obj = Competition(title=title, start_date=startDate, end_date=endDate, description=description, is_hackathon = True)
                obj.save()
                messages.success(request, 'تم انشاء الحدث بنجاح')
                return HttpResponseRedirect('/competitions')
            else:
                return render(request, "home/addEvent.html")
        else: return HttpResponseRedirect('/competitions')
    except:
        print(traceback.format_exc())
        if __isEnabledErrorPage: return HttpResponseRedirect('/pages')
   
@login_required(login_url="/login/")
def editEvent(request, eID):
    try: 
        user = User.objects.filter( Q(id=request.user.id) & ( Q(is_superuser=1) | Q(is_staff=1)))
        if len(user)>=1: user = user.first() 
        
        event = Competition.objects.get(id = eID)
        if user:
            if request.method == "POST" and request.POST.get('Delete').upper() == 'DELETE':
                event.delete()
            elif request.method == 'POST':
                title = request.POST.get('title')
                type = request.POST.get('type')
                if type == 'Competition': event.is_hackathon = False
                else: event.is_hackathon = True
                start_date = request.POST.get('start_date')
                end_date = request.POST.get('end_date')
                desc = request.POST.get('description')
                ltr = 0
                if request.POST.get('english_align') == 'ltr': ltr = 1
                
                # update record
                event.title = title
                if start_date: event.start_date = start_date
                if end_date: event.end_date = end_date
                event.description = desc
                event.alignment = ltr
                event.save()
                messages.success(request, "تم تعديل الحدث بنجاح")
                html_template = loader.get_template('home/competition.html')
            else:
                html_template = loader.get_template('home/editEvent.html')
                return HttpResponse(html_template.render({'event':event}, request))
        return HttpResponseRedirect('/competitions')
    except:
        print(traceback.format_exc())
        return HttpResponseRedirect('/competitions')

@login_required(login_url="/login/")
def viewEvent(request,eID):
    try: 
        user = User.objects.get(id = request.user.id)
        if __isMaintenanceMode(request) == True: return HttpResponseRedirect('home/construction.html')
        if __isNotValidProfile(user) == True and not user.is_superuser and not user.is_staff:
            return HttpResponseRedirect('/pageuser')

        check = Group.objects.filter(Q(event_id = eID) & (Q(user1 = user) | Q(user2 = user) |Q(user3 = user) |Q(user4 = user) |Q(user5 = user)))
        group = None
        if check.count()>=1: group = check.first()
        event = Competition.objects.get(id = eID)
        currentTime = datetime.now(timezone.utc)
        challenges = Challenge.objects.filter(belongsToEvent = event)
        # create submissions instance for all groups as viewed and starting of event
        if event.start_date<=currentTime and currentTime<event.end_date and group != None :
            for ch in challenges:
                check = Submission.objects.filter(challenge = ch, group_id = group.id).count()
                if check<=0: submit = Submission.objects.create(challenge = ch, group_id = group.id, view_date = currentTime)

        # obtain basic statistics about the challenges
        nonContestants_ids = list(map(lambda x: x.id, Contestant.objects.filter(~Q(is_user = 1))))
        totalSubmissions = totalPassed = 0
        for obj in challenges:
            check = Submission.objects.filter(Q(challenge_id = obj.id) & Q(status=1)).exclude(contestant_id__in = nonContestants_ids).count()
            obj.submissions = check
            totalSubmissions = totalSubmissions + check
            check = Submission.objects.filter(Q(challenge_id = obj.id) & Q(sum_result__gte=60)).exclude(contestant_id__in = nonContestants_ids).count()
            obj.passed = check
            totalPassed = totalPassed + check
        
        groups = Group.objects.filter(event = event)
        context = {'event': event, 'currentTime':currentTime, 'challenges':challenges, 'groups':groups, 'group':group, 'totalSubmissions':totalSubmissions, 'totalPassed':totalPassed}
        html_template = loader.get_template('home/competition.html')
        return HttpResponse(html_template.render(context, request))
    except:
        print(traceback.format_exc())
        return HttpResponseRedirect('/competitions')

@login_required(login_url="/login/")
def registerAGroup(request,compID):
    try:
        competition = Competition.objects.get(id = compID)
        user = User.objects.get(id = request.user.id)
        if __isMaintenanceMode(request) == True: return HttpResponseRedirect('home/construction.html')
        if __isNotValidProfile(user) == True and not user.is_superuser and not user.is_staff:
            return HttpResponseRedirect('/pageuser')
        
        name = None
        if request.method == "POST":
            n = 1
            members = {}
            members['member1']=members['member2']=members['member3']=members['member4']=members['member5']=None
            members['member'+ str(n)] = User.objects.get(id = request.user.id)
            # retrive other members
            
            n = 2
            for i in range(1,50,1):
                check = User.objects.filter(email = request.POST.get('member'+ str(i)))
                if check.count()>=1 and check.first() != user:
                    members['member'+ str(n)] = User.objects.filter(email = request.POST.get('member'+ str(i))).first()
                    n = n + 1
                    
            name = request.POST.get('name')
            exists = False
            if Group.objects.filter(name = name, event = competition).count() >= 1: exists = True
            
            if exists == True: 
                context = {'competition':competition, 'name':name, 'exists': exists}
                html_template = loader.get_template('home/groupRegisteration.html')
                return HttpResponse(html_template.render(context, request))
            
            group = Group(name=name,user1=members['member1'],user2=members['member2'],user3=members['member3'],
                        user4=members['member4'],user5=members['member5'], event = competition)
            group.save()
            messages.success(request, 'تم انشاء اسم المجموعة بنجاح')
            return HttpResponseRedirect('/competitions')
        else:
            exists = None
            disable = False
            check = Group.objects.filter(Q(event_id = compID) & (Q(user1 = user) | Q(user2 = user) |Q(user3 = user) |Q(user4 = user) |Q(user5 = user)))
            name = None
            if check.count()>=1:
                disable = True
                name = check.first().name
            context = {'competition':competition, 'exists': exists, 'disable':disable, 'name':name}
            html_template = loader.get_template('home/groupRegisteration.html')
            return HttpResponse(html_template.render(context, request))
    except:
        print(traceback.format_exc())
        return HttpResponseRedirect('/competitions')
        
@login_required(login_url="/login/")
def editGroup(request,eID,gID):
    try:
        user = User.objects.get(id = request.user.id)
        if __isMaintenanceMode(request) == True: return HttpResponseRedirect('home/construction.html')
        if __isNotValidProfile(user) == True and not user.is_superuser and not user.is_staff:
            return HttpResponseRedirect('/pageuser')
        
        competition = Competition.objects.get(id = eID)
        group = Group.objects.get(id = gID)
        
        if request.method == "POST":
            if request.POST.get('Delete').upper() == 'DELETE':
                group.delete()
                messages.success(request, 'تم حذف المجموعة بنجاح')
                return HttpResponseRedirect('/competitions')     
            #for key,value in request.POST.items(): print(f'Key: {key}, value: {value}')
            
            n = 1
            members = {}
            members['member1']=members['member2']=members['member3']=members['member4']=members['member5']=None
            members['member'+ str(1)] = user
            n = 2
            for i in range(1,50,1):
                check = User.objects.filter(email = request.POST.get('member'+ str(i)))
                if check.count()>=1 and check.first() != user:
                    members['member'+ str(n)] = User.objects.filter(email = request.POST.get('member'+ str(i))).first()
                    n = n + 1
            name = request.POST.get('name')
            exists = False
            check = Group.objects.filter(name = name, event = competition)
            if check.count() >= 1 and check.first() != group: exists = True
            
            if exists == True:
                context = {'competition':competition, 'name':name, 'exists': exists}
                html_template = loader.get_template('home/groupRegisteration.html')
                return HttpResponse(html_template.render(context, request))
            
            #print(members)
            group.name = name
            group.user1 = members['member1']
            group.user2 = members['member2']
            group.user3 = members['member3']
            group.user4 = members['member4']
            group.user5 = members['member5']
                    
            group.save()
            messages.success(request, 'تم تعديل المجموعة بنجاح')
            return HttpResponseRedirect('/competitions')
        
        # load for editing
        members = {}
        members['member1'] = members['member2']=members['member3']=members['member4']=members['member5']=None
        if group.user1 != None: members['member1'] = User.objects.get(id = group.user1_id).email
        if group.user2 != None: members['member2'] = User.objects.get(id = group.user2_id).email
        if group.user3 != None: members['member3'] = User.objects.get(id = group.user3_id).email
        if group.user4 != None: members['member4'] = User.objects.get(id = group.user4_id).email
        if group.user5 != None: members['member5'] = User.objects.get(id = group.user5_id).email
        
        members = list(members.values())
        clean = []
        #print(members)
        for m in members: 
            if m!=None: clean.append(m)
        
        members = ','.join(clean)
        context = {'competition':competition, user:'user','exists': False, 'disable':False, 'group':group, 'members':members}
        html_template = loader.get_template('home/groupEditing.html')
        return HttpResponse(html_template.render(context, request))
    except:
        print(traceback.format_exc())
        return HttpResponseRedirect('/competitions')

@login_required(login_url="/login/")
def getMember(request):
    if 'term' in request.GET:
        query = request.GET.get("term", "")
        users = User.objects.filter(email__icontains=query)
        results = []
        for e in users: results.append(e.email)
        data = json.dumps(results)
    mimetype = "application/json"
    return HttpResponse(data, mimetype)

@login_required(login_url="/login/")
def viewSubmissions(request):
    try:
        user = User.objects.get(id = request.user.id)
        if __isMaintenanceMode(request) == True: return HttpResponseRedirect('home/construction.html')
        if __isNotValidProfile(user) == True and not user.is_superuser and not user.is_staff:
            return HttpResponseRedirect('/pageuser')
        
        cont = Contestant.objects.get(user_id = request.user.id)
        collections = Submission.objects.filter(Q(contestant_id = cont.id) & ~Q(status = -1))
        html_template = loader.get_template('home/submissions.html')
        return HttpResponse(html_template.render({'segment': 'submissions', 'submissions': collections}, request))
    except:
        print(traceback.format_exc())
        return HttpResponseRedirect('/index')

@login_required(login_url="/login/")
def submission(request, sid):
    try:
        user = User.objects.get(id = request.user.id)
        if __isMaintenanceMode(request) == True: return HttpResponseRedirect('home/construction.html')
        if __isNotValidProfile(user) == True and not user.is_superuser and not user.is_staff:
            return HttpResponseRedirect('/pageuser')
        
        submit = Submission.objects.get(id=sid)
        if submit.challenge.references != None and len(submit.challenge.references) >= 2:
            referenceText = submit.challenge.references
        elif submit.challenge.belongsToEvent == None:
            check = Reference.objects.filter(type = submit.challenge.type, level = submit.level)
            if len(check)>= 1: referenceText = check[0].references
            else: referenceText = None
        else: referenceText = None
        return render(request, "home/submission.html", ({'submit': submit, 'referenceText':referenceText}))
    except:
        print(traceback.format_exc())
        return HttpResponseRedirect('/submissions')

@login_required(login_url="/login/")
def showResult(request, chId):
    try:
        user = User.objects.get(id = request.user.id)
        if __isMaintenanceMode(request) == True: return HttpResponseRedirect('home/construction.html')
        if __isNotValidProfile(user) == True and not user.is_superuser and not user.is_staff:
            return HttpResponseRedirect('/pageuser')

        ch = Challenge.objects.get(id = chId)
        if user:
            nonContestants = Contestant.objects.filter(~Q(is_user = 1))
            nonContestants_ids = list(map(lambda x: x.id, nonContestants))
            submissions = Submission.objects.filter(Q(challenge = ch) & Q(counter__gte = 1) & Q(status = 1)).order_by('-sum_result','solve_date','diff').distinct().exclude(contestant_id__in = nonContestants_ids)
            badSubmissions = Submission.objects.filter(Q(challenge = ch) & Q(counter__gte = 1) & Q(status = 3)).order_by('-view_date').distinct().exclude(contestant_id__in = nonContestants_ids)
            ch = Challenge.objects.get(id=chId)
            return render(request, "home/challengeResult.html", {'ch': ch, 'submissions':submissions, 'badSubmissions':badSubmissions})
        else: return HttpResponseRedirect("/competitions")
    except:
        print(traceback.format_exc())
        return HttpResponseRedirect('/competitions')

@login_required(login_url="/login/")
def viewScoreBoard(request,eID):
    try:
        user = User.objects.get(id = request.user.id)
        if __isMaintenanceMode(request) == True: return HttpResponseRedirect('home/construction.html')
        if __isNotValidProfile(user) == True and not user.is_superuser and not user.is_staff: 
            return HttpResponseRedirect('/pageuser')
            
        event = Competition.objects.get(id = eID)
        challenges = Challenge.objects.filter(belongsToEvent = event).order_by("id")
        challenges_ids = list(map(lambda x: x.id, challenges))
        groups = Group.objects.filter(event_id = eID).values()
        
        # sort groups based on decending order of their result and assending order of their diff
        for g in groups:
            baseQuery = Submission.objects.filter(Q(group_id = g['id']) & Q(challenge_id__in=challenges_ids))
            #g['sum_result'] = Submission.objects.filter(Q(group_id = g['id']) & ~Q(status = -1) & Q(challenge_id__in=challenges_ids)).aggregate(sum_result = Sum("result"))['sum_result']
            g['sum_result'] = baseQuery.exclude(Q(status = -1)).aggregate(sum_result = Sum("sum_result"))['sum_result']
            #g['sum_diff'] = Submission.objects.filter(Q(group_id = g['id']) & ~Q(status = -1) & Q(challenge_id__in=challenges_ids)).aggregate(sum_diff = Sum("diff"))['sum_diff']
            g['sum_diff'] = baseQuery.exclude(Q(status = -1)).aggregate(sum_diff = Sum("diff"))['sum_diff']
            g['submissions'] = baseQuery.order_by('challenge_id').distinct()
            
        # use manual sorting of groups using insertion sort
        data = __sortGroups(groups)
        
        currentTime = datetime.now(timezone.utc)
            
        context = {'event': event, 'currentTime':currentTime, 'challenges':challenges, 'groups':data}
        html_template = loader.get_template('home/scoreboard.html')
        return HttpResponse(html_template.render(context, request))
    except:
        print(traceback.format_exc())
        return HttpResponseRedirect('/competitions')
        
@login_required(login_url="/login/")
def viewReferences(request):
    try:
        user = User.objects.get(id = request.user.id)
        if user.is_superuser or user.is_staff:
                html_template = loader.get_template('home/references.html')
                return HttpResponse(html_template.render({'references': Reference.objects.all().order_by('level', 'type')}, request))
        else:
            return HttpResponseRedirect('/index')
    except:
        print(traceback.format_exc())
        return HttpResponseRedirect('/index')

@login_required(login_url="/login/")
def addReference(request):
    try:
        user = User.objects.get(id = request.user.id)
        if user.is_superuser or user.is_staff:
            if request.method == 'POST':
                level = request.POST.get('level')
                type = request.POST.get('type')
                text = request.POST.get('references')
                ref = Reference(level=level, type = type, references=text)
                ref.save()
                messages.success(request, 'تم انشاء المرجع بنجاح')
                return HttpResponseRedirect('/references')
            else:
                html_template = loader.get_template('home/addRef.html')
                return HttpResponse(html_template.render({'levels': __getLevelList(False), 'pTypes':__getProblemTypes()}, request))
    except:
        print(traceback.format_exc())
        return HttpResponseRedirect('/index')

@login_required(login_url="/login/")
def editReference(request, refID):
    try:
        user = User.objects.get(id = request.user.id)
        ref = Reference.objects.get(id = refID)
        if user.is_superuser or user.is_staff:
            if request.method == "POST" and request.POST.get('Delete').upper() == 'DELETE':
                ref.delete()
            elif request.method == 'POST':
                level = request.POST.get('level')
                type = request.POST.get('type')
                text = request.POST.get('references')
                ref.level = level
                ref.type = type
                ref.references = text
                ref.save()
                messages.success(request, 'تم تعديل المرجع بنجاح')
            else:
                html_template = loader.get_template('home/editRef.html')
                return HttpResponse(html_template.render({'ref':ref, 'levels': __getLevelList(False), 'pTypes':__getProblemTypes()}, request))
            return HttpResponseRedirect('/references')
    except:
        print(traceback.format_exc())
        return HttpResponseRedirect('/index')
    
@login_required(login_url="/login/")
def page_user(request):
    try:
        cont = Contestant.objects.get(user_id=request.user.id)
        profile = User.objects.get(id=request.user.id)
        if __isMaintenanceMode(request) == True: return HttpResponseRedirect('home/construction.html')
        if __notValidNames(profile): messages.warning(request, "يجب تحديث ملف التعريف: الاسم إلى الاسم الكامل او الثلاثي")
        if __notValidEmail(profile): messages.warning(request, "يجب تحديث ملف التعريف: البريد الإلكتروني إلى البريد الإلكتروني الرسمي")
        
        if request.method == "POST" and request.POST.get('nameUpdate') != None:
            user_nameF = request.POST.get('First_Name')
            user_nameM = request.POST.get('Middle_Name')
            user_nameM2 = request.POST.get('Middle_Name2')
            user_nameL = request.POST.get('Last_Name')
            user_type = True
            if profile.is_superuser == '1' or profile.is_staff == '1': user_type = False
            cont.user_nameF = user_nameF
            cont.user_nameM = user_nameM
            cont.user_nameM2 = user_nameM2
            cont.user_nameL = user_nameL
            cont.is_user = user_type
            cont.save()
            if __notValidNames(profile): messages.warning(request, "يجب تحديث ملف التعريف: الاسم إلى الاسم الكامل او الثلاثي")
            else: messages.success(request, "تم تحديث ملف التعريف بنجاح")
        elif request.method == "POST" and request.POST.get('passwordUpdate') != None:
            # update password
            oldP = request.POST.get('oldPassword')
            newP = request.POST.get('newPassword')
            newP2 = request.POST.get('newPassword2')
            checking= profile.check_password(oldP)
            if checking and newP == newP2:
                profile.set_password(newP)
                profile.save()
                messages.success(request, "تم تحديث ملف التعريف بنجاح")
            else:
                messages.warning(request, "لم يتم تعديل كلمة المرور")
        elif request.method == "POST" and request.POST.get('emailUpdate') != None:
            # update email
            nEmail = request.POST.get('newEmail')
            
            success = True
            if profile.email == nEmail:
                messages.warning(request, "يجب استخدام عنوان بريدي مختلف عن الحالي")
                success = False
            if not ("edu.sa" in nEmail):
                messages.warning(request, "يجب تحديث ملف التعريف: البريد الإلكتروني إلى البريد الإلكتروني الرسمي")
                success = False
            if success:
                profile.email = nEmail
                profile.save()
                messages.success(request, "تم تحديث ملف التعريف بنجاح")
                
        if profile.is_superuser == True or profile.is_staff == True:
            cont.is_user = False
            cont.save()
        # import un attempted placements
        allplacements = Challenge.objects.filter(level = 'Placement')
        for obj in allplacements:
            check = Submission.objects.filter(Q(challenge_id = obj.id) & Q(status=1)).count()
            obj.submissions = check
            check = Submission.objects.filter(Q(challenge_id = obj.id) & Q(sum_result__gte=60)).count()
            obj.passed = check
        placements = []
        for p in allplacements:
            checking = Submission.objects.filter(Q(challenge=p) & Q(contestant=cont) & Q(status=1))
            if len(checking)<=0: placements.append(p)
        html_template = loader.get_template('home/page-user.html')
        return HttpResponse(html_template.render({'cont': cont, 'placements': placements}, request))
    except:
        print(traceback.format_exc())
        return HttpResponseRedirect('/index')
    
@login_required(login_url="/login/")
def users(request):
    try:
        user = User.objects.get(id=request.user.id)
        if user.is_superuser:
            users = User.objects.all().order_by('-is_superuser', '-is_staff')
            html_template = loader.get_template('home/users.html')
            return HttpResponse(html_template.render({'users': users}, request))
    except:
        print(traceback.format_exc())
        return HttpResponseRedirect('/index')
    
@login_required(login_url="/login/")
def userEdit(request, uid):
    try:
        user = User.objects.get(id=request.user.id, is_superuser='1')
        if user and request.method == "POST" and request.POST.get('Delete').upper() == 'DELETE':
            Contestant.objects.get(user_id = uid).delete()
            User.objects.get(id=uid).delete()
        elif user and request.method == 'POST':
            fname = request.POST.get('fName')
            lname = request.POST.get('lName')
            userType = request.POST.get('userType')
            targetUser = User.objects.get(id = uid)
            user_profile = False
            if userType == 'admin':
                user_profile = False
                targetUser.is_superuser = '1'
                targetUser.is_staff = '0'
            elif userType == 'staff':
                user_profile = False
                targetUser.is_superuser = '0'
                targetUser.is_staff = '1'
            else:
                user_profile = True
                targetUser.is_superuser = '0'
                targetUser.is_staff = '0'
            targetUser.first_name = fname
            targetUser.last_name = lname
            targetUser.save()
            contestant = Contestant.objects.filter(user_id = uid)
            if  len(contestant)<=0:
                contestant = Contestant.objects.create(user_id = uid).first()
            contestant = Contestant.objects.get(user_id = uid)
            contestant.is_user = user_profile
            contestant.save()
        else:
            targetUser = User.objects.get(id = uid)
            html_template = loader.get_template('home/userEdit.html')
            return HttpResponse(html_template.render({'targetUser': targetUser}, request))
        return HttpResponseRedirect('/users')
    except:
        print(traceback.format_exc())
        return HttpResponseRedirect('/index')
  
@login_required(login_url="/login/")
def viewContestants(request):
    try:
        user = User.objects.get(id = request.user.id)
        if user.is_superuser or user.is_staff:
            contestants = Contestant.objects.filter( is_user = 1 ).order_by('user_nameF', 'user_nameM','user_nameM2','user_nameL')
            data = contestants.values()
            for obj in data:
                obj['email'] = User.objects.get(id=obj['user_id']).email
                # obtain all submission counts
                obj['submissions'] = Submission.objects.filter(Q(contestant_id = obj['id']) & ~Q(status = -1)).distinct().count()
            contestants = sorted(data, key=lambda obj:obj['submissions'], reverse=True)
                
            html_template = loader.get_template('home/contestants.html')
            return HttpResponse(html_template.render({'contestants': contestants}, request))
        else:
            return HttpResponseRedirect('/index')
    except:
        print(traceback.format_exc())
        return HttpResponseRedirect('/index')
    
@login_required(login_url="/login/")
def viewContestant(request, cID):
    try:
        user = User.objects.get(id = request.user.id)
        if user.is_superuser or user.is_staff:
            totalSubmissions = Submission.objects.filter(Q(contestant_id = cID) & ~Q(status=-1)).count() # this only show 1 and 3
            submissions = Submission.objects.filter(Q(contestant_id = cID) & Q(status = 1))
            contestant = Contestant.objects.get(id=cID)
            contestant.email = User.objects.get(id=contestant.user_id).email
            successSubmissions = Submission.objects.filter(Q(contestant_id = cID) & Q(sum_result__gte = 60)).count()
            fullMarkSubmissions = Submission.objects.filter(Q(contestant_id = cID) & Q(sum_result = 100)).count()
            users1 = Contestant.objects.filter(is_user = True, user_scoreL1__gte = 1).order_by('-user_scoreL1').distinct()
            users2 = Contestant.objects.filter(is_user = True, user_scoreL2__gte = 1).order_by('-user_scoreL2').distinct()
            users3 = Contestant.objects.filter(is_user = True, user_scoreL3__gte = 1).order_by('-user_scoreL3').distinct()
            users4 = Contestant.objects.filter(is_user = True, user_scoreL4__gte = 1).order_by('-user_scoreL4').distinct()
            users5 = Contestant.objects.filter(is_user = True, user_scoreL5__gte = 1).order_by('-user_scoreL5').distinct()
                
            bad_submissions = Submission.objects.filter(Q(contestant_id = cID) & Q(status = 3))
                
            index = 1
            userLevel1 = None
            for e in users1:
                if e.id == int(cID):
                    userLevel1 = index
                    break
                else: index = index + 1
                
            index = 1
            userLevel2 = None
            for e in users2:
                if e.id == int(cID):
                    userLevel2 = index
                    break
                else: index = index + 1
                    
            index = 1
            userLevel3 = None
            for e in users3:
                if e.id == int(cID):
                    userLevel3 = index
                    break
                else: index = index + 1
                    
            index = 1
            userLevel4 = None
            for e in users4:
                if e.id == int(cID):
                    userLevel4 = index
                    break
                else: index = index + 1
                    
            index = 1
            userLevel5 = None
            for e in users5:
                if e.id == int(cID):
                    userLevel5 = index
                    break
                else: index = index + 1
                
            html_template = loader.get_template('home/contestant.html')
            return HttpResponse(html_template.render({'totalSubmissions':totalSubmissions, 'contestant':contestant, 'submissions':submissions, 'bad_submissions':bad_submissions,'successSubmissions':successSubmissions, 'fullMarkSubmissions':fullMarkSubmissions, 'userLevel1':userLevel1, 'userLevel2':userLevel2, 'userLevel3':userLevel3, 'userLevel4':userLevel4, 'userLevel5':userLevel5}, request))
        else:
            return HttpResponseRedirect('/index')
    except:
        print(traceback.format_exc())
        return HttpResponseRedirect('/index')
    
@login_required(login_url="/login/")
def viewFile(request, sID):
    user_profile = User.objects.get(id = request.user.id)
    try:
        if user_profile.is_superuser or user_profile.is_staff:
            submission = Submission.objects.get(id=sID)
            challenge = Challenge.objects.get(id=submission.challenge_id)
            fMain = None
            if submission.language == 'Java':
                fMain = open(str(challenge.filepath), 'r')
            elif submission.language == 'Python':
                fMain = open(str(challenge.filepathPy), 'r')
            file = open(str(submission.filepath), 'r')
            mainContent = fMain.read()
            content = file.read()
            html_template = loader.get_template('home/filecontent.html')
            return HttpResponse(html_template.render({'mainContent':mainContent,'content':content}, request))
    except:
        print(traceback.format_exc())
        return HttpResponseRedirect('/pages')
    
@login_required(login_url="/login/")
def viewMainFile(request, cID, target):
    user_profile = User.objects.get(id = request.user.id)
    if user_profile.is_superuser or user_profile.is_staff:
            ch = Challenge.objects.get(id=cID)
            if target == 'Java': path = str(ch.filepath)
            elif target == 'Python': path = str(ch.filepathPy)
            elif target == 'Cpp': path = str(ch.filepathCpp)
            file = open(path, 'r')
            content = file.read()
            html_template = loader.get_template('home/filecontent2.html')
            return HttpResponse(html_template.render({'content':content}, request))
    else:
        return HttpResponseRedirect('/pages')

def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:
        load_template = request.path.split('/')[-1]

        if load_template == 'admin': return HttpResponseRedirect(reverse('admin:dashboard'))
        context['segment'] = load_template
        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))
    except template.TemplateDoesNotExist:
        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))
    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))

def __isEnabledErrorPage(): return True

def __getLevelList(with_p):
    levels = []
    levels.append('Level 1')
    levels.append('Level 2')
    levels.append('Level 3')
    levels.append('Level 4')
    levels.append('Level 5')
    if with_p: levels.append('Placement')
    return levels

def __getProblemTypes():
    types = []
    types.append('Arrays')
    types.append('Brute force')
    types.append('Dynamic programming')
    types.append('Mathematical and geometry')
    types.append('Greedy')
    types.append('Recursion')
    types.append('Search and sorting')
    types.append('String manipulation')
    return types

def __sortGroups(data) -> dict:
    data2 = list(data)
    size = len(data)
    for i in range(1, size, 1):
        for j in range(i - 1, -1, -1):
            #print("Result: " + str(data2[j]['sum_result']) + ", " + str(data2[j+1]['sum_result']))
            #print("Diff: " + str(data2[j]['sum_diff']) + ", " +  str(data2[j+1]['sum_diff']))
            if data2[j]['sum_result'] == None and data2[j+1]['sum_result'] == None: continue
            if data2[j]['sum_result'] == None and data2[j+1]['sum_result'] != None:
                data2[j], data2[j+1] = data2[j+1], data2[j]
                continue
            if data2[j]['sum_diff'] == None and data2[j+1]['sum_diff'] == None: continue
            if data2[j]['sum_diff'] == None and data2[j+1]['sum_diff'] == None:
                data2[j], data2[j+1] = data2[j+1], data2[j]
                continue
            
            if data2[j]['sum_result']<data2[j+1]['sum_result'] or (data2[j]['sum_result'] == data2[j+1]['sum_result'] and data2[j]['sum_diff'] > data2[j+1]['sum_diff']):
                # swap
                data2[j], data2[j+1] = data2[j+1], data2[j]
            else: break
    return data2

def __isNotValidProfile(user):
    checkNames = True
    checkEmail = True
    invalid = False
    if checkNames:
        if __notValidNames(user): invalid = True
    if checkEmail: 
        if __notValidEmail(user): invalid = True    
    return invalid

def __notValidNames(user):
    cont = Contestant.objects.get(user_id = user.id)
    while(True):
        if cont.user_nameF == None or len(cont.user_nameF)<=0: return True
        if cont.user_nameM == None or len(cont.user_nameM)<=0: return True
        if cont.user_nameL == None or len(cont.user_nameL)<=0: return True
        break
    return False
    
def __notValidEmail(user):
    user = User.objects.get(id = user.id)
    if not "edu.sa" in user.email: return True
    return False
   
def __updateTestFile(challenge, file, lang:str):
    filename = file.name
    if lang == "Java": dirs = 'files' + os.sep + str(challenge.id) + os.sep + 'Java'
    if lang == "Python": dirs = 'files' + os.sep + str(challenge.id) + os.sep + 'Python'
    if lang == "Cpp": dirs = 'files' + os.sep + str(challenge.id) + os.sep + 'Cpp'
    
    filepath = dirs + os.sep + filename
    if os.path.exists(filepath): os.remove(filepath)
    fs = FileSystemStorage(location=dirs)
    fs.save(filename, file)
    
    if lang == "Java": challenge.filepath = filepath
    if lang == "Python": challenge.filepathPy = filepath
    if lang == "Cpp": challenge.filepathCpp = filepath
