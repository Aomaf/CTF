# -*- encoding: utf-8 -*-

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import LoginForm, SignUpForm, RecoverForm
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.shortcuts import render, redirect
from django.utils.encoding import force_bytes, force_str
from .token import account_activation_token
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.template import loader
from apps.home.models import Contestant

def loginPage(request):
    form = LoginForm(request.POST or None)
    msg = None
    if 'recoveryMsg' in request.session:
        msg = request.session['recoveryMsg']
        del request.session['recoveryMsg']
    
    if request.method == "POST":
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                cont = Contestant.objects.filter(user_id = user.id)
                if not cont or len(cont)<=0: Contestant.objects.create(user_id = user.id, is_user = True)
                return redirect("/dashboard")
            else: msg = 'البيانات غير صحيحة'
        else:
            msg = 'Error validating the form'
    return render(request, "accounts/login.html", {"form": form, "msg": msg})

def logoutPage(request):
    logout(request)
    return redirect('/')

def registerPage(request):
    msg = None
    success = False
    username = None
    disable_activation = False
    is_active = True
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            while(True):
                if not ("edu.sa" in email):
                    msg = ' يجب استخدام عنوان بريدي رسمي . '
                    success = False
                    break 
                check = User.objects.filter(email=email, is_active = 1)
                if len(check)>=1:
                    msg = ' يوجد حساب فعال له نفس البريد الالكتروني المدخل . '
                    success = False
                    break
                success = True
                break
                   
            if disable_activation == True and success:
                form.save()
                username = form.cleaned_data.get("username")
                raw_password = form.cleaned_data.get("password1")
                user = authenticate(username=username, password=raw_password)
                msg = 'تم إنشاء حسابك بنجاح'
                is_active = True
            elif disable_activation == False and success:
                user = form.save(commit=False)
                user.is_active = False
                user.save()
                site = get_current_site(request)
                subject = "QuPC رابط التفعيل"
                username = form.cleaned_data.get("username")
                message = render_to_string('accounts/active_email.html',{
                    'user': user,
                    'domain': site.domain,
                    'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                    'token':account_activation_token.make_token(user),
                })
                to_email = form.cleaned_data.get('email')  
                email = EmailMessage(subject, message, to=[to_email])
                email.send()
                msg = "تم التسجيل بنجاح وتم ارسال رابط التفعيل على البريد الالكتروني. الرجاء تفعيل حسابك."
        else:  msg = 'بيانات غير صالحة'
    else: form = SignUpForm()
    return render(request, "accounts/register.html", {"form": form, "msg": msg, "success": success,"usenrame": username, 'is_active':is_active})

def activatePage(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):  
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        success = True
        msg = 'شكرا لك على تفعيل حسابك. يمكنك الان استخدام منصة جامعتي تبرمج. اهلا بك.'
        return render(request, "accounts/register.html", {"form": None, "msg": msg, "success": success,"usenrame": user.username, 'is_active':True})
    else:
        success = False
        msg = 'خطأ في عملية تفعيل حسابك. الرجاء اعادة التسجيل مرة آخرى'
        form = SignUpForm()
        return render(request, "accounts/register.html", {"form": form, "msg": msg, "success": success,"usenrame": None, 'is_active':False})
        
def recoverPasswordPage(request):
    form = RecoverForm(request.POST or None)
    msg = None
    if request.method == "POST":
        if form.is_valid():
            email = form.cleaned_data.get("email")
            user = User.objects.filter(email__exact = email, is_active = 1)
            if len(user)==1:
                user = User.objects.get(email__exact = email, is_active = 1)
                tPassword = User.objects.make_random_password()
                subject = "QuPC استعادة كلمة المرور لمنصة"
                message = render_to_string('accounts/password_recovery.html',{
                    'user': user,
                    'tPassword':tPassword,
                })
                user.set_password(tPassword)
                user.save()
                to_email = user.email
                email = EmailMessage(subject, message, to=[to_email])
                email.send()
                msg = 'تم استعادة كلمة المرور بنجاح وتم ارسالها الى بريدك الالكتروني'
                request.session['recoveryMsg'] = msg
                return redirect('login')
            elif len(user)>1:
                msg = 'البيانات المدخلة غير متطابقة ويوجد عدة مستخدمين بهذا الايميل'
            else:
                msg = 'البيانات غير صحيحة. لا يوجد مستخدم بهذا الاسم'
        else:
            msg = 'Error validating the form'
    return render(request, "accounts/recover.html", {"form": form, "msg": msg})

