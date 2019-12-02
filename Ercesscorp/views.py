from django.shortcuts import render, redirect, get_object_or_404, render_to_response
from django.contrib.auth.models import User
from django.conf import settings
import logging
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.core import serializers
from django.urls import reverse
from django.template import RequestContext, Context, loader
from hashlib import md5
from dashboard.forms import Articles2Form, BoostEventForm
from html import unescape
from django.utils.dateparse import parse_date
import secrets
import time
import os
import re
from PIL import Image
from django.core.files.storage import FileSystemStorage
from datetime import datetime
import itertools
from django.contrib.staticfiles.urls import static
from dashboard.models import AdminActionLog, EventProcesses, EventVerificationResult, Rsvp, StatusPromotionTicketing, PartnerSites, StatusOnChannel, BoostEvent, EventStatusOnChannel
from django.shortcuts import render_to_response
from django.contrib import messages


from .forms import RegistrationForm, UserForm, LoginForm, ForgotPasswordForm, ContactForm, ResetPassword,UpdateContact
from .models import RegistrationData, BlogData, ContactData, Users
from dashboard.models import Rsvp, StatusPromotionTicketing, Articles2, Tickets, TicketsSale, AdminEventAssignment, Admin, StatusOnChannel, Categories, Topics, CategorizedEvents, AboutCountries, EventEditLogs

from django.utils import timezone

from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth.hashers import make_password, check_password
import hashlib
from .models import UserRegistrationToken
import uuid
from datetime import datetime as dt
######## to manage error of MultipleObjectsReturned ###########
from django.core.exceptions import MultipleObjectsReturned


email_sent_from = settings.EMAIL_HOST_USER

flag = 0
l = []
email_verify_dict = {}


logging.basicConfig(filename='test.log', level=logging.DEBUG,
                    format='%(asctime)s:%(levelname)s:%(message)s')


def send_verification_email(host_url_param, user_id_param, user_email_param, firstname_param, lastname_param):
    try:
        email_token = str(uuid.uuid4()) + str(user_id_param)
        # save token into db
        currentTime = dt.now().strftime("%Y-%m-%d %H:%M:%S")

        # UserRegistrationToken.objects.filter(user_email=emailVal)
        user_registration_token_filter_data = UserRegistrationToken.objects.filter(
            user_email=user_email_param)
        if len(user_registration_token_filter_data) == 0:
            UserRegistrationToken.objects.create(
                user_email_token=email_token, user_email=user_email_param, user_email_token_created_on=currentTime)
        else:
            UserRegistrationToken.objects.filter(user_email=user_email_param).update(
                user_email_token=email_token, user_email_token_created_on=currentTime)
        # ends here ~ save token into db

        verify_url = 'http://' + host_url_param + \
            '/live/verify_email/' + email_token + '/'
        # send email
        html_message = loader.render_to_string('static/common/signup_verification.html',
                                               {
                                                   'firstname': firstname_param,
                                                   'lastname': lastname_param,
                                                   'verify_url': verify_url
                                               })
        send_mail('Verify Email', 'message', email_sent_from, [
                  user_email_param], fail_silently=False, html_message=html_message)
        # ends here ~ send email

    except Exception as e:
        print('error is ', e)


@csrf_exempt
def registration(request):
    regerr = False
    pass_no_match = False
    mail_no_match = False
    auth_email_failed = False
    submitted = False
    sec_code = None
    errormail = False
    x = 0
    if request.method == 'POST':
        try:
            # read request data
            requestData = request.body
            requestDataDecode = requestData.decode('utf8').replace("'", '"')
            requestDataJson = json.loads(requestDataDecode)
            # ends here ~ read request data

            # set value into variable
            fnameVal = requestDataJson['fnameVal']
            lnameVal = requestDataJson['lnameVal']
            locVal = requestDataJson['locVal']
            emailVal = requestDataJson['emalVal']
            passVal = requestDataJson['passVal']
            # ends here ~ set value into variable

            # test code
            # Users.objects.filter().exclude(id=1).delete()
            # UserRegistrationToken.objects.filter(user_email=emailVal).delete()
            # ends here ~ test code

            filterData = Users.objects.filter(user=emailVal)
            if len(filterData) == 0:
                # save values into db
                pswd_encoded = hashlib.md5(passVal.encode('utf-8')).hexdigest()
                email_encoded = hashlib.md5(
                    emailVal.encode('utf-8')).hexdigest()
                new_user = Users(user=emailVal, firstname=fnameVal, lastname=lnameVal,
                                 location=locVal, password=pswd_encoded, md5=email_encoded)
                new_user.save()
                # ends here ~ save values into db

                # email_token = str(uuid.uuid4()) + str(new_user.id)

                send_verification_email(
                    request.get_host(), new_user.id, emailVal, fnameVal, lnameVal)
                '''
                html_message = loader.render_to_string('static/common/signup_verification.html',
                     {
                     'firstname': 'firstname_param',
                     'lastname': 'lastname_param',
                     'verify_url':'verify_url'
                     })
                '''
             #   send_mail('subject','message',email_sent_from,['mybooks0101@gmail.com'],fail_silently=False) #,html_message=html_message)
                # # ends here ~ send email

                messageData = {'message': 'Congratulations! your account is successfully created. Please check your email and follow the instructions.',
                               'responseType': 'success', 'messageType': 'success'}

            else:

                messageData = {'message': 'This account already exists in our record. Try to login.',
                               'responseType': 'success', 'messageType': 'error'}


#            messageData = {'as':'as'}
            return HttpResponse(json.dumps(messageData))
        except Exception as e:
            print('error is', e)
            ############### new code ~ Date: 21 april 2019 #############
            # @author Shubham
            # return message
            messageData = {'message': e,
                           'responseType': 'error', 'messageType': 'error'}
            return HttpResponse(json.dumps(messageData))
            ################ ends here ~  new code ~ Date: 21 april 2019 #############

    else:
        form1 = UserForm()
        form2 = RegistrationForm()
        if 'regerr' in request.GET:
            regerr = True
        if 'pass_no_match' in request.GET:
            pass_no_match = True
        if 'mail_no_match' in request.GET:
            mail_no_match = True
        if 'submitted' in request.GET:
            submitted = True
        if 'errormail' in request.GET:
            errormail = True
        if 'auth_email_failed' in request.GET:
            auth_email_failed = True
        return render(request, 'registration.html', {'form1': form1,
                                                     'form2': form2,
                                                     'regerr': regerr,
                                                     'pass_no_match': pass_no_match,
                                                     'mail_no_match': mail_no_match,
                                                     'errormail': errormail,
                                                     'submitted': submitted,
                                                     'auth_email_failed': auth_email_failed})


def verify_mail(request, slug):
    try:
        try:
            filterData = UserRegistrationToken.objects.get(
                user_email_token=slug)
            filterTime = filterData.user_email_token_created_on
        except Exception as e:
            print('verify_email error', e)
            messageData = {'message': 'Token is invalid. Please get a new confirmation mail from your dashboard.',
                           'responseType': 'success', 'token_type': 'email'}
            # return HttpResponse(json.dumps(messageData))
            context = {}
            context['messageData'] = messageData
            return render(request, 'email_password_template.html', context)

        if (filterTime == ''):
            messageData = {'message': 'Token is invalid. Please get a new confirmation mail from your dashboard.',
                           'responseType': 'success', 'token_type': 'email'}
        else:
            tokenCreateTime = filterTime.strftime("%Y-%m-%d %H:%M:%S")
            currentTime = dt.now().strftime("%Y-%m-%d %H:%M:%S")

            fmt = '%Y-%m-%d %H:%M:%S'
            tokenCreateTimeNew = dt.strptime(tokenCreateTime, fmt)
            currentTimeNew = dt.strptime(currentTime, fmt)
            print(tokenCreateTimeNew)
            print(currentTimeNew)
            minutesDifference = currentTimeNew - tokenCreateTimeNew
            diff_minutes = (minutesDifference.days * 24 * 60) + \
                (minutesDifference.seconds / 60)

            if diff_minutes >= 5:
                messageData = {'message': 'Token is invalid. Please get a new confirmation mail from your dashboard.',
                               'responseType': 'success', 'token_type': 'email'}
                # if (filterData.user_password_token == ''):
                #     UserRegistrationToken.objects.filter(user_email=filterData.user_email).delete()
                # else:
                #     UserRegistrationToken.objects.filter(user_email=filterData.user_email).update(user_email_token='',user_email_token_created_on='')
            else:
                Users.objects.filter(
                    user=filterData.user_email).update(status='active')
                filterUserTable = Users.objects.get(user=filterData.user_email)
                if (filterData.user_password_token == ''):
                    UserRegistrationToken.objects.filter(
                        user_email=filterData.user_email).delete()
                else:
                    UserRegistrationToken.objects.filter(user_email=filterData.user_email).update(
                        user_email_token='', user_email_token_created_on='')
                html_message = loader.render_to_string('static/common/welcome_email_template.html', {
                    'firstname': filterUserTable.firstname,
                    'lastname': filterUserTable.lastname,
                })

                # send welcome template
                send_mail('Welcome to Ercess', 'message', email_sent_from, [
                          filterData.user_email], fail_silently=False, html_message=html_message)
                messageData = {'message': 'We were successful to verify your email address. You can proceed with login now.',
                               'responseType': 'success', 'token_type': 'email'}
                # ends here ~ send welcome template

        # return HttpResponse(json.dumps(messageData))
        context = {}
        context['messageData'] = messageData
        return render(request, 'email_password_template.html', context)
    except Exception as e:
        print('error is ', e)
        messageData = {'message': 'Something went wrong. Please try again.',
                       'responseType': 'error', 'token_type': 'email'}
        context = {}
        context['messageData'] = messageData
        return render(request, 'email_password_template.html', context)


'''
def registration(request):
    print('in view')
    regerr =False
    pass_no_match = False
    mail_no_match = False
    auth_email_failed = False
    submitted = False
    sec_code = None
    errormail = False
    x =0
    if request.method == 'POST':
        form1  = UserForm(request.POST)
        form2 = RegistrationForm(request.POST)
        if form1.is_valid() and form2.is_valid() :
            print('after validation')
            firstname = request.POST.get('firstname','')
            lastname = request.POST.get('lastname','')
            email = request.POST.get('email','')
            cemail = request.POST.get('confirmmail','')
            password = request.POST.get('password','')
            re_enter_password = request.POST.get('reenter_password','')

            # print(firstname, lastname , email ,cemail ,password , re_enter_password)
            if email != cemail :
                return redirect('/live/signup?mail_no_match=True')
            if password!= re_enter_password :
                return redirect('/live/signup?pass_no_match=True')

            data = User.objects.filter(email=email)
            print(data)
            if not data :
                try:
                    user = User.objects.create_user(username=email ,
                                                    first_name = firstname ,
                                                    last_name = lastname ,
                                                    email=email ,
                                                    password=password)
                    user.save()
                    u = authenticate(username=email, password=password , email=email)

                    # print('before auth save')
                    print(u.save())
                    # print('after auth save')
                    # mobile = request.POST.get('mobile','')
                    gender = request.POST.get('gender', '')
                    location = request.POST.get('location', '')
                    reg = RegistrationData(
                        user=user,
                        gender= gender,
                        location= location
                    )
                    x = reg.save()
                    pswd_encoded = md5(password.encode('utf-8')).hexdigest()
                    new_user = Users(user=email, firstname = firstname,
                                     lastname = lastname, password=pswd_encoded,
                                     gender= gender, location= location)

                    new_user.save()
                except Exception as e:
                    print('exception in register')
                    print(e)
                    return redirect('/live/signup?regerr=True')
            else:
                return redirect('/live/signup?regerr=True')
            if x is not None:
                return redirect('/live/signup?regerr=True')
            else :
                try:
                    sec_code = get_sec_code()
                    print('-------------')
                    print(sec_code)
                    res = send_mail('Verify email', 'http://127.0.0.1:8000/live/verify_email/?email='+email+'&token='+sec_code + '\n\n\n' + 'verify your email !!!',
                                    'no-reply@ercess.com', [email, ])
                except Exception as e:
                    #print(res)
                    print(e)
                    return redirect('/live/signup?errormail=True')
                else:
                    # add email and seccode to dict
                    set_key_email(email, sec_code)
                    return redirect('/live/signup?submitted=True')
        form1 = UserForm()
        form2 = RegistrationForm()
        return render(request, 'registration.html', {'form1': form1, 'form2': form2})
    else :
        form1 = UserForm()
        form2 = RegistrationForm()
        if 'regerr' in request.GET:
            regerr = True
        if 'pass_no_match' in request.GET:
            pass_no_match = True
        if 'mail_no_match' in request.GET:
            mail_no_match = True
        if 'submitted' in request.GET:
            submitted = True
        if 'errormail' in request.GET:
            errormail = True
        if 'auth_email_failed' in request.GET:
            auth_email_failed = True
        return render(request , 'registration.html',{'form1':form1 ,
                                                     'form2':form2 ,
                                                     'regerr':regerr,
                                                     'pass_no_match':pass_no_match,
                                                     'mail_no_match':mail_no_match ,
                                                     'errormail':errormail,
                                                     'submitted':submitted ,
                                                     'auth_email_failed':auth_email_failed})

'''


def set_key_email(email, sec_code):
    key1 = str(email)
    key2 = key1 + 'sc'
    email_verify_dict[key1] = email
    email_verify_dict[key2] = sec_code


'''
def verify_mail(request):
    if request.method == 'GET':
        if 'token' in request.GET:
            token = request.GET.get('token', '')
        if 'email' in request.GET:
            email = request.GET.get('email', '')

        key1 = str(email)
        key2 = key1 + 'sc'

        if key1 in email_verify_dict and key2 in email_verify_dict:
            print('exist')
            #set value 1 in db and redirect to login
            u = User.objects.get(email=email)
            print(u)
            r = RegistrationData.objects.get(user_id=u.pk)
            r.verify = 1
            r.save()

            print('pop out keys')

            print(email_verify_dict.pop(key1))
            print(email_verify_dict.pop(key2))

            return  redirect('/live/login?verified=True')
        else:
            print('no')
            #show error that authentication failed
            return redirect('/live/signup?auth_email_failed=True')

'''


@csrf_exempt
def loginview(request):
    loginerror = False
    error = False
    verify_error = False
    verified = False
    mail = False
    contact = False
    submitted = False
    passchange = False
    if request.method == 'POST':
        requestData = request.body
        requestDataDecode = requestData.decode('utf8').replace("'", '"')
        requestDataJson = json.loads(requestDataDecode)

        email = requestDataJson['emalVal']
        password = requestDataJson['passVal']

        print('after login form validation')

        pswd_encoded = md5(password.encode('utf-8')).hexdigest()

        if Users.objects.filter(user=email).exists():

            if Users.objects.filter(user=email, password=pswd_encoded).exists():

                u = Users.objects.get(user=email)

                #status = u.status
                # if status=='active':
                request.session['username'] = email
                request.session['userid'] = u.id
                request.session['firstname'] = u.firstname
                request.session['lastname'] = u.lastname

                request.session.modified = True
                # us = authenticate(username=email, password=password)
                # if us:
                #   next_url = request.GET.get('next')
                #  print(next_url)
                # if next_url:
                print(request)
                print(request.session.keys())
                messageData = {'url': '/live/dashboard/add-event',
                               'responseType': 'success', 'messageType': 'success'}
                return HttpResponse(json.dumps(messageData))
                # return HttpResponseRedirect('/live/dashboard/add-event')
                # return redirect('dashboard:step_one')
                # else:
                #   return redirect('dashboard:how')
                # else :
                #   messageData = {'message':'Verify your email','responseType':'success', 'messageType':'success'}
                #  return HttpResponse(json.dumps(messageData))
                # return redirect('/live/login?verify_error=True')
            else:
                messageData = {'message': 'Invalid details provided',
                               'responseType': 'success', 'messageType': 'error'}
                return HttpResponse(json.dumps(messageData))
                # return redirect('/live/login?error=True')
        else:
            messageData = {'message': 'Oops! this user does not exist in our record.',
                           'responseType': 'success', 'messageType': 'error'}
            return HttpResponse(json.dumps(messageData))
       # print('checkkkkkk----------------------------------------------')
       # print(form.errors)
        #form = LoginForm()
        # return render(request, 'login.html', {'form': form})
    else:
        form = LoginForm()
        if 'loginerror' in request.GET:
            loginerror = True
        if 'error' in request.GET:
            error = True
        if 'mail' in request.GET:
            mail = True
        if 'contact' in request.GET:
            contact = True
        if 'submitted' in request.GET:
            submitted = True
        if 'passchange' in request.GET:
            passchange = True
        if 'verify_error' in request.GET:
            verify_error = True
        if 'verified' in request.GET:
            verified = True
        return render(request, 'login.html', {'form': form, 'loginerror': loginerror, 'error': error,
                                              'mail': mail, 'contact': contact,
                                              'submitted': submitted, 'passchange': passchange,
                                              'verify_error': verify_error,
                                              'verified': verified})


'''
def loginview(request):
    error = False
    verify_error = False
    verified = False
    mail = False
    contact =False
    submitted = False
    passchange = False
    if request.method == 'POST':
        form = LoginForm(request.POST)
        print('before validation')
        if form.is_valid():
            print('after validation')
            email = request.POST.get('email' ,'')
            password = request.POST.get('password', '')
            # print(username)
            # print(password)
            user = authenticate(username = email , password = password)
            # print('user in login view')
            print('user')
            print(user)
            if user :

                u = User.objects.get(email=email)
                print(u)
                r = RegistrationData.objects.get(user_id= u.pk )
                print('in views of ercess corp')
                verify = r.verify
                if verify:
                    print(r.submitted)
                    request.session['sub'] = r.submitted
                    print(request.session['sub'])
                    request.session['username'] = email
                    login(request, user)
                    return redirect('dashboard:how')
                else :
                    return redirect('/live/login?verify_error=True')
            else :
                return redirect('/live/login?error=True')
        form = LoginForm()
        return render(request, 'login.html', {'form': form})
    else:
        form = LoginForm()
        if 'error' in request.GET:
            error = True
        if 'mail' in request.GET:
            mail = True
        if 'contact' in request.GET:
            contact = True
        if 'submitted' in request.GET:
            submitted = True
        if 'passchange' in request.GET:
            passchange = True
        if 'verify_error' in request.GET:
            verify_error = True
        if 'verified' in request.GET:
            verified = True
        return render(request, 'login.html', {'form': form ,'error':error ,
                                              'mail':mail ,'contact':contact ,
                                              'submitted':submitted ,'passchange':passchange,
                                              'verify_error':verify_error,
                                              'verified':verified})
'''
@csrf_exempt
def forgotPassword(request):
    try:
        errormail = False
        usernotexist = False
        res = 0
        if request.method == 'POST':
            try:
                # read request data
                requestData = request.body
                print('requestData', requestData)
                requestDataDecode = requestData.decode(
                    'utf8').replace("'", '"')
                requestDataJson = json.loads(requestDataDecode)
                # ends here ~ read request data

                # set value into variable
                emailVal = requestDataJson['emalVal']
                # ends here ~ set value into variable

                filterData = Users.objects.filter(user=emailVal)
                if len(filterData) == 0:
                    messageData = {'message': 'Oops! this user does not exist in our record.',
                                   'responseType': 'success', 'messageType': 'error'}
                else:
                    filterUserData = Users.objects.get(user=emailVal)
                    password_token = str(uuid.uuid4()) + str(filterUserData.id)

                    # save token into db
                    currentTime = dt.now().strftime("%Y-%m-%d %H:%M:%S")
                    user_registration_token_filter_data = UserRegistrationToken.objects.filter(
                        user_email=emailVal)
                    if len(user_registration_token_filter_data) == 0:
                        UserRegistrationToken.objects.create(
                            user_password_token=password_token, user_email=emailVal, user_password_token_created_on=currentTime)
                    else:
                        UserRegistrationToken.objects.filter(user_email=emailVal).update(
                            user_password_token=password_token, user_password_token_created_on=currentTime)
                    # ends here ~ save token into db

                    verify_url = 'http://' + request.get_host() + '/live/reset_password/' + \
                        password_token + '/'
                    # send email
                    html_message = loader.render_to_string('static/common/forget_password_template.html',
                                                           {
                                                               'verify_url': verify_url
                                                           })
                    print('emailVal', emailVal)
                    print('email_sent_from', email_sent_from)
                    send_mail('Reset Password - Ercess', 'message', email_sent_from,
                              [emailVal], fail_silently=False, html_message=html_message)
                    # ends here ~ send email

                    messageData = {'message': 'Please check your email to reset password.',
                                   'responseType': 'success', 'messageType': 'success'}

                return HttpResponse(json.dumps(messageData))

            except Exception as e:
                print('error is', e)
        else:
            form = ForgotPasswordForm()
            if 'errormail' in request.GET:
                errormail = True
            if 'usernotexist' in request.GET:
                usernotexist = True
            return render(request, 'fogotpassword.html', {'form': form, 'errormail': errormail, 'usernotexist': usernotexist})
    except Exception as e:
        print('error is ', e)


@csrf_exempt
def setNewPassword(request):
    try:
        # read request data
        requestData = request.body
        requestDataDecode = requestData.decode('utf8').replace("'", '"')
        requestDataJson = json.loads(requestDataDecode)
        # ends here ~ read request data

        print(requestDataJson)
        # get all required values
        slugValue = requestDataJson['slugVal']
        passwordValue = requestDataJson['passVal']
        # ends here ~ get all required values

        # code for changed password
        try:
            filterData = UserRegistrationToken.objects.get(
                user_password_token=slugValue)
            pswd_encoded = hashlib.md5(
                passwordValue.encode('utf-8')).hexdigest()
            Users.objects.filter(user=filterData.user_email).update(
                password=pswd_encoded)
            # ends here ~ code for changed password

            if (filterData.user_email_token == ''):
                UserRegistrationToken.objects.filter(
                    user_email=filterData.user_email).delete()
            else:
                UserRegistrationToken.objects.filter(user_email=filterData.user_email).update(
                    user_password_token='', user_password_token_created_on='')
            messageData = {'url': '/live/login/', 'message': 'Your password was reset successfully.',
                           'responseType': 'success', 'token_type': 'password', 'messageType': 'success'}
            return HttpResponse(json.dumps(messageData))
        except Exception as e:
            messageData = {'message': 'Token is already used to reset your password.',
                           'responseType': 'success', 'token_type': 'password', 'messageType': 'error'}
            return HttpResponse(json.dumps(messageData))

    except Exception as e:
        raise


def resetPassword(request, slug):
    try:
        usernotexist = False
        passnotmatch = False
        if request.method == 'POST':
            pass
            # # read request data
            # requestData = request.body
            # requestDataDecode = requestData.decode('utf8').replace("'", '"')
            # requestDataJson = json.loads(requestDataDecode)
            # # ends here ~ read request data

            # print(requestDataJson)

        else:
            try:
                filterData = UserRegistrationToken.objects.get(
                    user_password_token=slug)
                filterTime = filterData.user_password_token_created_on
            except Exception as e:
                messageData = {'message': 'Your token is expired. Please try again.',
                               'responseType': 'success', 'token_type': 'password', 'messageType': 'error'}
                context = {}
                context['messageData'] = messageData
                return render(request, 'resetpassword.html', context)

            if (filterTime == ''):
                messageData = {'message': 'Your token is expired. Please try again.',
                               'responseType': 'success', 'token_type': 'password', 'messageType': 'error'}
            else:
                tokenCreateTime = filterTime.strftime("%Y-%m-%d %H:%M:%S")
                currentTime = dt.now().strftime("%Y-%m-%d %H:%M:%S")

                fmt = '%Y-%m-%d %H:%M:%S'
                tokenCreateTimeNew = dt.strptime(tokenCreateTime, fmt)
                currentTimeNew = dt.strptime(currentTime, fmt)

                minutesDifference = currentTimeNew - tokenCreateTimeNew
                diff_minutes = (minutesDifference.days * 24 *
                                60) + (minutesDifference.seconds / 60)

                if diff_minutes >= 2880:
                    messageData = {'message': 'Your token is expired. Please try again.',
                                   'responseType': 'success', 'token_type': 'password', 'messageType': 'error'}
                else:
                    messageData = {'message': 'Your toke to reset password is valid.', 'responseType': 'success',
                                   'token_type': 'password', 'messageType': 'success', 'email': filterData.user_email}
                # return HttpResponse(json.dumps(messageData))
                context = {}
                context['messageData'] = messageData
                return render(request, 'resetpassword.html', context)
                # form = ResetPassword()
                # return render(request, 'resetpassword.html',
                #                   {'form': form})
    except Exception as e:
        print('error is ', e)


'''
def forgotPassword(request):
    errormail = False
    usernotexist = False
    res = 0
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = request.POST.get('email','')
            # print(email)
            try :
                u = User.objects.get(email=email)
            except :
                return redirect('/live/forgot_password?usernotexist=True')
            if  u :
                try:
                    res = send_mail('Change your password', 'http://127.0.0.1:8000/live/reset_password/?token='+get_sec_code() + '\n\n\n' + 'change your password within 5 minutes !!!', 'no-reply@ercess.com', [email,])
                    clear_list()
                except Exception as e:
                    print(res)
                    print(e)
                    pass
                if res  == 1:
                    # give submission message to user
                    return redirect('/live/login?mail=True')
                else :
                    # give error to user
                    return redirect('/live/forgot_password?errormail=True')

            else :
                #raise user doesnot exist
                return redirect('/live/forgot_password?usernotexist=True')
        form = ForgotPasswordForm()
        return render(request, 'fogotpassword.html', {'form': form})
    else:
        form = ForgotPasswordForm()
        if 'errormail' in request.GET:
            errormail = True
        if 'usernotexist' in request.GET:
            usernotexist = True
        return render(request, 'fogotpassword.html', {'form': form ,'errormail':errormail ,'usernotexist':usernotexist})

def resetPassword(request):
    usernotexist = False
    passnotmatch = False
    if request.method == 'POST':
        form = ResetPassword(request.POST)
        if form.is_valid():
            email = request.POST.get('email', '')
            password = request.POST.get('password','')
            rpassword = request.POST.get('rpassword', '')
            try:
                u = User.objects.get(email=email)
            except :
                return redirect('/live/reset_password?usernotexist=True')
            if  u :
                if password == rpassword :
                    u.set_password(password)
                    u.save()
                    return redirect('/live/login?passchange=True')
                else :
                    #raiseerror password not matching
                    return redirect('/live/reset_password?passnotmatch=True')
            else :
                #raise user does not exist
                return redirect('/live/reset_password?usernotexist=True')
        form = ResetPassword()
        return render(request, 'resetpassword.html', {'form': form})
    else:
        form = ResetPassword()

        if 'usernotexist' in request.GET:
            usernotexist = True
        if 'passnotmatch' in request.GET:
            passnotmatch = True
        if 'token' in request.GET:
            token = request.GET.get('token', '')
            res = check_token(token)
            print(res)
            if res == 1 :
                return render(request, 'resetpassword.html',
                              {'form': form, 'usernotexist': usernotexist, 'passnotmatch': passnotmatch})
            elif res == 0 :
                return render(request , 'request_timeout.html')
        else :
            return render(request, '403.html')
        return render(request, 'resetpassword.html',
                      {'form': form, 'usernotexist': usernotexist, 'passnotmatch': passnotmatch})
'''


def home(request):
    try:

        try:
            print('trying to delete session data',
                  request.session.get('username'))
            del request.session['username']
            request.session.modified = True
        except Exception as e:
            print(e)
        try:
            print('trying to delete session  sub data',
                  request.session.get('sub'))
            del request.session['sub']
            request.session.modified = True
        except Exception as e:
            print(e)
        try:
            logout(request)
        except Exception as e:
            print(e)
    except Exception as e:
        print(e)
    return render(request, 'index.html')


def multichannelpromotion(request):
    # print('multichannel promotion')
    return render(request, 'multichannel_promotion.html')


def sellstallspaces(request):
    return render(request, 'stall_spaces.html')


def advertisement(request):
    return render(request, 'paid-advertisement.html')


def howitworks(request):
    # print('inside how it works')
    return render(request, 'how-it-works.html')
#
# def createevent(request):
#     pass
#
#
# def manageevents(request):
#     pass
#
#
# def salesreport(request):
#     pass


def aboutus(request):
    return render(request, 'about-us.html')


def contactus(request):
    res = 0
    x = 0
    send_to = 'no-reply@ercess.com'
    contactregerror = False
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data.get('name', '')
            email = form.cleaned_data.get('email', '')
            mobile = form.cleaned_data.get('mobile', '')
            purpose = form.cleaned_data.get('purpose', '')
            comment = form.cleaned_data.get('comment', '')
            try:
                res = send_mail('Customer Query', 'contact details of customer' + 'name : ' + name + 'email : ' + email + 'phone no :' + str(mobile)
                                + 'purpose :' + purpose + 'comments :' + comment, email, [email, ])

                con = ContactData(
                    username=name,
                    email=email,
                    mobile=mobile,
                    purpose=purpose,
                    comment=comment
                )

                x = con.save()

            except Exception as e:
                print(e)

            if res == 1 and x is None:
                # give submission message to user
                return redirect('/live/login?contact=True')
            else:
                # give error to user
                return redirect('/live/contact?contactregerror=True')
        form = ForgotPasswordForm()
        return render(request, 'contact-us.html', {'form': form})
    else:
        form = ContactForm()
        if 'contactregerror' in request.GET:
            contactregerror = True
        return render(request, 'contact-us.html', {'form': form, 'contactregerror': contactregerror})


def blog(request):
    data = BlogData.objects.all()
    return render(request, 'blog.html', {'data': data[0], 'desc': data[0].description[0:300]})


def blogpost(request, pk):

    data = BlogData.objects.get(pk=pk)
    return render(request, 'blog-post.html', {'data': data})


def career(request):
    return render(request, 'careers.html')


def pricing(request):
    return render(request, 'pricing.html')


def partners(request):
    return render(request, 'partners.html')


def marketing(request):
    pass


def privacypolicy(request):
    return render(request, 'privacy-policy.html')


def logoutview(request):
    time = timezone.now()
    username = request.session.get('username')
    print(username)

    try:
        if not request.session.get('username'):
            return redirect('/live/')
        # logout(request)
        # print('trying to delete session data', request.session.get('username'))
        if 'admin_id' in request.session.keys():
            action = AdminActionLog()
            action.admin_id = request.session['admin_id']
            print(action.admin_id)
            print("--------------------------------")
            action.timestamp = time
            action.parameter = "log-out"
            action.event_id = 0
            action.action_taken = "logged out"
            action.save()
        print('--------------------')
        for key in list(request.session.keys()):
            del request.session[key]

        #del request.session['username']
        #del request.session['sub']
        #print('data deleted')
        #print('auth logging out')
        # print(request.session.keys())
        # request.session.flush()
        # request.session = {}
        # print(request.session.keys())

        return render(request, 'index.html')

    except:
        print('unable to delete')
        return render(request, 'index.html')


def blogdetails(request):
    blogs = BlogData.objects.all()
    data = {"results": list(blogs.values(
        'blog_id', 'title', 'author', 'date', 'description'))}
    return JsonResponse(data)


def blogspecific(request, pk):
    blog = get_object_or_404(BlogData, pk=pk)
    data = {
        "results": {
            'blog_id': blog.blog_id,
            'title': blog.title,
            'author': blog.author,
            'date': blog.date,
            'description': blog.description
        }
    }
    return JsonResponse(data)


def bad_request(request):
    response = render_to_response('400.html')
    response.status_code = 400
    return response


def permission_denied(request):
    response = render_to_response('403.html')
    response.status_code = 403
    return response


def page_not_found(request):
    response = render_to_response('404.html')
    response.status_code = 404
    return response


def server_error(request):
    response = render_to_response('500.html')
    response.status_code = 500
    return response


def get_sec_code():
    sc = secrets.token_hex(16)
    l.append(sc)
    print(l)
    return sc


def check_token(token):
    flag = 0
    print('token' + token)
    print('list' + str(l))
    for scc in l:
        print(scc)
        if scc == token:
            flag = 1
    if flag == 1:
        return 1
    else:
        return 0


def clear_list():
    timeout = time.time() + 60 * 5
    while True:
        if time.time() > timeout:
            l.clear()
            break


def manageevents(request):
    if 'userid' not in request.session.keys():
        return redirect('/live/login')
    e = []
    r = request.session.get('userid')
    print(r)
    l = StatusPromotionTicketing.objects.all().filter(
        connected_user=r, complete_details=1).values('event_id').order_by('-event_id')
    d = StatusPromotionTicketing.objects.all().filter(
        connected_user=r, complete_details=0).values('event_id').order_by('-event_id')
    now = datetime.now(tz=timezone.utc)
    print(l, d)
    tot_count = [len(l) + len(d)]
    print(tot_count)
    pr = []
    up = []
    pn = []
    un = []
    psd = []
    usd = []
    u_src = []
    p_src = []
    d_src = []
    pc = 0
    uc = 0
    for i in range(0, (len(l))):
        print(i)
        p = Articles2.objects.all().filter(edate__lt=now, id=l[i]['event_id'])
        u = Articles2.objects.all().filter(edate__gt=now, id=l[i]['event_id'])
        if len(p) != 0:
            pr.append(p.values('id')[0]['id'])
            pn.append(p.values('event_name')[0]['event_name'])
            psd.append(p.values('sdate')[0]['sdate'])
            p_src.append(p.values('banner')[0]['banner'])

        elif len(u) != 0:
            up.append(u.values('id')[0]['id'])
            un.append(u.values('event_name')[0]['event_name'])
            usd.append(u.values('sdate')[0]['sdate'])
            u_src.append(u.values('banner')[0]['banner'])
    stat = []
    for i in up:
        # print(i)
        st = StatusPromotionTicketing.objects.all().filter(event_id=i)
        # print(st)
        if len(st) != 0:
            stat.append(st.values('event_active')[0]['event_active'])
    print(up)
    print(stat)

    # admin_mobile
    admin_mobile = []
    print("--------admin mobile section -------------------")
    for i in range(0, len(up)):
        # print("---------")
        # print(stat)
        # print(up[i])
        if stat[i] == 5:
            # @author Shubham
            a_m = AdminEventAssignment.objects.all().filter(event_id=up[i])
            # a_m = Admin_Event_Assignment.objects.all().filter(event_id=up[i])
            # ends here ~ @author Shubham
            # print(a_m)
            if len(a_m) != 0:
                a_id = (a_m.values('admin_id')[0]['admin_id'])
                print(a_id)
                ad_m = Admin.objects.all().filter(table_id=a_id)
                print(ad_m)
                if len(ad_m) != 0:
                    num = ad_m[0].mobile
                    print(num)
                    if num != None:
                        admin_mobile.append(num)
                    elif num == None:
                        num = '9886188705'
                        admin_mobile.append(num)

                else:
                    admin_mobile.append('9886188705')
                    # print('nested else')
            else:
                admin_mobile.append('9886188705')
                # print("in this")
        elif stat[i] != 5:
            admin_mobile.append('')

    # for i in t_id:
    #     ad_m=Admin.objects.all().filter(table_id=i)
    #     if len(ad_m)!=0:
    #         admin_mobile.append(ad_m.values('mobile')[0]['mobile'])
    #     else:
    #         admin_mobile.append('9886188705')
    print(admin_mobile)
    print("----------admin mobile--------------")
    print(up)
    print(un)
    print(usd)
    print(stat)
    print(u_src)
    upcm = itertools.zip_longest(up, un, usd, stat, admin_mobile, u_src)
#    upcm = zip(up,un,usd,stat,admin_mobile,u_src)
#    print("UPCNM",list(upcm))
    upcm_count = [len(up)]
    # for previous meetings

    # qy=[]
    # qk=[]
    #
    # for k in pr:
    #     q = Tickets_Sale.objects.all().filter(event_id=k).values('table_id')
    #     for h in q:
    #         qy
    #         qk.append(h['table_id'])
    #     qy.append(qk)
    # qty = []
    # qt =[]
    # for i in qy:
    #     for t in i:
    #         qty_l = Tickets_Sale.objects.all().filter(table_id=t).values('qty')
    #         qt.append(qty_l[0]['qty'])
    #     qty.append(qt)
    #
    # val=0
    # value = []
    # for i in qty:
    #     for t in i:
    #         val=val+t
    #     value.append(val)

    print("tickets--------------------------------")
    print(pr)
    value = []

    for i in pr:

        # @author Shubham
        tickt = TicketsSale.objects.all().filter(event_id=i)
        # tickt = Tickets_Sale.objects.all().filter(event_id=i)
        # ends here ~ @author Shubham


        if len(tickt) != 0:
            sum = 0
            for i in tickt:
                if (i.qty != None):
                    sum += i.qty
            value.append(sum)
        else:
            value.append(0)

    print(value)

    int_c = []
    for k in pr:


        # @author Shubham
        ct = Rsvp.objects.all().filter(event_id=k).values('table_id').count()
        # ct = Rsvp.objects.all().filter(event_id=k).values('table_id').count()
        # ends here ~ @author Shubham

        int_c.append(ct)

    prev = zip(pr, pn, psd, value, int_c, p_src)
    prev_count = [len(pr)]

    # draft
    d_id = []
    d_n = []
    d_sd = []
    draft_count = [len(d)]
    # print(d)
    for i in d:
        # print(i)
        dr = Articles2.objects.all().filter(id=i['event_id'])
        # print(dr)
        if len(dr) != 0:
            d_id.append(dr.values('id')[0]['id'])
            d_n.append(dr.values('event_name')[0]['event_name'])
            d_sd.append(dr.values('sdate')[0]['sdate'])
            d_src.append(dr.values('banner')[0]['banner'])

    # print(d_id)
    draft = zip(d_id, d_n, d_sd, d_src)
    print(tot_count, upcm_count, prev_count, draft_count)
    count = zip(tot_count, upcm_count, prev_count, draft_count)
    return render(request, 'dashboard/organizer_dashboard.html', {'prev': prev, 'upcm': upcm, 'draft': draft, 'count': count})


def RSVP(request):
    if 'userid' not in request.session.keys():
        return redirect('/live/login')
    user = request.session.get('userid')
    print(user)

    ticketing = StatusPromotionTicketing.objects.all().filter(connected_user=user, complete_details=1).exclude().values(
        'event_id').order_by('-event_id')
    print(ticketing)
    count_t = len(ticketing)
    now = datetime.now()

    # upcoming tab
    up_id = []
    up_sdate = []
    up_name = []
    up_ban = []
    up_city = []

    # past_tab
    pa_id = []
    pa_sdate = []
    pa_name = []
    pa_ban = []
    pa_city = []

    for i in range(0, count_t):
        up_eve = Articles2.objects.filter(sdate__gt=now, id=ticketing[i]['event_id']).all() | Articles2.objects.filter(
            edate__gt=now, id=ticketing[i]['event_id']).all()

        pa_eve = Articles2.objects.filter(
            edate__lt=now, id=ticketing[i]['event_id']).all()

        if len(up_eve) != 0:
            up_id.append(up_eve.values('id')[0]['id'])
            up_sdate.append(up_eve.values('sdate')[0]['sdate'])
            up_name.append(up_eve.values('event_name')[0]['event_name'])
            up_ban.append(up_eve.values('banner')[0]['banner'])
            up_city.append(up_eve.values('city')[0]['city'])

        elif len(pa_eve) != 0:
            pa_id.append(pa_eve.values('id')[0]['id'])
            pa_sdate.append(pa_eve.values('sdate')[0]['sdate'])
            pa_name.append(pa_eve.values('event_name')[0]['event_name'])
            pa_ban.append(pa_eve.values('banner')[0]['banner'])
            pa_city.append(pa_eve.values('city')[0]['city'])
    # RSVP count for upcoming tab
    print(up_id)
    up_count = []
    for i in up_id:
        rsv = Rsvp.objects.all().filter(event_id=i)
        print(rsv)
        if len(rsv) != 0:
            count = 0
            for i in rsv:
                count += 1
            up_count.append(count)
        elif len(rsv) == 0:
            up_count.append(0)
    print(up_count)

    # RSVP count for past tab
    print(pa_id)
    pa_count = []
    for i in pa_id:
        rsv = Rsvp.objects.all().filter(event_id=i)
        print(rsv)
        if len(rsv) != 0:
            count = 0
            for i in rsv:
                count += 1
            pa_count.append(count)
        elif len(rsv) == 0:
            pa_count.append(0)
    print(pa_count)

    upcoming = zip(up_id, up_name, up_sdate, up_ban, up_city, up_count)
    u_cnt = len(up_id)
    past = zip(pa_id, pa_name, pa_sdate, pa_ban, pa_city, pa_count)
    p_cnt = len(pa_id)

    return render(request, 'dashboard/RSVP.html', {'upcoming': upcoming, 'u_cnt': u_cnt, 'p_cnt': p_cnt,
                                                   'past': past, 't_count': count_t})


def getInquiries(request):
    if 'userid' not in request.session.keys():
        return redirect('/live/login')
    return render(request, 'dashboard/inquiries.html')


def getSales(request):
    if 'userid' not in request.session.keys():
        return redirect('/live/login')
    user = request.session.get('userid')

    ticketing = StatusPromotionTicketing.objects.all().filter(connected_user=user,
                                                              complete_details=1).exclude().values('event_id').order_by('-event_id')
    print(ticketing)
    count_t = len(ticketing)
    now = datetime.now()

    # upcoming tab
    up_id = []
    up_sdate = []
    up_name = []
    up_ban = []
    up_city = []

    # past_tab
    pa_id = []
    pa_sdate = []
    pa_name = []
    pa_ban = []
    pa_city = []

    for i in range(0, count_t):
        up_eve = Articles2.objects.filter(sdate__gt=now, id=ticketing[i]['event_id']).all() | Articles2.objects.filter(
            edate__gt=now, id=ticketing[i]['event_id']).all()

        pa_eve = Articles2.objects.filter(
            edate__lt=now, id=ticketing[i]['event_id']).all()

        if len(up_eve) != 0:
            up_id.append(up_eve.values('id')[0]['id'])
            up_sdate.append(up_eve.values('sdate')[0]['sdate'])
            up_name.append(up_eve.values('event_name')[0]['event_name'])
            up_ban.append(up_eve.values('banner')[0]['banner'])
            up_city.append(up_eve.values('city')[0]['city'])

        elif len(pa_eve) != 0:
            pa_id.append(pa_eve.values('id')[0]['id'])
            pa_sdate.append(pa_eve.values('sdate')[0]['sdate'])
            pa_name.append(pa_eve.values('event_name')[0]['event_name'])
            pa_ban.append(pa_eve.values('banner')[0]['banner'])
            pa_city.append(pa_eve.values('city')[0]['city'])

    # count of ticket sale upcoming events
    up_sale = []

    print(up_id)
    for i in up_id:

        # @author Shubham
        sale = TicketsSale.objects.all().filter(event_id=i).values('qty')
        #  sale = Tickets_Sale.objects.all().filter(event_id=i).values('qty')
        # ends here ~ @author Shubham

        u_s = 0
        print(sale)

        if len(sale) != 0:
            for i in sale:
                print(i)
                qty = i['qty']
                u_s += qty
            up_sale.append(u_s)
        elif len(sale) == 0:
            up_sale.append(0)
    print(up_sale)

    # count of ticket sale past events
    pa_sale = []

    for i in pa_id:

        # @author Shubham
        sale = TicketsSale.objects.all().filter(event_id=i).values('qty')
        # sale = Tickets_Sale.objects.all().filter(event_id=i).values('qty')
        # ends here ~ @author Shubham
        p_s = 0

        if len(sale) != 0:
            for i in sale:
                qty = i['qty']
                p_s += qty
            pa_sale.append(p_s)
        elif len(sale) == 0:
            pa_sale.append(0)
    print(pa_sale)

    upcoming = zip(up_id, up_name, up_sdate, up_ban, up_city, up_sale)
    up_count = len(up_id)

    past = zip(pa_id, pa_name, pa_sdate, pa_ban, pa_city, pa_sale)
    pa_count = len(pa_id)

    total_count = up_count + pa_count

    return render(request, 'dashboard/sales.html', {'upcoming': upcoming, 'up_count': up_count,
                                                    'past': past, 'pa_count': pa_count,
                                                    't_count': total_count})


def getHelp(request):
    return render(request, 'dashboard/help.html')


def profile(request):
    if 'userid' not in request.session.keys():
        return redirect('/live/login')

    user = Users.objects.get(pk=request.session['userid'])
    print(user)
    # print(id)
    # user = Users.objects.all().filter(id = id)
    # print(user)
    # , {'user_info': user}
    return render(request, 'dashboard/profile.html', {'user': user})


def settings(request):
    if 'userid' not in request.session.keys():
        return redirect('/live/login')

    return render(request, 'dashboard/settings.html')


def rsvp_event(request, event_id):
    rsv = Rsvp.objects.all().filter(event_id=event_id).order_by('-event_id')
    count = len(rsv)
    print('count', count)
    name = []
    email = []
    mobile = []
    recieved = []

    if count != 0:
        for i in rsv:
            name.append(i.attendee_name)
            email.append(i.attendee_email)
            mobile.append(i.attendee_contact)
            recieved.append(i.date_added)

    event = Articles2.objects.all().filter(id=event_id)
    eventname = ''

    for i in event:
        eventname = i.event_name
    print(eventname)

    items = zip(name, email, mobile, recieved)
    return render(request, 'dashboard/rsvp_event.html', {'count': count, 'items': items, 'eventname': eventname})


def event_details(request, event_id):
    if 'userid' not in request.session.keys():
        return redirect('/live/login')
    print(event_id)
    data = []
    e = Articles2.objects.all().filter(id=event_id)
    eve_id = e.values('id')[0]['id']
    name = [e.values('event_name')[0]['event_name']]

    img = [e.values('banner')[0]['banner']]
    create_date = e.values('date_added')[0]['date_added']

    # for complete details check
    print(e.values('id')[0]['id'])
    status_check = StatusPromotionTicketing.objects.filter(
        event_id=e.values('id')[0]['id']).values('complete_details')
    print(status_check)
    print(status_check[0]['complete_details'])
    status = False
    if status_check[0]['complete_details'] == 1:
        status = True

    #############################    ADMIN RELATION WITH THE EVENT   ###########################################
    print("admin------------------------ event---------------------assgnmnt")
    assigned = AdminEventAssignment.objects.all().filter(event_id=eve_id)
    print(assigned)

    if assigned:
        admin = Admin.objects.all().filter(table_id=assigned[0].admin_id)
        admin_name = admin[0].fname + " " + admin[0].lname
        print(admin_name)
        contact = admin[0].mobile
        print(contact)
    else:
        admin_name = ''
        contact = ''

    # for sale
    name_s = []
    amt = []
    qty = []


    # @author Shubham
    e_s = TicketsSale.objects.all().filter(event_id=event_id).order_by('-purchase_date').values('table_id')
    # e_s = Tickets_Sale.objects.all().filter(event_id=event_id).order_by('-purchase_date').values('table_id')
    # ends here ~ @author Shubham

    c_s = [len(e_s)]

    for i in range(0, len(e_s)):

        if i < 3:

            # @author Shubham
            d = TicketsSale.objects.all().filter(table_id=e_s[i]['table_id'])
            # d = Tickets_Sale.objects.all().filter(table_id=e_s[i]['table_id'])
            # ends here ~ @author Shubham
            name.append(d.values('attendee_name')[0]['attendee_name'])
            amt.append(d.values('ampunt_paid')[0]['ampunt_paid'])
            qty.append(d.values('qty')[0]['qty'])

    sale = zip(name, amt, qty)

    # for rsvp
    name_r = []
    cont = []
    email = []


    # @author Shubham
    e_r = Rsvp.objects.all().filter(event_id=event_id).order_by('-date_added').values('table_id')
    # e_r = Rsvp.objects.all().filter(event_id=event_id).order_by('-date_added').values('table_id')
    # ends here ~ @author Shubham

    for i in range(0, len(e_r)):
        if i < 3:


            # @author Shubham
            d = Rsvp.objects.all().filter(table_id=e_r[i]['table_id'])
            # d = Rsvp.objects.all().filter(table_id=e_r[i]['table_id'])
            # ends here ~ @author Shubham

            name_r.append(d.values('attendee_name')[0]['attendee_name'])
            cont.append(d.values('attendee_contact')[0]['attendee_contact'])
            email.append(d.values('attendee_email')[0]['attendee_email'])

    rsvp_d = zip(name_r, cont, email)
    c_r = [len(e_r)]

    data = zip(name, img, c_s, c_r)

    # for fail errors
    print("Fail errors---------------------------")
    veri_res = EventVerificationResult.objects.all().filter(event_id=event_id)
    print(veri_res.values('event_id'))
    veri_id = []
    if len(veri_res) != 0:
        for i in veri_res:
            if i.status == 'fail':
                veri_id.append(i.verified_against)
    veri_count = len(veri_id)
    print(veri_id)
    msg_to_org = []
    for i in veri_id:
        process = EventProcesses.objects.all().filter(process_id=i)
        msg_to_org.append(process[0].msg_to_org)

    print(msg_to_org)
    print("-------------------------fail errors")

    # for site
    s_n = []
    c_l = []
    c_ps = []
    c_p = []

    # s = StatusOnChannel.objects.all().filter(event_id=event_id).values('table_id')
    s = EventStatusOnChannel.objects.all().filter(event_id=event_id).values('table_id')
    s_len = len(s)
    print(s)
    for i in s:
        d = EventStatusOnChannel.objects.all().filter(table_id=i['table_id'])
        # d = StatusOnChannel.objects.all().filter(table_id=i['table_id'])
        s_i = PartnerSites.objects.all().filter(
            table_id=(d.values('site_id')[0]['site_id']))
        s_n.append(s_i.values('site_name')[0]['site_name'])
        c_l.append(d.values('link')[0]['link'])
        c_ps.append(d.values('promotion_status')[0]['promotion_status'])
        c_p.append(d.values('partner_status')[0]['partner_status'])

    print(c_l)

    print("Link ----------------------------------")
    print(c_l)
    site_link = []
    for i in c_l:
        if (i == None or i == '' or i == "None" or i == "none" or i == "NULL"):
            site_link.append(0)
        else:
            site_link.append(i)
    print(site_link)

    print("----------------------------------ends link")
    site = zip(s_n, site_link, c_ps, c_p)

    return render(request, 'dashboard/event_details.html', {'data': data, 'sale': sale, 'admin': admin_name,
                                                            'contact': contact, 'create': create_date,
                                                            'rsvp': rsvp_d, 'site': site,
                                                            'status': status, 's_len': s_len,
                                                            'eve_id': eve_id, 'veri_count': veri_count,
                                                            'msg_org': msg_to_org})


def legal(request):
    if 'userid' not in request.session.keys():
        return redirect('/live/login')

    return render(request, 'dashboard/legal.html')


def edit_event(request, event_id):
    if 'userid' not in request.session.keys():
        return redirect('/live/login')

    s = []
    now = datetime.now()
    d = Articles2.objects.all().filter(id=event_id)
    spe = StatusPromotionTicketing.objects.all().filter(
        event_id=event_id).values('approval')
    spea = spe[0]['approval']
    print(spea)
    if spea == 1:
        print("logs will be maintained")
    s.append(d.values('event_name')[0]['event_name'])
    s.append(d.values('website')[0]['website'])
    k = d.values('sdate')[0]['sdate']
    sl = now.replace(hour=k.hour, minute=k.minute, second=k.second,
                     microsecond=k.microsecond, year=k.year, month=k.month, day=k.day)
    # sd=datetime.date(k)
    print(sl)
    if k.month < 10:
        if k.day < 10:
            sda = '0' + str(k.day) + '/0' + str(k.month) + '/' + str(k.year)
        else:
            sda = str(k.day) + '/0' + str(k.month) + '/' + str(k.year)
    else:
        if k.day < 10:
            sda = '0' + str(k.day) + '/' + str(k.month) + '/' + str(k.year)
        else:
            sda = str(k.day) + '/' + str(k.month) + '/' + str(k.year)
    s.append(sda)
    s.append(d.values('start_time')[0]['start_time'])
    k1 = d.values('edate')[0]['edate']
    el = now.replace(hour=k1.hour, minute=k1.minute, second=k1.second,
                     microsecond=k1.microsecond, year=k1.year, month=k1.month, day=k1.day)

    # ed=datetime.date(k1)
    # print(ed)
    if k1.month < 10:
        if k1.day < 10:
            eda = '0' + str(k1.day) + '/0' + str(k1.month) + '/' + str(k1.year)
        else:
            eda = str(k1.day) + '/0' + str(k1.month) + '/' + str(k1.year)
    else:
        if k1.day < 10:
            eda = '0' + str(k1.day) + '/' + str(k1.month) + '/' + str(k1.year)
        else:
            eda = str(k1.day) + '/' + str(k1.month) + '/' + str(k1.year)
    print(eda)
    s.append(eda)
    s.append(d.values('end_time')[0]['end_time'])
    s.append(d.values('address_line1')[0]['address_line1'])
    s.append(d.values('address_line2')[0]['address_line2'])
    s.append(d.values('city')[0]['city'])
    s.append(d.values('state')[0]['state'])
    s.append(d.values('country')[0]['country'])
    s.append(d.values('pincode')[0]['pincode'])
    s.append(float(d.values('latitude')[0]['latitude']))
    s.append(float(d.values('longitude')[0]['longitude']))
    s.append(d.values('place_id')[0]['place_id'])
    # s.append(d.values('venue_not_decided')[0]['venue_not_decided'])
    print(s[1])
    par = ['event_name', 'website', 'sdate', 'start_time', 'eddate', 'end_time', 'address_line1',
           'address_line2', 'city', 'state', 'country', 'pincode', 'latitude', 'longitude', 'place_id']

    if request.method == 'POST':
        print(event_id)

        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        print(type(start))
        l = []
        articles2 = Articles2.objects.get(id=event_id)
        print(request.session['userid'])

        event_name = request.POST.get('event_name', '')
        l.append(event_name)
        website = request.POST.get('website', '')
        l.append(website)
        stdate = request.POST.get('sdate', '')
        sdate = now.replace(hour=0, minute=0, second=0, microsecond=0, year=int(
            stdate[6:]), month=int(stdate[3:5]), day=int(stdate[:2]))
        l.append(sdate)
        start_t = request.POST.get('start_time', '')
        print(len(start_t), start_t[6:], start_t[:2])

        if start_t[0] == '1' and start_t[1] != ':':
            if start_t[6:] == 'AM' and start_t[:2] != '12':
                start_time = now.time().replace(hour=int(start_t[:2]), minute=int(
                    start_t[3:5]), second=0, microsecond=0)
            elif start_t[6:] == 'AM' and start_t[:2] == '12':
                # print("herrrrrrrrrrrrreeeeeeeeeeeeeeeeeeeeeeeeeee")
                start_time = now.time().replace(hour=0, minute=int(
                    start_t[3:5]), second=0, microsecond=0)
            elif start_t[6:] == 'PM' and start_t[:2] == '12':
                start_time = now.time().replace(hour=int(start_t[:2]), minute=int(
                    start_t[3:5]), second=0, microsecond=0)
            else:
                start_time = now.time().replace(
                    hour=(int(start_t[:2]) + 12), minute=int(start_t[3:5]), second=0, microsecond=0)
        else:
            if start_t[5:] == 'AM':
                start_time = now.time().replace(hour=int(start_t[0]), minute=int(
                    start_t[2:4]), second=0, microsecond=0)
            else:
                start_time = now.time().replace(
                    hour=(int(start_t[0]) + 12), minute=int(start_t[2:4]), second=0, microsecond=0)
        # print(start_time[0],start_time[2:4],start_time[5:])
        # start_time = now.time().replace(hour=int(start_t[0]), minute=int(start_t[2:4]), second=0, microsecond=0)
        # print(datetime.time(int(start_time[0]),int(start_time[2:4]),0))
        print(start_time)
        l.append(start_time)
        eddate = request.POST.get('edate', '')
        edate = now.replace(hour=0, minute=0, second=0, microsecond=0, year=int(
            eddate[6:]), month=int(eddate[3:5]), day=int(eddate[:2]))
        l.append(edate)
        end_t = request.POST.get('end_time', '')
        # print("herrrrrrrrrrrrreeeeeeeeeeeeeeeeeeeeeeeeeee")
        print(len(end_t), end_t[6:], end_t[:2])

        if end_t[0] == '1' and end_t[1] != ':':
            if end_t[6:] == 'AM' and end_t[:2] != '12':
                end_time = now.time().replace(hour=int(end_t[:2]), minute=int(
                    end_t[3:5]), second=0, microsecond=0)
            elif end_t[6:] == 'AM' and end_t[:2] == '12':
                # print("herrrrrrrrrrrrreeeeeeeeeeeeeeeeeeeeeeeeeee")
                end_time = now.time().replace(hour=0, minute=int(
                    end_t[3:5]), second=0, microsecond=0)
            elif end_t[6:] == 'PM' and end_t[:2] == '12':
                end_time = now.time().replace(hour=int(end_t[:2]), minute=int(
                    end_t[3:5]), second=0, microsecond=0)
            else:
                end_time = now.time().replace(
                    hour=(int(end_t[:2]) + 12), minute=int(end_t[3:5]), second=0, microsecond=0)
        else:
            if end_t[5:] == 'AM':
                end_time = now.time().replace(hour=int(end_t[0]), minute=int(
                    end_t[2:4]), second=0, microsecond=0)
            else:
                end_time = now.time().replace(
                    hour=(int(end_t[0]) + 12), minute=int(end_t[2:4]), second=0, microsecond=0)
        print(end_time)
        l.append(end_time)
        address_line1 = request.POST.get('address_line1', '')
        l.append(address_line1)
        address_line2 = request.POST.get('address_line2', '')
        l.append(address_line2)
        city = request.POST.get('city', '')
        l.append(city)
        state = request.POST.get('state', '')
        l.append(state)
        country = request.POST.get('country', '')
        l.append(country)
        pincode = request.POST.get('pincode', '')
        l.append(int(pincode))
        latitude = request.POST.get('latitude', '')
        l.append(float(latitude))
        longitude = request.POST.get('longitude', '')
        l.append(float(longitude))
        place_id = request.POST.get('place_id', '')
        l.append(place_id)

        # for venue not started
        venue_not_decided = request.POST.get('venue_not_decided', '')
        if venue_not_decided == 'true':
            venue_not_decided = True
        else:
            venue_not_decided = False


        # ends here ~ for venue not started

        print(stdate, eddate)

        # for i in range(0,len(s)):

        #     print(l[i],s[i])

        print(l[2], str(l[2].day))
        if l[0] != s[0]:
            print("0")
            articles2.event_name = event_name
            print(l[0], s[0])
            if spea == 1:
                log = EventEditLogs(old_data=s[0], new_data=l[0], parameter=par[0], taken_action='update',
                                    event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                log.save()

        if l[1] != s[1]:
            print("1")
            articles2.website = website
            print(l[0], s[0])
            if spea == 1:
                log = EventEditLogs(old_data=s[1], new_data=l[1], parameter=par[1], taken_action='update',
                                    event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                log.save()

        if l[2] != sl:
            print("2")
            articles2.sdate = sdate
            print(l[2], sl)
            if spea == 1:
                log = EventEditLogs(old_data=sl, new_data=l[2], parameter=par[2], taken_action='update',
                                    event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                log.save()

        if l[3] != s[3]:
            print("3")
            articles2.start_time = start_time
            print(l[3], s[3])
            if spea == 1:
                log = EventEditLogs(old_data=s[3], new_data=l[3], parameter=par[3], taken_action='update',
                                    event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                log.save()

        if l[4] != el:
            print("3")
            articles2.edate = edate
            print(l[4], el)
            if spea == 1:
                log = EventEditLogs(old_data=el, new_data=l[4], parameter=par[4], taken_action='update',
                                    event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                log.save()

        if l[5] != s[5]:
            print("5")
            articles2.end_time = end_time
            print(l[5], s[5])
            if spea == 1:
                log = EventEditLogs(old_data=s[5], new_data=l[5], parameter=par[5], taken_action='update',
                                    event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                log.save()

        if l[6] != s[6]:
            print("6")
            articles2.address_line1 = l[6]
            print(l[6], s[6])
            if spea == 1:
                log = EventEditLogs(old_data=s[6], new_data=l[6], parameter=par[6], taken_action='update',
                                    event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                log.save()

        if l[7] != s[7]:
            print("7")
            articles2.address_line2 = address_line2
            print(l[7], s[7])
            if spea == 1:
                log = EventEditLogs(old_data=s[7], new_data=l[7], parameter=par[7], taken_action='update',
                                    event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                log.save()

        if l[8] != s[8]:
            print("8")
            articles2.city = city
            print(l[8], s[8])
            if spea == 1:
                log = EventEditLogs(old_data=s[8], new_data=l[8], parameter=par[8], taken_action='update',
                                    event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                log.save()

        if l[9] != s[9]:
            print("8")
            articles2.state = state
            print(l[9], s[9])
            if spea == 1:
                log = EventEditLogs(old_data=s[9], new_data=l[9], parameter=par[9], taken_action='update',
                                    event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                log.save()

        if l[10] != s[10]:
            print("10")
            articles2.country = country
            print(l[10], s[10])
            if spea == 1:
                log = EventEditLogs(old_data=s[10], new_data=l[10], parameter=par[10], taken_action='update',
                                    event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                log.save()

        if l[11] != s[11]:
            print("11")
            articles2.pincode = pincode
            print(l[11], s[11])
            if spea == 1:
                log = EventEditLogs(old_data=s[11], new_data=l[11], parameter=par[11], taken_action='update',
                                    event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                log.save()

        if l[12] != s[12]:
            print("12")
            articles2.latitude = l[12]
            print(l[12], s[12])
            if spea == 1:
                log = EventEditLogs(old_data=s[12], new_data=l[12], parameter=par[12], taken_action='update',
                                    event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                log.save()

        if l[13] != s[13]:
            print("13")
            articles2.longitude = l[13]
            print(l[13], s[13])
            if spea == 1:
                log = EventEditLogs(old_data=s[13], new_data=l[13], parameter=par[13], taken_action='update',
                                    event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                log.save()

        if l[14] != s[14]:
            print("14")
            articles2.place_id = l[14]
            print(l[14], s[14])
            if spea == 1:
                log = EventEditLogs(old_data=s[14], new_data=l[14], parameter=par[14], taken_action='update',
                                    event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                log.save()

        print(l)

        # articles2.event_name = event_name
        # articles2.sdate = sdate
        # articles2.edate = edateif venue_not_decided == 'true':
        # articles2.start_time = start_time
        # articles2.end_time = end_time
        # articles2.address_line1 = address_line1
        # articles2.address_line2 = address_line2
        # articles2.city = city
        # articles2.state = state
        # articles2.country = country
        # articles2.pincode = pincode
        # articles2.latitude = l[11]
        # articles2.longitude = l[12]
        articles2.venue_not_decided = venue_not_decided
        articles2.save()

        # l[1]=
        # l[3]=

        k_l = l[2]
        if k_l.month < 10:
            if k_l.day < 10:
                print("herrrrrrrrrrrrreeeeeeeeeeeeeeeeeeeeeeeeeee", k_l.day)
                l[2] = '0' + str(k_l.day) + '/0' + \
                    str(k_l.month) + '/' + str(k_l.year)
            else:
                l[2] = str(k_l.day) + '/0' + \
                    str(k_l.month) + '/' + str(k_l.year)
        else:
            if k_l.day < 10:
                l[2] = '0' + str(k_l.day) + '/' + \
                    str(k_l.month) + '/' + str(k_l.year)
            else:
                l[2] = str(k_l.day) + '/' + str(k_l.month) + \
                    '/' + str(k_l.year)

        k1_l = l[4]

        if k1_l.month < 10:
            if k1_l.day < 10:
                l[4] = '0' + str(k1_l.day) + '/0' + \
                    str(k1_l.month) + '/' + str(k1_l.year)
            else:
                l[4] = str(k1_l.day) + '/0' + \
                    str(k1_l.month) + '/' + str(k1_l.year)
        else:
            if k1_l.day < 10:
                l[4] = '0' + str(k1_l.day) + '/' + \
                    str(k1_l.month) + '/' + str(k1_l.year)
            else:
                l[4] = str(k1_l.day) + '/' + str(k1_l.month) + \
                    '/' + str(k1_l.year)

        print(l, s)
        print(l[2], s[2])
        print(l[4], s[4])

        return render(request, 'dashboard/edit_event.html', {'event_id': event_id, 's': l, })

    return render(request, 'dashboard/edit_event.html', {'event_id': event_id, 's': s, })


# def edit_action_one(request, event_id):

#     print(event_id)
#     now = datetime.now()
#     start = now.replace(hour=0, minute=0, second=0, microsecond=0)
#     print(type(start))
#     articles2 = Articles2.objects.get(id = event_id)
#     event_name=request.POST.get('event_name','')
#     stdate=request.POST.get('sdate','')
#     start_time=request.POST.get('start_time','')
#     eddate=request.POST.get('edate','')
#     end_time=request.POST.get('end_time','')
#     address_line1=request.POST.get('address_line1','')
#     address_line2=request.POST.get('address_line2','')
#     city=request.POST.get('city','')
#     state=request.POST.get('state','')
#     country=request.POST.get('country','')
#     pincode=request.POST.get('pincode','')
#     latitude=request.POST.get('latitude','')
#     longitude=request.POST.get('longitude','')
#     print(stdate,eddate)

#     sdate=now.replace(hour=0, minute=0, second=0, microsecond=0, year=int(stdate[6:]), month=int(stdate[3:5]), day=int(stdate[:2]))
#     edate=now.replace(hour=0, minute=0, second=0, microsecond=0, year=int(eddate[6:]), month=int(eddate[3:5]), day=int(eddate[:2]))

#     print(sdate,edate)

#     articles2.event_name = event_name
#     articles2.sdate = sdate
#     articles2.edate = edate
#     articles2.start_time = start_time
#     articles2.end_time = end_time
#     articles2.address_line1 = address_line1
#     articles2.address_line2 = address_line2
#     articles2.city = city
#     articles2.state = state
#     articles2.country = country
#     articles2.pincode = pincode
#     articles2.latitude = latitude
#     articles2.longitude = longitude

#     articles2.save()

#     # s_u=Articles2(id=event_id,event_name=event_name,start_time=start_time,end_time=end_time,address_line1=address_line1,address_line2=address_line2,city=city,state=state,country=country)
#     # print(s_u)

#     # s_u.save()

#     #sdate=sdate,start_time=start_time,edate=edate,end_time=end_time,
#     # s=[]
#     # d = Articles2.objects.all().filter(id=event_id)
#     # s.append(d.values('event_name')[0]['event_name'])
#     # s.append(d.values('sdate')[0]['sdate'])
#     # s.append(d.values('start_time')[0]['start_time'])
#     # s.append(d.values('edate')[0]['edate'])
#     # s.append(d.values('end_time')[0]['end_time'])
#     # s.append(d.values('address_line1')[0]['address_line1'])
#     # s.append(d.values('address_line2')[0]['address_line2'])
#     # s.append(d.values('city')[0]['city'])
#     # s.append(d.values('state')[0]['state'])
#     # s.append(d.values('country')[0]['country'])
#     # s.append(d.values('pincode')[0]['pincode'])


#     return HttpResponseRedirect(reverse('dashboard:edit-event-two', args=(event_id,)))

def edit_event_two(request, event_id):
    if 'userid' not in request.session.keys():
        return redirect('/live/login')

    cat = []
    cat1 = []
    a = Categories.objects.all().values('category')
    # print(a)
    for i in a:
        cat.append(i['category'])
    a1 = Categories.objects.all().values('category_id')
    # print(a1)
    for i in a1:
        cat1.append(i['category_id'])
    # print(cat1)
    c = zip(cat, cat1)
    e = CategorizedEvents.objects.all().filter(
        event_id=event_id).values('category_id')
    k = e.values('category_id')[0]['category_id']
    l = e.values('topic_id')[0]['topic_id']
    print(type(k), l)

    a2 = Topics.objects.all().filter(category=k).values('topic')
    a3 = Topics.objects.all().filter(category=k).values('topics_id')
    # print(a2,a3)
    to = []
    t_i = []
    for i in range(0, len(a2)):
        to.append(a2[i]['topic'])
        t_i.append(a3[i]['topics_id'])
    print(to, t_i)
    t = zip(to, t_i)

    f = StatusPromotionTicketing.objects.all().filter(event_id=event_id)
    pr = f.values('private')[0]['private']
    tick = f.values('ticketing')[0]['ticketing']
    print(type(pr), tick)

    # if request.method=='POST':
    #     h=request.POST.get('value','')
    #     print(h)
    #     data ={'a2':Topics.objects.all().filter(category=h)}
    #     a3=Topics.objects.all().filter(category=h).values('topics_id')

    #     # t=zip(a2,a3)

    #     return JsonResponse(data)

    return render(request, 'dashboard/edit_event_two.html', {'event_id': event_id, 'c': c, 'k': k, 't': t, 'l': l, 'pr': pr, 'tick': tick})


###############

def edit_event_two(request, event_id):
    if 'userid' not in request.session.keys():
        return redirect('/live/login')

    cat = []
    cat1 = []
    a = Categories.objects.all().values('category')
    # print(a)
    for i in a:
        cat.append(i['category'])
    a1 = Categories.objects.all().values('category_id')
    # print(a1)
    for i in a1:
        cat1.append(i['category_id'])
    # print(cat1)
    c = zip(cat, cat1)
    e = CategorizedEvents.objects.all().filter(
        event_id=event_id).values('category_id')
    k = e.values('category_id')[0]['category_id']
    l = e.values('topic_id')[0]['topic_id']
    print(type(k), l)

    a2 = Topics.objects.all().filter(category=k).values('topic')
    a3 = Topics.objects.all().filter(category=k).values('topics_id')
    # print(a2,a3)
    to = []
    t_i = []
    for i in range(0, len(a2)):
        to.append(a2[i]['topic'])
        t_i.append(a3[i]['topics_id'])
    print(to, t_i)
    t = zip(to, t_i)

    f = StatusPromotionTicketing.objects.all().filter(event_id=event_id)
    pr = f.values('private')[0]['private']
    tick = f.values('ticketing')[0]['ticketing']
    print(type(pr), tick)

    # if request.method=='POST':
    #     h=request.POST.get('value','')
    #     print(h)
    #     data ={'a2':Topics.objects.all().filter(category=h)}
    #     a3=Topics.objects.all().filter(category=h).values('topics_id')

    #     # t=zip(a2,a3)

    #     return JsonResponse(data)

    return render(request, 'dashboard/edit_event_two.html', {'event_id': event_id, 'c': c, 'k': k, 't': t, 'l': l, 'pr': pr, 'tick': tick})


def edit_action_two(request, event_id):
    if request.method == 'GET':

        cat = []
        cat1 = []
        a = Categories.objects.all().values('category')
        # print(a)
        for i in a:
            cat.append(i['category'])
        a1 = Categories.objects.all().values('category_id')
        # print(a1)
        for i in a1:
            cat1.append(i['category_id'])
        # print(cat1)
        c = zip(cat, cat1)
        e = CategorizedEvents.objects.all().filter(
            event_id=event_id).values('category_id')
        k = e.values('category_id')[0]['category_id']
        l = e.values('topic_id')[0]['topic_id']
        print(type(k), l)

        a2 = Topics.objects.all().filter(category=k).values('topic')
        a3 = Topics.objects.all().filter(category=k).values('topics_id')
        # print(a2,a3)
        to = []
        t_i = []
        for i in range(0, len(a2)):
            to.append(a2[i]['topic'])
            t_i.append(a3[i]['topics_id'])
        print(to, t_i)
        t = zip(to, t_i)

        f = StatusPromotionTicketing.objects.all().filter(event_id=event_id)
        pr = f.values('private')[0]['private']
        tick = f.values('ticketing')[0]['ticketing']
        print(type(pr), tick)

        # if request.method=='POST':
        #     h=request.POST.get('value','')
        #     print(h)
        #     data ={'a2':Topics.objects.all().filter(category=h)}
        #     a3=Topics.objects.all().filter(category=h).values('topics_id')

        #     # t=zip(a2,a3)

        #     return JsonResponse(data)

        return render(request, 'dashboard/edit_event_two.html', {'event_id': event_id, 'c': c, 'k': k, 't': t, 'l': l, 'pr': pr, 'tick': tick})
    if request.method == 'POST':
        print(event_id)
        now = datetime.now()

        # ca = CategorizedEvents.objects.all().filter(event_id=event_id)
        # sp = StatusPromotionTicketing.objects.all().filter(event_id=event_id)
        ca = CategorizedEvents.objects.get(event_id=event_id)
        sp = StatusPromotionTicketing.objects.all().filter(event_id=event_id)
        cat = []
        cat1 = []
        a = Categories.objects.all().values('category')
        # print(a)
        for i in a:
            cat.append(i['category'])
        a1 = Categories.objects.all().values('category_id')
        # print(a1)
        for i in a1:
            cat1.append(i['category_id'])
        # print(cat1)
        c = zip(cat, cat1)

        spe = StatusPromotionTicketing.objects.all().filter(
            event_id=event_id).values('approval')
        spea = spe[0]['approval']
        print(spea)
        if spea == 1:
            print("logs will be maintained")

        e = CategorizedEvents.objects.all().filter(event_id=event_id)
        k1 = e.values('category_id')[0]['category_id']
        l1 = e.values('topic_id')[0]['topic_id']

        f = StatusPromotionTicketing.objects.all().filter(event_id=event_id)
        pr = f.values('private')[0]['private']
        tick = f.values('ticketing')[0]['ticketing']
        print(type(pr), tick)

        cat_id = request.POST.get('category_id', '0')
        top_id = request.POST.get('topic_id', '0')
        pri = request.POST.get('type1', '')
        ticket = request.POST.get('type2', '')

        par = ['category_id', 'topic_id', 'private', 'ticketing']

        if pri == 'public':
            private = 0
        else:
            private = 1
        if ticket == 'paid':
            ticketing = 1
        else:
            ticketing = 0

        print(type(cat_id), top_id, type(private), ticketing)

        if int(cat_id) != k1 and int(top_id) == l1:

            print('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')

            # h=request.POST.get('category_id','0')
            # print(type(h))
            a2 = Topics.objects.all().filter(category=cat_id).values('topic')
            a3 = Topics.objects.all().filter(category=cat_id).values('topics_id')
            # print(a2,type(a3[0]['topics_id']))
            to = []
            t_i = []
            for i in range(0, len(a2)):
                to.append(a2[i]['topic'])
                t_i.append(a3[i]['topics_id'])
            print(to, t_i)
            t = zip(to, t_i)
            k = int(cat_id)

            if pr != private:
                print("private")
                sp.private = private
                if spea == 1:
                    log = EventEditLogs(old_data=pr, new_data=private, parameter=par[2], taken_action='update',
                                        event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                    log.save()

            if tick != ticketing:
                print("ticket")
                sp.ticketing = ticketing
                if spea == 1:
                    log = EventEditLogs(old_data=tick, new_data=ticketing, parameter=par[3], taken_action='update',
                                        event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')

                    log.save()
                StatusPromotionTicketing.objects.filter(event_id=event_id).update(private=private,ticketing=ticketing)
            for object in sp:
                object.save()

            pr = private
            tick = ticketing

            return render(request, 'dashboard/edit_event_two.html', {'event_id': event_id, 't': t, 'c': c, 'k': k, 'pr': pr, 'tick': tick})

        if int(cat_id) != k1 and int(top_id) != l1:
            print('BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB')
            # h=request.POST.get('category_id','0')
            # print(type(h))
            a2 = Topics.objects.all().filter(category=cat_id).values('topic')
            a3 = Topics.objects.all().filter(category=cat_id).values('topics_id')
            # print(a2,type(a3[0]['topics_id']))
            to = []
            t_i = []
            for i in range(0, len(a2)):
                to.append(a2[i]['topic'])
                t_i.append(a3[i]['topics_id'])
            print(to, t_i)
            t = zip(to, t_i)
            k = int(cat_id)
            l = int(top_id)

            for i in t_i:
                if i == int(top_id):
                    if k1 != k:
                        print("Catogory")
                        ca.category_id = cat_id
                        if spea == 1:
                            log = EventEditLogs(old_data=k1, new_data=k, parameter=par[0], taken_action='update',
                                                event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                            log.save()

                    if l1 != l:
                        print("Topic")
                        ca.topic_id = top_id
                        if spea == 1:
                            log = EventEditLogs(old_data=l1, new_data=l, parameter=par[1], taken_action='update',
                                                event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                            log.save()

                        ca.save()

                    if pr != private:
                        print("private")
                        sp.private = private
                        if spea == 1:
                            log = EventEditLogs(old_data=pr, new_data=private, parameter=par[2], taken_action='update',
                                                event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                            log.save()

                    if tick != ticketing:
                        print("ticket")
                        sp.ticketing = ticketing
                        if spea == 1:
                            log = EventEditLogs(old_data=tick, new_data=ticketing, parameter=par[3], taken_action='update',
                                                event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                            log.save()
                        StatusPromotionTicketing.objects.filter(event_id=event_id).update(private=private,ticketing=ticketing)

                    for object in sp:
                        object.save()

            pr = private
            tick = ticketing


            print('event_id', event_id, 't', t, 'c', c, 'k', k, 'l', l, 'pr', pr, 'tick', tick)

            return render(request, 'dashboard/edit_event_two.html', {'event_id': event_id, 't': t, 'c': c, 'k': k, 'l': l, 'pr': pr, 'tick': tick})

        if int(cat_id) == k1 and int(top_id) == l1:
            print('CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC')
            # h=request.POST.get('category_id','')
            # print(type(h))
            a2 = Topics.objects.all().filter(category=cat_id).values('topic')
            a3 = Topics.objects.all().filter(category=cat_id).values('topics_id')
            # print(a2,type(a3[0]['topics_id']))
            to = []
            t_i = []
            for i in range(0, len(a2)):
                to.append(a2[i]['topic'])
                t_i.append(a3[i]['topics_id'])
            print(to, t_i)
            t = zip(to, t_i)
            k = int(cat_id)
            l = int(top_id)

            if pr != private:
                print("private")
                sp.private = private
                if spea == 1:
                    log = EventEditLogs(old_data=pr, new_data=private, parameter=par[2], taken_action='update',
                                        event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                    log.save()

            if tick != ticketing:
                print("ticket")
                sp.ticketing = ticketing
                if spea == 1:
                    log = EventEditLogs(old_data=tick, new_data=ticketing, parameter=par[3], taken_action='update',
                                        event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                    log.save()
                StatusPromotionTicketing.objects.filter(event_id=event_id).update(private=private,ticketing=ticketing)

            for object in sp:
                object.save()

            pr = private
            tick = ticketing

            return render(request, 'dashboard/edit_event_two.html', {'event_id': event_id, 't': t, 'c': c, 'k': k, 'l': l, 'pr': pr, 'tick': tick})

        if int(cat_id) == k1 and int(top_id) != l1:
            print('DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD')
            # h=request.POST.get('category_id','')
            # print(type(h))
            a2 = Topics.objects.all().filter(category=cat_id).values('topic')
            a3 = Topics.objects.all().filter(category=cat_id).values('topics_id')
            # print(a2,type(a3[0]['topics_id']))
            to = []
            t_i = []
            for i in range(0, len(a2)):
                to.append(a2[i]['topic'])
                t_i.append(a3[i]['topics_id'])
            print(to, t_i)
            t = zip(to, t_i)
            k = int(cat_id)
            l = int(top_id)

            for i in t_i:
                if i == int(top_id):
                    print("topic")
                    ca.topic_id = top_id
                    ca.save()
                    if spea == 1:
                        log = EventEditLogs(old_data=l1, new_data=l, parameter=par[1], taken_action='update',
                                            event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                        log.save()
                    if pr != private:
                        print("private")
                        sp.private = private
                        if spea == 1:
                            log = EventEditLogs(old_data=pr, new_data=private, parameter=par[2], taken_action='update',
                                                event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                            log.save()

                    if tick != ticketing:
                        print("ticket")
                        sp.ticketing = ticketing
                        if spea == 1:
                            log = EventEditLogs(old_data=tick, new_data=ticketing, parameter=par[3], taken_action='update',
                                                event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                            log.save()
                        StatusPromotionTicketing.objects.filter(event_id=event_id).update(private=private,ticketing=ticketing)

                    for object in sp:
                        object.save()

            pr = private
            tick = ticketing

            return render(request, 'dashboard/edit_event_two.html', {'event_id': event_id, 't': t, 'c': c, 'k': k, 'l': l, 'pr': pr, 'tick': tick})

    return HttpResponseRedirect(reverse('dashboard:edit-event-four', args=(event_id,)))



##############


# def edit_action_two(request, event_id):

#     print(event_id)
#     now = datetime.now()

#     ca = CategorizedEvents.objects.all().filter(event_id=event_id)
#     sp = StatusPromotionTicketing.objects.all().filter(event_id=event_id)
#     cat = []
#     cat1 = []
#     a = Categories.objects.all().values('category')
#     # print(a)
#     for i in a:
#         cat.append(i['category'])
#     a1 = Categories.objects.all().values('category_id')
#     # print(a1)
#     for i in a1:
#         cat1.append(i['category_id'])
#     # print(cat1)
#     c = zip(cat, cat1)

#     spe = StatusPromotionTicketing.objects.all().filter(
#         event_id=event_id).values('approval')
#     spea = spe[0]['approval']
#     print(spea)
#     if spea == 1:
#         print("logs will be maintained")

#     e = CategorizedEvents.objects.all().filter(event_id=event_id)
#     k1 = e.values('category_id')[0]['category_id']
#     l1 = e.values('topic_id')[0]['topic_id']

#     f = StatusPromotionTicketing.objects.all().filter(event_id=event_id)
#     pr = f.values('private')[0]['private']
#     tick = f.values('ticketing')[0]['ticketing']
#     print(type(pr), tick)

#     cat_id = request.POST.get('category_id', '0')
#     top_id = request.POST.get('topic_id', '0')
#     pri = request.POST.get('type1', '')
#     ticket = request.POST.get('type2', '')

#     par = ['category_id', 'topic_id', 'private', 'ticketing']

#     if pri == 'public':
#         private = 0
#     else:
#         private = 1
#     if ticket == 'paid':
#         ticketing = 1
#     else:
#         ticketing = 0

#     print(type(cat_id), top_id, type(private), ticketing)

#     if int(cat_id) != k1 and int(top_id) == l1:
#         # h=request.POST.get('category_id','0')
#         # print(type(h))
#         a2 = Topics.objects.all().filter(category=cat_id).values('topic')
#         a3 = Topics.objects.all().filter(category=cat_id).values('topics_id')
#         # print(a2,type(a3[0]['topics_id']))
#         to = []
#         t_i = []
#         for i in range(0, len(a2)):
#             to.append(a2[i]['topic'])
#             t_i.append(a3[i]['topics_id'])
#         print(to, t_i)
#         t = zip(to, t_i)
#         k = int(cat_id)

#         if pr != private:
#             print("private")
#             sp.private = private
#             if spea == 1:
#                 log = EventEditLogs(old_data=pr, new_data=private, parameter=par[2], taken_action='update',
#                                     event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
#                 log.save()

#         if tick != ticketing:
#             print("ticket")
#             sp.ticketing = ticketing
#             if spea == 1:
#                 log = EventEditLogs(old_data=tick, new_data=ticketing, parameter=par[3], taken_action='update',
#                                     event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
#                 log.save()
#         for object in sp:
#             object.save()

#         pr = private
#         tick = ticketing

#         return render(request, 'dashboard/edit_event_two.html', {'event_id': event_id, 't': t, 'c': c, 'k': k, 'pr': pr, 'tick': tick})

#     if int(cat_id) != k1 and int(top_id) != l1:
#         # h=request.POST.get('category_id','0')
#         # print(type(h))
#         a2 = Topics.objects.all().filter(category=cat_id).values('topic')
#         a3 = Topics.objects.all().filter(category=cat_id).values('topics_id')
#         # print(a2,type(a3[0]['topics_id']))
#         to = []
#         t_i = []
#         for i in range(0, len(a2)):
#             to.append(a2[i]['topic'])
#             t_i.append(a3[i]['topics_id'])
#         print(to, t_i)
#         t = zip(to, t_i)
#         k = int(cat_id)
#         l = int(top_id)

#         for i in t_i:
#             if i == int(top_id):
#                 if k1 != k:
#                     print("Catogory")
#                     ca.category_id = cat_id
#                     if spea == 1:
#                         log = EventEditLogs(old_data=k1, new_data=k, parameter=par[0], taken_action='update',
#                                             event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
#                         log.save()

#                 if l1 != l:
#                     print("Topic")
#                     ca.topic_id = top_id
#                     if spea == 1:
#                         log = EventEditLogs(old_data=l1, new_data=l, parameter=par[1], taken_action='update',
#                                             event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
#                         log.save()

#                 ca.save()

#                 if pr != private:
#                     print("private")
#                     sp.private = private
#                     if spea == 1:
#                         log = EventEditLogs(old_data=pr, new_data=private, parameter=par[2], taken_action='update',
#                                             event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
#                         log.save()

#                 if tick != ticketing:
#                     print("ticket")
#                     sp.ticketing = ticketing
#                     if spea == 1:
#                         log = EventEditLogs(old_data=tick, new_data=ticketing, parameter=par[3], taken_action='update',
#                                             event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
#                         log.save()

#                 for object in sp:
#                     object.save()

#         pr = private
#         tick = ticketing

#         return render(request, 'dashboard/edit_event_two.html', {'event_id': event_id, 't': t, 'c': c, 'k': k, 'l': l, 'pr': pr, 'tick': tick})

#     if int(cat_id) == k1 and int(top_id) == l1:
#         # h=request.POST.get('category_id','')
#         # print(type(h))
#         a2 = Topics.objects.all().filter(category=cat_id).values('topic')
#         a3 = Topics.objects.all().filter(category=cat_id).values('topics_id')
#         # print(a2,type(a3[0]['topics_id']))
#         to = []
#         t_i = []
#         for i in range(0, len(a2)):
#             to.append(a2[i]['topic'])
#             t_i.append(a3[i]['topics_id'])
#         print(to, t_i)
#         t = zip(to, t_i)
#         k = int(cat_id)
#         l = int(top_id)

#         if pr != private:
#             print("private")
#             sp.private = private
#             if spea == 1:
#                 log = EventEditLogs(old_data=pr, new_data=private, parameter=par[2], taken_action='update',
#                                     event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
#                 log.save()

#         if tick != ticketing:
#             print("ticket")
#             sp.ticketing = ticketing
#             if spea == 1:
#                 log = EventEditLogs(old_data=tick, new_data=ticketing, parameter=par[3], taken_action='update',
#                                     event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
#                 log.save()

#         for object in sp:
#             object.save()

#         pr = private
#         tick = ticketing

#         return render(request, 'dashboard/edit_event_two.html', {'event_id': event_id, 't': t, 'c': c, 'k': k, 'l': l, 'pr': pr, 'tick': tick})

#     if int(cat_id) == k1 and int(top_id) != l1:
#         # h=request.POST.get('category_id','')
#         # print(type(h))
#         a2 = Topics.objects.all().filter(category=cat_id).values('topic')
#         a3 = Topics.objects.all().filter(category=cat_id).values('topics_id')
#         # print(a2,type(a3[0]['topics_id']))
#         to = []
#         t_i = []
#         for i in range(0, len(a2)):
#             to.append(a2[i]['topic'])
#             t_i.append(a3[i]['topics_id'])
#         print(to, t_i)
#         t = zip(to, t_i)
#         k = int(cat_id)
#         l = int(top_id)

#         for i in t_i:
#             if i == int(top_id):
#                 print("topic")
#                 ca.topic_id = top_id
#                 ca.save()
#                 if spea == 1:
#                     log = EventEditLogs(old_data=l1, new_data=l, parameter=par[1], taken_action='update',
#                                         event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
#                     log.save()
#                 if pr != private:
#                     print("private")
#                     sp.private = private
#                     if spea == 1:
#                         log = EventEditLogs(old_data=pr, new_data=private, parameter=par[2], taken_action='update',
#                                             event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
#                         log.save()

#                 if tick != ticketing:
#                     print("ticket")
#                     sp.ticketing = ticketing
#                     if spea == 1:
#                         log = EventEditLogs(old_data=tick, new_data=ticketing, parameter=par[3], taken_action='update',
#                                             event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
#                         log.save()

#                 for object in sp:
#                     object.save()

#         pr = private
#         tick = ticketing

#         return render(request, 'dashboard/edit_event_two.html', {'event_id': event_id, 't': t, 'c': c, 'k': k, 'l': l, 'pr': pr, 'tick': tick})

#     return HttpResponseRedirect(reverse('dashboard:edit-event-four', args=(event_id,)))


# def edit_event_three(request, event_id):
#     if 'userid' not in request.session.keys():
#         return redirect('/live/login')

#     return render(request, 'dashboard/edit_event_four.html', {'event_id': event_id, })


def edit_event_four(request, event_id):
    if 'userid' not in request.session.keys():
        return redirect('/live/login')
    now = datetime.now()
    descform = Articles2Form()

    # print('descform > ', descform)

    a = Articles2.objects.all().filter(id=event_id).values('description')
    d = a[0]['description']
    d = d[3:]
    d = d[:-4]
    # d = unescape(d)
    # print(d)
    inst = get_object_or_404(Articles2, id=event_id)
    # print(inst.country)
    qs_india = get_object_or_404(AboutCountries, country="India")
    # print(qs_india.bank_regex1)
    # print(qs_india.bank_regex2)
    bank_regex1 = qs_india.bank_regex1
    bank_regex2 = qs_india.bank_regex2
    # print(type(bank_regex1), type(bank_regex2))

    spe = StatusPromotionTicketing.objects.all().filter(
        event_id=event_id).values('approval')
    # print(spe)
    spea = spe[0]['approval']
    # print(spea)
    if spea == 1:
        print("logs will be maintained")

    if request.method == 'POST':
        descform = Articles2Form(
            request.POST, instance=get_object_or_404(Articles2, id=event_id))

        # print('descform',descform.is_valid())
        # print('=======')

        if not descform.is_valid():
            return render(request, 'dashboard/edit_event_four.html', {'descform': descform, 'flag': True})
        d1 = unescape(descform.cleaned_data.get('description'))
        # print(d1)
        d1 = d1[3:]
        d1 = d1[:-4]
        print(d1)
        if spea == 1:
            log = EventEditLogs(old_data=d, new_data=d1, parameter="description", taken_action='update',
                                event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
            log.save()
        descform.save()
        # h=request.POST.get('b1','')
        # print(h)


        return render(request, 'dashboard/edit_event_four.html', {'event_id': event_id, 'descform': descform, 'd': d1, 'bank_regex1': bank_regex1, 'bank_regex2': bank_regex2})

    # @author Shubham
    # d = d.replace('\n','<br/>')
    # d = '/p>'
    d = d.replace("\n","")
    d = d.replace(" ", "")
    # d = '&nbsp;ashdkahkdhkasd</p> kashdjahdj'
    # ends here ~ @author Shubham
    return render(request, 'dashboard/edit_event_four.html', {'event_id': event_id, 'descform': descform, 'd': d, 'bank_regex1': bank_regex1, 'bank_regex2': bank_regex2})


def edit_event_five(request, event_id, ticket_id):
    if 'userid' not in request.session.keys():
        return redirect('/live/login')
    now = datetime.now()
    inst = get_object_or_404(Articles2, id=event_id)
    # date11 = inst.sdate.strftime('%m/%d/%Y')
    # sdate11 = inst.sdate.strftime('%d/%m/%Y')

    date = inst.sdate.strftime('%m/%d/%Y')
    sdate = inst.sdate.strftime('%d/%m/%Y')
    edate = inst.edate.strftime('%d/%m/%Y')
    eventStartTime = inst.start_time.strftime('%H:%M')
    eventEndTime = inst.end_time.strftime('%H:%M')

    spe = StatusPromotionTicketing.objects.all().filter(
        event_id=event_id).values('approval')
    spea = spe[0]['approval']
    print(spea)
    if spea == 1:
        print("logs will be maintained")

    print(event_id)
    print(ticket_id)

    allTicketsDetailFilter = Tickets.objects.all().filter(event_id=event_id)
    names = []
    for i in range(0,len(allTicketsDetailFilter)):
        names.append(allTicketsDetailFilter.values('ticket_name')[i]['ticket_name'])
    ticketnames = json.dumps(names)

    d = Tickets.objects.all().filter(tickets_id=ticket_id)
    print(d)
    s = []
    s.append(d.values('ticket_name')[0]['ticket_name'])

    s.append(d.values('ticket_price')[0]['ticket_price'])
    s.append(d.values('other_charges')[0]['other_charges'])
    s.append(d.values('other_charges_type')[0]['other_charges_type'])
    s.append(d.values('ticket_qty')[0]['ticket_qty'])
    s.append(d.values('min_qty')[0]['min_qty'])
    s.append(d.values('max_qty')[0]['max_qty'])
    k = d.values('ticket_start_date')[0]['ticket_start_date']
    sl = now.replace(hour=k.hour, minute=k.minute, second=k.second,
                     microsecond=k.microsecond, year=k.year, month=k.month, day=k.day)
    # sd=datetime.date(k)
    print(sl)
    if k.month < 10:
        if k.day < 10:
            sda = '0' + str(k.day) + '/0' + str(k.month) + '/' + str(k.year)
        else:
            sda = str(k.day) + '/0' + str(k.month) + '/' + str(k.year)
    else:
        if k.day < 10:
            sda = '0' + str(k.day) + '/' + str(k.month) + '/' + str(k.year)
        else:
            sda = str(k.day) + '/' + str(k.month) + '/' + str(k.year)
    s.append(sda)
    print(sda)
    q = datetime.time(k)
    s.append(q)
    # s.append(d.values('start_time')[0]['start_time'])
    k1 = d.values('expiry_date')[0]['expiry_date']
    el = now.replace(hour=k1.hour, minute=k1.minute, second=k1.second,
                     microsecond=k1.microsecond, year=k1.year, month=k1.month, day=k1.day)

    # ed=datetime.date(k1)
    # print(ed)
    if k1.month < 10:
        if k1.day < 10:
            eda = '0' + str(k1.day) + '/0' + str(k1.month) + '/' + str(k1.year)
        else:
            eda = str(k1.day) + '/0' + str(k1.month) + '/' + str(k1.year)
    else:
        if k1.day < 10:
            eda = '0' + str(k1.day) + '/' + str(k1.month) + '/' + str(k1.year)
        else:
            eda = str(k1.day) + '/' + str(k1.month) + '/' + str(k1.year)
    s.append(eda)
    print(eda)
    r = datetime.time(k1)
    s.append(r)
    print(r)
    msg = d.values('ticket_msg')[0]['ticket_msg']
    if msg == "None" or msg == "NULL" or msg == "" or msg == None:
        msg = "1"
    s.append(msg)
    s.append(d.values('ticket_label')[0]['ticket_label'])

    print(s)

    if request.method == 'POST':
        print(event_id)
        now = datetime.now()
        # a=Tickets.objects.all().filter(event_id=event_id).values('tickets_id')
        # t_id=a[0]['tickets_id']
        # print(t_id)
        l = []
        t = Tickets.objects.get(tickets_id=ticket_id)
        ticket_name = request.POST.get('ticket_name', '')
        l.append(ticket_name)
        ticket_price = request.POST.get('ticket_price', '')
        l.append(ticket_price)
        other_charges = request.POST.get('other_charges', '')
        l.append(other_charges)
        other_charges_type = request.POST.get('other_charges_type', '')
        l.append(int(other_charges_type))
        ticket_qty = request.POST.get('ticket_qty', '')
        l.append(int(ticket_qty))
        min_qty = request.POST.get('min_qty', '')
        l.append(int(min_qty))
        max_qty = request.POST.get('max_qty', '')
        l.append(int(max_qty))

        tsd = request.POST.get('start_date')
        start_t = request.POST.get('start_time_step5')

        if start_t[0] == '1' and start_t[1] != ':':
            if start_t[6:] == 'AM' and start_t[:2] != '12':
                start_time = now.time().replace(hour=int(start_t[:2]), minute=int(
                    start_t[3:5]), second=0, microsecond=0)
            elif start_t[6:] == 'AM' and start_t[:2] == '12':
                # print("herrrrrrrrrrrrreeeeeeeeeeeeeeeeeeeeeeeeeee")
                start_time = now.time().replace(hour=0, minute=int(
                    start_t[3:5]), second=0, microsecond=0)
            elif start_t[6:] == 'PM' and start_t[:2] == '12':
                start_time = now.time().replace(hour=int(start_t[:2]), minute=int(
                    start_t[3:5]), second=0, microsecond=0)
            else:
                start_time = now.time().replace(
                    hour=(int(start_t[:2]) + 12), minute=int(start_t[3:5]), second=0, microsecond=0)
        else:
            if start_t[5:] == 'AM':
                start_time = now.time().replace(hour=int(start_t[0]), minute=int(
                    start_t[2:4]), second=0, microsecond=0)
            else:
                start_time = now.time().replace(
                    hour=(int(start_t[0]) + 12), minute=int(start_t[2:4]), second=0, microsecond=0)

        st = str(start_time)
        sd = request.POST.get('end_date')
        end_t = request.POST.get('end_time_step5')

        if end_t[0] == '1' and end_t[1] != ':':
            if end_t[6:] == 'AM' and end_t[:2] != '12':
                end_time = now.time().replace(hour=int(end_t[:2]), minute=int(
                    end_t[3:5]), second=0, microsecond=0)
            elif end_t[6:] == 'AM' and end_t[:2] == '12':
                # print("herrrrrrrrrrrrreeeeeeeeeeeeeeeeeeeeeeeeeee")
                end_time = now.time().replace(hour=0, minute=int(
                    end_t[3:5]), second=0, microsecond=0)
            elif end_t[6:] == 'PM' and end_t[:2] == '12':
                end_time = now.time().replace(hour=int(end_t[:2]), minute=int(
                    end_t[3:5]), second=0, microsecond=0)
            else:
                end_time = now.time().replace(
                    hour=(int(end_t[:2]) + 12), minute=int(end_t[3:5]), second=0, microsecond=0)
        else:
            if end_t[5:] == 'AM':
                end_time = now.time().replace(hour=int(end_t[0]), minute=int(
                    end_t[2:4]), second=0, microsecond=0)
            else:
                end_time = now.time().replace(
                    hour=(int(end_t[0]) + 12), minute=int(end_t[2:4]), second=0, microsecond=0)

        o = str(end_time)
        print(tsd + st)
        print(type(l), st)
        ticket_start_date = tsd + " " + st
        ticket_start_date = datetime.strptime(
            ticket_start_date, '%d/%m/%Y %H:%M:%S')
        l.append(ticket_start_date)
        expiry_date = sd + " " + o
        expiry_date = datetime.strptime(expiry_date, '%d/%m/%Y %H:%M:%S')
        l.append(expiry_date)
        print(ticket_start_date, expiry_date)

        ticket_msg = request.POST.get('ticket_msg', '')
        l.append(ticket_msg)
        ticket_label = request.POST.get('ticket_label', '')
        l.append(ticket_label)
        print(l)
        par = ['ticket_name', 'ticket_price', 'other_charges', 'other_charges_type', 'ticket_qty',
               'min_qty', 'max_qty', 'ticket_start_date', 'expiry_date', 'ticket_msg', 'ticket_label']

        for i in range(0, len(l) - 4):
            print(l[i], s[i])

        if l[0] != s[0]:
            print("0")
            t.ticket_name = ticket_name
            print(par[0], l[0], s[0])
            if spea == 1:
                log = EventEditLogs(old_data=s[0], new_data=l[0], parameter=par[0], taken_action='update',
                                    event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                log.save()

        if l[1] != s[1]:
            print("1")
            t.ticket_price = ticket_price
            print(par[1], l[1], s[1])
            if spea == 1:
                log = EventEditLogs(old_data=s[1], new_data=l[1], parameter=par[1], taken_action='update',
                                    event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                log.save()

        if l[2] != s[2]:
            print("2")
            t.other_charges = other_charges
            print(par[2], l[2], s[2])
            if spea == 1:
                log = EventEditLogs(old_data=s[2], new_data=l[2], parameter=par[2], taken_action='update',
                                    event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                log.save()

        if l[3] != s[3]:
            print("3")
            t.other_charges_type = other_charges_type
            print(par[3], l[3], s[3])
            if spea == 1:
                log = EventEditLogs(old_data=s[3], new_data=l[3], parameter=par[3], taken_action='update',
                                    event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                log.save()

        if l[4] != s[4]:
            print("4")
            t.ticket_qty = ticket_qty
            print(par[4], l[4], s[4])
            if spea == 1:
                log = EventEditLogs(old_data=s[4], new_data=l[4], parameter=par[4], taken_action='update',
                                    event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                log.save()

        if l[5] != s[5]:
            print("5")
            t.min_qty = min_qty
            print(par[5], l[5], s[5])
            if spea == 1:
                log = EventEditLogs(old_data=s[5], new_data=l[5], parameter=par[5], taken_action='update',
                                    event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                log.save()

        if l[6] != s[6]:
            print("6")
            t.max_qty = max_qty
            print(par[6], l[6], s[6])
            if spea == 1:
                log = EventEditLogs(old_data=s[6], new_data=l[6], parameter=par[6], taken_action='update',
                                    event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                log.save()

        if l[7] != sl:
            print("7")
            t.ticket_start_date = ticket_start_date
            print(par[7], l[7], sl)
            if spea == 1:
                log = EventEditLogs(old_data=sl, new_data=l[7], parameter=par[7], taken_action='update',
                                    event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                log.save()

        if l[8] != el:
            print("8")
            t.expiry_date = expiry_date
            print(par[8], l[8], el)
            if spea == 1:
                log = EventEditLogs(old_data=el, new_data=l[8], parameter=par[8], taken_action='update',
                                    event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                log.save()

        if l[9] != s[11]:
            print("9")
            t.ticket_msg = ticket_msg
            print(par[9], l[9], s[11])
            if spea == 1:
                log = EventEditLogs(old_data=s[11], new_data=l[9], parameter=par[9], taken_action='update',
                                    event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                log.save()

        if l[10] != s[12]:
            print("10")
            t.ticket_label = ticket_label
            print(par[10], l[10], s[12])
            if spea == 1:
                log = EventEditLogs(old_data=s[12], new_data=l[10], parameter=par[10], taken_action='update',
                                    event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                log.save()

        print(l, s)

        t.save()

        return HttpResponseRedirect(reverse('dashboard:edit-event-ticket', args=(event_id,)))
    return render(request, 'dashboard/edit_event_five.html', {'event_id': event_id, 'ticket_id': ticket_id, 'event_start_date':date, 'sdate':sdate, 'edate':edate,'event_start_time':eventStartTime,'event_end_time':eventEndTime, 's': s, 'ticketnames':ticketnames})


def edit_action_three(request, event_id):

    print(event_id)

    return HttpResponseRedirect(reverse('dashboard:edit-event-four', args=(event_id,)))


def delete_ticket(request, md5, event_id, ticket_id, return_page):

    t = Tickets.objects.get(tickets_id=ticket_id)
    t.delete()

    if return_page == 0:
        return HttpResponseRedirect(reverse('dashboard:step_five', args=(md5,event_id)))
    elif return_page == 1:
        return HttpResponseRedirect(reverse('dashboard:edit-event-ticket', args=(event_id,)))


def edit_event_ticket(request, event_id):

    print(event_id)
    id = []
    name = []
    price = []
    currency = []
    eventStartDate = []
    eventStart_date = ''

    country = Articles2.objects.all().filter(id=event_id).values('country')
    country = country[0]['country']
    print(country)
    currency = AboutCountries.objects.all().filter(
        country=country).values('currency')
    print(currency)
    currency = currency[0]['currency']
    print(currency)
    tick = Tickets.objects.all().filter(event_id=event_id)
    print('tick')
    print(list(tick))

    # tkts = Tickets.objects.all().filter(event_id = event_id)
    # print(tkts)
    # tkt_name = []
    # tkt_price = []
    # oth_chrgs = []
    # oth_chrgs_type =[]
    # tkt_qty = []
    # min_qty = []
    # max_qty = []
    # tkt_left = []
    # tkt_msg = []
    # s_date = []
    # e_date = []
    # e_fee = []
    # trans_fee = []
    # tkt_lbl = []
    # activ = []

    # for i in tkts:
    #     tkt_name.append(i.ticket_name)
    #     tkt_price.append(i.ticket_price)
    #     oth_chrgs.append(i.other_charges)
    #     oth_chrgs_type.append(i.other_charges_type)
    #     tkt_qty.append(i.ticket_qty)
    #     min_qty.append(i.min_qty)
    #     max_qty.append(i.max_qty)
    #     tkt_left.append(i.qty_left)
    #     tkt_msg.append(i.ticket_msg)
    #     s_date.append(i.ticket_start_date)
    #     e_date.append(i.expiry_date)
    #     e_fee.append(i.ercess_fee)
    #     trans_fee.append(i.transaction_fee)
    #     tkt_lbl.append(i.ticket_label)
    #     activ.append(i.active)
    # print("message-------------")
    # print(len(tkt_name), len(tkt_price), len(oth_chrgs),
    #                 len(oth_chrgs_type), len(tkt_qty), len(min_qty),
    #                 len(max_qty), len(tkt_left),len(tkt_msg), len(s_date), len(e_date),
    #                 len(e_fee), len(trans_fee), len(tkt_lbl), len(activ))
    # print(oth_chrgs)
    # print("message-------------")
    for i in range(0, len(tick)):
        print(i)
        id.append(tick.values('tickets_id')[i]['tickets_id'])
        name.append(tick.values('ticket_name')[i]['ticket_name'])
        price.append(tick.values('ticket_price')[i]['ticket_price'])

    eventStart_date = Articles2.objects.all().filter(id=event_id).values('sdate')
    eventStart_date = eventStart_date[0]['sdate']
    ticks = zip(id, name, price)

    return render(request, 'dashboard/edit_event_ticket.html', {'event_id': event_id, 'currency': currency, 'ticks': ticks, 'eventStart_date':eventStart_date })


def new_ticket(request, event_id):
    print('---------------------------------------','userid' not in request.session.keys(),request.session)
    if 'userid' not in request.session.keys():
        return redirect('/live/login')
    event_id = event_id
    print("len(tick)")
    inst = get_object_or_404(Articles2, id=event_id)
    # date11 = inst.sdate.strftime('%m/%d/%Y')
    # sdate11 = inst.sdate.strftime('%d/%m/%Y')

    date = inst.sdate.strftime('%m/%d/%Y')
    sdate = inst.sdate.strftime('%d/%m/%Y')
    edate = inst.edate.strftime('%d/%m/%Y')
    eventStartTime = inst.start_time.strftime('%H:%M')
    eventEndTime = inst.end_time.strftime('%H:%M')

    aboutcountries = AboutCountries.objects.all()
    now = datetime.now()

    if request.method == 'POST':
        print(event_id)
        now = datetime.now()
        # a=Tickets.objects.all().filter(event_id=event_id).values('tickets_id')
        # t_id=a[0]['tickets_id']
        # print(t_id)
        l = []
        # t= Tickets.objects.get(tickets_id = ticket_id)
        ticket_name = request.POST.get('ticket_name', '')
        l.append(ticket_name)
        ticket_price = request.POST.get('ticket_price', '')
        l.append(ticket_price)
        other_charges = request.POST.get('other_charges', '')
        l.append(other_charges)
        other_charges_type = request.POST.get('other_charges_type', '')
        l.append(int(other_charges_type))
        ticket_qty = request.POST.get('ticket_qty', '')
        l.append(int(ticket_qty))
        min_qty = request.POST.get('min_qty', '')
        l.append(int(min_qty))
        max_qty = request.POST.get('max_qty', '')
        l.append(int(max_qty))

        tsd = request.POST.get('start_date')
        start_t = request.POST.get('start_time_step5')


        if start_t[0] == '1' and start_t[1] != ':':
            if start_t[6:] == 'AM' and start_t[:2] != '12':
                start_time = now.time().replace(hour=int(start_t[:2]), minute=int(
                    start_t[3:5]), second=0, microsecond=0)
            elif start_t[6:] == 'AM' and start_t[:2] == '12':
                # print("herrrrrrrrrrrrreeeeeeeeeeeeeeeeeeeeeeeeeee")
                start_time = now.time().replace(hour=0, minute=int(
                    start_t[3:5]), second=0, microsecond=0)
            elif start_t[6:] == 'PM' and start_t[:2] == '12':
                start_time = now.time().replace(hour=int(start_t[:2]), minute=int(
                    start_t[3:5]), second=0, microsecond=0)
            else:
                start_time = now.time().replace(
                    hour=(int(start_t[:2]) + 12), minute=int(start_t[3:5]), second=0, microsecond=0)
        else:
            if start_t[5:] == 'AM':
                start_time = now.time().replace(hour=int(start_t[0]), minute=int(
                    start_t[2:4]), second=0, microsecond=0)
            else:
                start_time = now.time().replace(
                    hour=(int(start_t[0]) + 12), minute=int(start_t[2:4]), second=0, microsecond=0)

        st = str(start_time)
        sd = request.POST.get('end_date')
        end_t = request.POST.get('end_time_step5')


        if end_t[0] == '1' and end_t[1] != ':':
            if end_t[6:] == 'AM' and end_t[:2] != '12':
                end_time = now.time().replace(hour=int(end_t[:2]), minute=int(
                    end_t[3:5]), second=0, microsecond=0)
            elif end_t[6:] == 'AM' and end_t[:2] == '12':
                # print("herrrrrrrrrrrrreeeeeeeeeeeeeeeeeeeeeeeeeee")
                end_time = now.time().replace(hour=0, minute=int(
                    end_t[3:5]), second=0, microsecond=0)
            elif end_t[6:] == 'PM' and end_t[:2] == '12':
                end_time = now.time().replace(hour=int(end_t[:2]), minute=int(
                    end_t[3:5]), second=0, microsecond=0)
            else:
                end_time = now.time().replace(
                    hour=(int(end_t[:2]) + 12), minute=int(end_t[3:5]), second=0, microsecond=0)
        else:
            if end_t[5:] == 'AM':
                end_time = now.time().replace(hour=int(end_t[0]), minute=int(
                    end_t[2:4]), second=0, microsecond=0)
            else:
                end_time = now.time().replace(
                    hour=(int(end_t[0]) + 12), minute=int(end_t[2:4]), second=0, microsecond=0)

        o = str(end_time)
        print(o)
        print(tsd + st)
        print (end_t)

        print(type(l), st)
        ticket_start_date = tsd + " " + st
        ticket_start_date = datetime.strptime(
            ticket_start_date, '%d/%m/%Y %H:%M:%S')
        l.append(ticket_start_date)
        expiry_date = sd + " " + o
        expiry_date = datetime.strptime(expiry_date, '%d/%m/%Y %H:%M:%S')
        l.append(expiry_date)
        print(ticket_start_date, expiry_date)
        print(' l >> ',l)

        ticket_msg = request.POST.get('ticket_msg', '')
        l.append(ticket_msg)
        ticket_label = request.POST.get('ticket_label', '')
        l.append(ticket_label)
        print(l)
        tk = Tickets(event_id=event_id, ticket_name=l[0], ticket_price=l[1], other_charges=l[2], other_charges_type=l[3], ticket_qty=l[4], min_qty=l[5],
                     max_qty=l[6], qty_left=l[4], ticket_msg=l[9], ticket_start_date=l[7], expiry_date=l[8], ercess_fee=1, transaction_fee=1, ticket_label=l[10], active=1)
        tk.save()

        return HttpResponseRedirect(reverse('dashboard:edit-event-ticket', args=(event_id,)))

    return render(request, 'dashboard/new_ticket.html', {'event_id': event_id, 'a': aboutcountries,'event_start_date':date, 'sdate':sdate, 'edate':edate,'event_start_time':eventStartTime,'event_end_time':eventEndTime })


def edit_action_five(request, event_id, ticket_id):

    # print(event_id)
    # now = datetime.now()
    # # a=Tickets.objects.all().filter(event_id=event_id).values('tickets_id')
    # # t_id=a[0]['tickets_id']
    # # print(t_id)
    # t= Tickets.objects.get(tickets_id = ticket_id)
    # ticket_name=request.POST.get('ticket_name','')

    # tsd = request.POST.get('start_date')
    # start_t = request.POST.get('start_time_step5')

    # if start_t[0] == '1' and start_t[1] != ':':
    #     if start_t[6:] == 'AM' and start_t[:2] != '12':
    #         start_time = now.time().replace(hour=int(start_t[:2]), minute=int(start_t[3:5]), second=0, microsecond=0)
    #     elif start_t[6:] == 'AM' and start_t[:2] == '12':
    #         # print("herrrrrrrrrrrrreeeeeeeeeeeeeeeeeeeeeeeeeee")
    #         start_time = now.time().replace(hour=0, minute=int(start_t[3:5]), second=0, microsecond=0)
    #     elif start_t[6:] == 'PM' and start_t[:2] == '12':
    #         start_time = now.time().replace(hour=int(start_t[:2]), minute=int(start_t[3:5]), second=0, microsecond=0)
    #     else:
    #         start_time = now.time().replace(hour=(int(start_t[:2]) + 12), minute=int(start_t[3:5]), second=0, microsecond=0)
    # else:
    #     if start_t[5:] == 'AM':
    #         start_time = now.time().replace(hour=int(start_t[0]), minute=int(start_t[2:4]), second=0, microsecond=0)
    #     else:
    #         start_time = now.time().replace(hour=(int(start_t[0]) + 12), minute=int(start_t[2:4]), second=0, microsecond=0)

    # l=str(start_time)
    # sd = request.POST.get('end_date')
    # end_t = request.POST.get('end_time_step5')

    # if end_t[0] == '1' and end_t[1] != ':':
    #     if end_t[6:] == 'AM' and end_t[:2] != '12':
    #         end_time = now.time().replace(hour=int(end_t[:2]), minute=int(end_t[3:5]), second=0, microsecond=0)
    #     elif end_t[6:] == 'AM' and end_t[:2] == '12':
    #         # print("herrrrrrrrrrrrreeeeeeeeeeeeeeeeeeeeeeeeeee")
    #         end_time = now.time().replace(hour=0, minute=int(end_t[3:5]), second=0, microsecond=0)
    #     elif end_t[6:] == 'PM' and end_t[:2] == '12':
    #         end_time = now.time().replace(hour=int(end_t[:2]), minute=int(end_t[3:5]), second=0, microsecond=0)
    #     else:
    #         end_time = now.time().replace(hour=(int(end_t[:2]) + 12), minute=int(end_t[3:5]), second=0, microsecond=0)
    # else:
    #     if end_t[5:] == 'AM':
    #         end_time = now.time().replace(hour=int(end_t[0]), minute=int(end_t[2:4]), second=0, microsecond=0)
    #     else:
    #         end_time = now.time().replace(hour=(int(end_t[0]) + 12), minute=int(end_t[2:4]), second=0, microsecond=0)

    # o=str(end_time)
    # print(tsd + l )
    # print(type(l),l)
    # ticket_start_date = tsd +" "+ l
    # ticket_start_date = datetime.strptime(ticket_start_date, '%d/%m/%Y %H:%M:%S')
    # expiry_date= sd +" "+ o
    # expiry_date= datetime.strptime(expiry_date, '%d/%m/%Y %H:%M:%S')
    # print(ticket_start_date,expiry_date)

    # ticket_price=request.POST.get('ticket_price','')
    # other_charges=request.POST.get('other_charges','')
    # other_charges_type=request.POST.get('other_charges_type','')
    # ticket_qty=request.POST.get('ticket_qty','')
    # min_qty=request.POST.get('min_qty','')
    # max_qty=request.POST.get('max_qty','')
    # ticket_msg=request.POST.get('ticket_msg','')
    # ticket_label=request.POST.get('ticket_label','')
    # print(ticket_label)

    # t.ticket_name = ticket_name
    # t.ticket_start_date = ticket_start_date
    # t.expiry_date = expiry_date
    # t.ticket_price = ticket_price
    # t.other_charges = other_charges
    # t.other_charges_type = other_charges_type
    # t.ticket_qty = ticket_qty
    # t.min_qty = min_qty
    # t.max_qty = max_qty
    # t.ticket_msg = ticket_msg
    # t.ticket_label = ticket_label
    # t.save()

    return HttpResponseRedirect(reverse('dashboard:edit-event-five', args=(event_id, ticket_id)))


def edit_action_four(request, event_id):

    print(event_id)

    return HttpResponseRedirect(reverse('dashboard:edit-event-four', args=(event_id,)))


def step_three(request, md5, event_id):
    if 'userid' not in request.session.keys():
        return redirect('/live/login')

    logging.debug('Just above Post method code')

    if request.method == 'POST':
        logging.debug('Post method is working')
        logging.debug('{} {}'.format(event_id, md5))

        articles2 = Articles2.objects.get(id=event_id)
        logging.debug('getting access to db')
        event_name = re.sub('[^A-Za-z0-9 ]+', '', articles2.event_name)
        event_name = event_name.replace(' ', '-')
        image_name = event_name + '-' + str(event_id)
        print(image_name)
        uploadedfileurl = ''

        if request.method == 'POST' and request.FILES.get('myfile', None):
            logging.debug('Inside banner image code')
            myfile = request.FILES['myfile']
            logging.debug('{}'.format(myfile))
            logging.debug(myfile.name.split('.'))
            image_name_banner = image_name + '-' + \
                'banner' + '.' + myfile.name.split('.')[-1]
            logging.debug(
                'banner image name will be saved as: {}'.format(image_name_banner))
            # logging.debug(image_name_banner)
            myfile.name = image_name_banner
            x_s = request.POST.get('x', '')
            y_s = request.POST.get('y', '')
            w_s = request.POST.get('width', '')
            h_s = request.POST.get('height', '')

            print('x_s > ',x_s)
            print('y_s > ',y_s)
            print('w_s > ',w_s)
            print('h_s > ',h_s)

            # return False

            if(x_s == None or x_s == ''):
                x = 0
                y = 0
            else:
                x = float(x_s)
                y = float(y_s)
            w = float(w_s)
            h = float(h_s)
            print(myfile.name)
            image = Image.open(myfile)
            cropped_image = image.crop((x, y, w + x, h + y))
            resized_image = cropped_image.resize((1600, 900), Image.ANTIALIAS)

            fs = FileSystemStorage(location='media')
            # logging.debug('File system storage data: {}'.format(fs))
            # # logging.debug(fs)
            # fs.save(myfile.name,resized_image)
            resized_image.name = myfile.name
            BASE_DIR = os.path.dirname(
                os.path.dirname(os.path.abspath(__file__)))
            MEDIA_DIR = os.path.join(BASE_DIR, 'media')
            print(MEDIA_DIR)
            resized_image.save(MEDIA_DIR + "/" + resized_image.name, format='PNG')
            filename = resized_image.name
            logging.debug('final name: {}'.format(filename))
            # logging.debug(filename)
            uploadedfileurl = fs.url(filename)
            u_banner = uploadedfileurl
        # logging.debug(u_banner)
        logging.debug('Saved url in db: {}'.format(u_banner))

        myfile1 = request.POST.get('myfile1', None)

        print(myfile1)
        uploadedfileurl_1 = ''
        u_p = ''
        if request.method == 'POST' and request.FILES.get('myfile1', None):
            myfile1 = request.FILES['myfile1']
            image_name_thumb = image_name + '-' + \
                'thumbnail' + '.' + myfile1.name.split('.')[-1]
            print(image_name_thumb)
            myfile1.name = image_name_thumb
            fs_1 = FileSystemStorage(location='media')
            filename_1 = fs_1.save(myfile1.name, myfile1)
            uploadedfileurl_1 = fs_1.url(filename_1)
            u_p = uploadedfileurl_1

        myfile2 = request.POST.get('myfile2', None)

        print(myfile2)
        uploadedfileurl_2 = ''
        u_editables = ''
        if request.method == 'POST' and request.FILES.get('myfile2', None):
            myfile2 = request.FILES['myfile2']
            editable_name = image_name + '-' + 'editable' + \
                '.' + myfile2.name.split('.')[-1]
            print(editable_name)
            myfile2.name = editable_name
            fs_2 = FileSystemStorage(location='media/editables')
            filename2 = fs_2.save(myfile2.name, myfile2)
            uploadedfileurl_2 = fs_2.url(filename2)
            u_editables = uploadedfileurl_2

        u_editables = uploadedfileurl_2.replace("/media/", "/media/editables/")
        articles2.banner = u_banner
        articles2.profile_image = u_p
        articles2.editable_image = u_editables
        # s=Articles2(id=event_id,banner=u_banner,profile_image=u_p,editable_image=u_editables)

        # print(s)
        articles2.save()

        # return render(request, 'dashboard/create-event/step_3/step_three_temp.html',{'event_id':event_id, 'md5':md5,})
        # return redirect('/live/dashboard/add-event-description/67a6687ee9ff3f3d54eb361752c9fcd1/36679')
        #base_url = reverse('dashboard:step_four', kwargs={'md5':md5, 'event_id':event_id})
        # print(base_url)

        # return redirect(base_url)
        return redirect(reverse('dashboard:step_four', kwargs={'md5': md5, 'event_id': event_id}))

    return render(request, 'dashboard/create-event/step_3/step_three_temp.html', {'event_id': event_id, 'md5': md5})


def step_three_action(request, md5, event_id):

    print(event_id, md5)
    # myfile=request.POST.get('myfile', None)
    # articles2 = Articles2.objects.get(id = event_id)
    # event_name = re.sub('[^A-Za-z0-9 ]+', '',articles2.event_name)
    # event_name = event_name.replace(' ','-')
    # image_name = event_name +'-'+str(event_id)
    # uploadedfileurl=''

    # if request.method=='POST' and request.FILES.get('myfile', None):
    #     myfile=request.FILES['myfile']
    #     print(myfile.name.split('.'))
    #     image_name_banner = image_name +'-' + 'banner' + '.' + myfile.name.split('.')[-1]
    #     print(image_name_banner)
    #     myfile.name = image_name_banner
    #     fs=FileSystemStorage(location='media/events/images')
    #     print(fs)
    #     filename=fs.save(myfile.name,myfile)
    #     print(filename)
    #     uploadedfileurl=fs.url(filename)
    #     u_banner=uploadedfileurl
    # print(u_banner)

    # myfile1=request.POST.get('myfile1', None)

    # print(myfile1)
    # uploadedfileurl_1=''
    # u_p=''
    # if request.method=='POST' and request.FILES.get('myfile1', None):
    #     myfile1=request.FILES['myfile1']
    #     image_name_thumb = image_name +'-' + 'thumbnail' + '.' + myfile1.name.split('.')[-1]
    #     print(image_name_thumb)
    #     myfile1.name = image_name_thumb
    #     fs_1=FileSystemStorage(location='media/events/images')
    #     filename_1=fs_1.save(myfile1.name,myfile1)
    #     uploadedfileurl_1=fs_1.url(filename_1)
    #     u_p =uploadedfileurl_1

    # myfile2=request.POST.get('myfile2', None)

    # print(myfile2)
    # uploadedfileurl_2=''
    # u_editables=''
    # if request.method=='POST' and request.FILES.get('myfile2', None):
    #     myfile2=request.FILES['myfile2']
    #     editable_name = image_name +'-' + 'editable' + '.' + myfile2.name.split('.')[-1]
    #     print(editable_name)
    #     myfile2.name = editable_name
    #     fs_2=FileSystemStorage(location='media/events/editables')
    #     filename2=fs_2.save(myfile2.name,myfile2)
    #     uploadedfileurl_2=fs_2.url(filename2)
    #     u_editables=uploadedfileurl_2

    # articles2.banner = u_banner
    # articles2.profile_image = u_p
    # articles2.editable_image = u_editables
    # #s=Articles2(id=event_id,banner=u_banner,profile_image=u_p,editable_image=u_editables)

    # #print(s)
    # articles2.save()

    # #return render(request, 'dashboard/create-event/step_3/step_three_temp.html',{'event_id':event_id, 'md5':md5,})
    # #return redirect('/live/dashboard/add-event-description/67a6687ee9ff3f3d54eb361752c9fcd1/36679')
    # #base_url = reverse('dashboard:step_four', kwargs={'md5':md5, 'event_id':event_id})
    # #print(base_url)

    # #return redirect(base_url)
    return redirect(reverse('dashboard:step_four', kwargs={'md5': md5, 'event_id': event_id}))

###################################################################################


def create_stall(request):

    return render(request, 'dashboard/create-stalls.html')

####################################################################################


def organizer_agreement(request):

    return render(request, 'dashboard/organizer-agreement.html')


#######################################################################################

def getSalesDetails(request, event_id):
    event = Articles2.objects.all().filter(id=event_id).first()
    print(event)
    eve_name = event.event_name
    print(eve_name)
    # @author Shubham
    sales = TicketsSale.objects.all().filter(event_id=event_id)
    # sales = Tickets_Sale.objects.all().filter(event_id=event_id)
    # ends here ~ @author Shubham
    print(sales)
    t_count = len(sales)
    print(t_count)

    tkt_type = []
    tkt_qty = []
    tkt_amt = []
    tkt_p_date = []
    tkt_s_site = []
    tkt_atendee = []
    tkt_book_id = []

    if t_count != 0:
        for i in sales:
            print(i)
            tkt_book_id.append(i.booking_id)
            tkt_type.append(i.ticket_type)
            tkt_amt.append(i.ampunt_paid)
            tkt_qty.append(i.qty)
            tkt_p_date.append(i.purchase_date)
            tkt_s_site.append(i.seller_site)
            tkt_atendee.append(i.attendee_name)

    details = zip(tkt_type, tkt_book_id, tkt_amt, tkt_qty,
                  tkt_p_date, tkt_s_site, tkt_atendee)
    return render(request, 'sale_detail.html', {'details': details, 'count': t_count, 'eve_name': eve_name})


########################################### boost event button ########################################

def boost(request, event_id):
    if 'userid' not in request.session.keys():
        return redirect('/live/login')
    c = Articles2.objects.all().filter(id=event_id).values('city')
    ac = BoostEvent.objects.all().filter(event_id=event_id)
    print(len(ac))
    if len(ac) == 4:
        # print('\n\n\n','vinayak','\n\n\n\n')
        #  WARNING:  message for user
        messages.warning(request, "can't add more citys")
    else:
        if request.method == "POST":
            form = BoostEventForm(request.POST)
            if form.is_valid():
                ei = form.save(commit=False)
                ei.event_id = event_id
                # print('\n\n\n',form,'\n\n\n\n')
                ei.save()
                #####can't redirect because we need to pass values ##############
                c = Articles2.objects.all().filter(id=event_id).values('city')
                ac = BoostEvent.objects.all().filter(event_id=event_id)
                form = BoostEventForm()
                return render(request, 'dashboard/boost_event.html', {'event_id': event_id, 's': c, 'ac': ac, 'form': form})
    form = BoostEventForm()

    return render(request, 'dashboard/boost_event.html', {'event_id': event_id, 's': c, 'ac': ac, 'form': form})



###########################update contact##############################
def updateMobileNo(request):
    if 'userid' not in request.session.keys():
        return redirect('/live/login')
    if request.method == "POST":
        form = UpdateContact(request.POST)
        if form.is_valid():
            #######################contact#########################
            user = Users.objects.get(pk=request.session['userid'])
            user.mobile = request.POST['mobile']
            print('\n\n\n\n\n\n\n',user.mobile,'/t vinayak')
            user.save()
            #######################################################
            return HttpResponseRedirect(reverse('dashboard:step_one'))
        else:
            return render(request,'dashboard/updateContact.html',{'form':form})

    else:
        form =  UpdateContact()
        return render(request,'dashboard/updateContact.html',{'form':form})


########################################################################

def update_event_tickets(request, md5, event_id, ticket_id):
    if request.method == 'POST':
        print(event_id)
        now = datetime.now()
        # a=Tickets.objects.all().filter(event_id=event_id).values('tickets_id')
        # t_id=a[0]['tickets_id']
        # print(t_id)
        l = []
        t = Tickets.objects.get(tickets_id=ticket_id)
        ticket_name = request.POST.get('ticket_name', '')
        l.append(ticket_name)
        ticket_price = request.POST.get('ticket_price', '')
        l.append(ticket_price)
        other_charges = request.POST.get('other_charges', '')
        l.append(other_charges)
        other_charges_type = request.POST.get('other_charges_type', '')
        l.append(int(other_charges_type))
        ticket_qty = request.POST.get('ticket_qty', '')
        l.append(int(ticket_qty))
        min_qty = request.POST.get('min_qty', '')
        l.append(int(min_qty))
        max_qty = request.POST.get('max_qty', '')
        l.append(int(max_qty))

        tsd = request.POST.get('start_date')
        start_t = request.POST.get('start_time_step5')

        if start_t[0] == '1' and start_t[1] != ':':
            if start_t[6:] == 'AM' and start_t[:2] != '12':
                start_time = now.time().replace(hour=int(start_t[:2]), minute=int(
                    start_t[3:5]), second=0, microsecond=0)
            elif start_t[6:] == 'AM' and start_t[:2] == '12':
                # print("herrrrrrrrrrrrreeeeeeeeeeeeeeeeeeeeeeeeeee")
                start_time = now.time().replace(hour=0, minute=int(
                    start_t[3:5]), second=0, microsecond=0)
            elif start_t[6:] == 'PM' and start_t[:2] == '12':
                start_time = now.time().replace(hour=int(start_t[:2]), minute=int(
                    start_t[3:5]), second=0, microsecond=0)
            else:
                start_time = now.time().replace(
                    hour=(int(start_t[:2]) + 12), minute=int(start_t[3:5]), second=0, microsecond=0)
        else:
            if start_t[5:] == 'AM':
                start_time = now.time().replace(hour=int(start_t[0]), minute=int(
                    start_t[2:4]), second=0, microsecond=0)
            else:
                start_time = now.time().replace(
                    hour=(int(start_t[0]) + 12), minute=int(start_t[2:4]), second=0, microsecond=0)

        st = str(start_time)
        sd = request.POST.get('end_date')
        end_t = request.POST.get('end_time_step5')

        if end_t[0] == '1' and end_t[1] != ':':
            if end_t[6:] == 'AM' and end_t[:2] != '12':
                end_time = now.time().replace(hour=int(end_t[:2]), minute=int(
                    end_t[3:5]), second=0, microsecond=0)
            elif end_t[6:] == 'AM' and end_t[:2] == '12':
                # print("herrrrrrrrrrrrreeeeeeeeeeeeeeeeeeeeeeeeeee")
                end_time = now.time().replace(hour=0, minute=int(
                    end_t[3:5]), second=0, microsecond=0)
            elif end_t[6:] == 'PM' and end_t[:2] == '12':
                end_time = now.time().replace(hour=int(end_t[:2]), minute=int(
                    end_t[3:5]), second=0, microsecond=0)
            else:
                end_time = now.time().replace(
                    hour=(int(end_t[:2]) + 12), minute=int(end_t[3:5]), second=0, microsecond=0)
        else:
            if end_t[5:] == 'AM':
                end_time = now.time().replace(hour=int(end_t[0]), minute=int(
                    end_t[2:4]), second=0, microsecond=0)
            else:
                end_time = now.time().replace(
                    hour=(int(end_t[0]) + 12), minute=int(end_t[2:4]), second=0, microsecond=0)

        o = str(end_time)
        print(tsd + st)
        print(type(l), st)
        ticket_start_date = tsd + " " + st
        ticket_start_date = datetime.strptime(
            ticket_start_date, '%d/%m/%Y %H:%M:%S')
        l.append(ticket_start_date)
        expiry_date = sd + " " + o
        expiry_date = datetime.strptime(expiry_date, '%d/%m/%Y %H:%M:%S')
        l.append(expiry_date)
        print(ticket_start_date, expiry_date)

        ticket_msg = request.POST.get('ticket_msg', '')
        l.append(ticket_msg)
        ticket_label = request.POST.get('ticket_label', '')
        l.append(ticket_label)
        print(l)
        par = ['ticket_name', 'ticket_price', 'other_charges', 'other_charges_type', 'ticket_qty',
               'min_qty', 'max_qty', 'ticket_start_date', 'expiry_date', 'ticket_msg', 'ticket_label']

        # for i in range(0, len(l) - 4):
        #     print(l[i], s[i])

        t.ticket_name = ticket_name
        t.ticket_price = ticket_price
        t.other_charges = other_charges
        t.other_charges_type = other_charges_type
        t.ticket_qty = ticket_qty
        t.min_qty = min_qty
        t.max_qty = max_qty
        t.ticket_start_date = ticket_start_date
        t.expiry_date = expiry_date
        t.ticket_msg = ticket_msg
        t.ticket_label = ticket_label

        t.save()

        return HttpResponseRedirect(reverse('dashboard:step_five', args=(md5,event_id)))



# code for edit images step 3 on edit event mode
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEDIA_DIR = os.path.join(BASE_DIR, 'media')
def edit_event_three(request, event_id):
    if 'userid' not in request.session.keys():
        return redirect('/live/login')

    if request.method == 'GET':
        article = Articles2.objects.get(id=event_id)
        pro_image= article.profile_image
        banner = article.banner
        edit_image = article.editable_image
        return render(request, 'dashboard/edit_event_three.html', {'pro_image': pro_image, 'banner': banner, 'edit_image':edit_image})
        # return render(request, 'dashboard/edit_event_three.html', {'event_id': 'event_id', 'ticket_id': 'ticket_id', 'event_start_date': 'date11', 'sdate': 'sdate11', 's': 's'})

    if request.method == 'POST':
        articles2 = Articles2.objects.get(id=event_id)
        event_name = re.sub('[^A-Za-z0-9 ]+', '', articles2.event_name)
        event_name = event_name.replace(' ', '-')
        image_name = event_name + '-' + str(event_id)
        print(image_name)
        uploadedfileurl = ''
        u_banner = ''
        if request.method == 'POST' and request.FILES.get('myfile', None):
            myfile = request.FILES['myfile']
            logging.debug('{}'.format(myfile))
            logging.debug(myfile.name.split('.'))
            image_name_banner = image_name + '-' + \
                'banner' + '.' + myfile.name.split('.')[-1]
            logging.debug(
                'banner image name will be saved as: {}'.format(image_name_banner))
            # logging.debug(image_name_banner)
            myfile.name = image_name_banner
            x_s = request.POST.get('x', '')
            y_s = request.POST.get('y', '')
            w_s = request.POST.get('width', '')
            h_s = request.POST.get('height', '')

            if(x_s == None or x_s == ''):
                x = 0
                y = 0
            else:
                x = float(x_s)
                y = float(y_s)
            w = float(w_s)
            h = float(h_s)


            image = Image.open(myfile)
            cropped_image = image.crop((x, y, w + x, h + y))
            # cropped_image = image.crop((x, y, w, h))
            # cropped_image = image.crop((0.0, 100.0, 800.0, 800.0))
            resized_image = cropped_image.resize((1600, 900), Image.ANTIALIAS)

            fs = FileSystemStorage(location='media')
            # logging.debug('File system storage data: {}'.format(fs))
            # # logging.debug(fs)
            # fs.save(myfile.name,resized_image)
            resized_image.name = myfile.name

            if os.path.exists(MEDIA_DIR + "/" + resized_image.name):
                os.remove(MEDIA_DIR + "/" + resized_image.name)
            resized_image.save(MEDIA_DIR + "/" + resized_image.name, format='PNG')
            filename = resized_image.name
            logging.debug('final name: {}'.format(filename))
            # logging.debug(filename)
            uploadedfileurl = fs.url(filename)
            u_banner = uploadedfileurl
            Articles2.objects.filter(id=event_id).update(banner=u_banner)
        # logging.debug(u_banner)
        logging.debug('Saved url in db: {}'.format(u_banner))

        myfile1 = request.POST.get('myfile1', None)

        print(myfile1)
        uploadedfileurl_1 = ''
        u_p = ''
        if request.method == 'POST' and request.FILES.get('myfile1', None):
            myfile1 = request.FILES['myfile1']
            image_name_thumb = image_name + '-' + \
                'thumbnail' + '.' + myfile1.name.split('.')[-1]
            print(image_name_thumb)
            myfile1.name = image_name_thumb
            fs_1 = FileSystemStorage(location='media')
            print(myfile1.name, myfile1)
            if os.path.exists(MEDIA_DIR + "/" + myfile1.name):
                os.remove(MEDIA_DIR + "/" + myfile1.name)
            filename_1 = fs_1.save(myfile1.name, myfile1)
            uploadedfileurl_1 = fs_1.url(filename_1)
            u_p = uploadedfileurl_1
            Articles2.objects.filter(id=event_id).update(profile_image=u_p)


        myfile2 = request.POST.get('myfile2', None)

        print(myfile2)
        uploadedfileurl_2 = ''
        u_editables = ''
        if request.method == 'POST' and request.FILES.get('myfile2', None):
            myfile2 = request.FILES['myfile2']
            editable_name = image_name + '-' + 'editable' + \
                '.' + myfile2.name.split('.')[-1]
            print(editable_name)
            myfile2.name = editable_name
            fs_2 = FileSystemStorage(location='media/editables')
            if os.path.exists(MEDIA_DIR + "/editables/" + myfile2.name):
                os.remove(MEDIA_DIR + "/editables/" + myfile2.name)
            filename2 = fs_2.save(myfile2.name, myfile2)
            uploadedfileurl_2 = fs_2.url(filename2)
            u_editables = uploadedfileurl_2
            u_editables = uploadedfileurl_2.replace("/media/", "/media/editables/")
            Articles2.objects.filter(id=event_id).update(editable_image=u_editables)
        # articles2.banner = u_banner
        # articles2.profile_image = u_p
        # articles2.editable_image = u_editables
        # s=Articles2(id=event_id,banner=u_banner,profile_image=u_p,editable_image=u_editables)

        # print(s)
        # articles2.save()



        # return redirect(base_url)
        return redirect(reverse('dashboard:edit-event-three', args={event_id}))

    return render(request, 'dashboard/edit_event_three.html', {'pro_image': pro_image, 'banner': banner, 'edit_image':edit_image})
# ends here ~ code for edit images step 3 on edit event mode
