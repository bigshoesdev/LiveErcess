from hashlib import md5
from django.shortcuts import redirect, get_object_or_404, render_to_response, render
from django.http import HttpResponse
from django.contrib import messages
from django.core import serializers
from django.urls import reverse
from urllib.parse import urlencode
from rest_framework.renderers import TemplateHTMLRenderer, StaticHTMLRenderer
from rest_framework.generics import ListCreateAPIView, ListAPIView
from rest_framework.response import Response
from datetime import datetime
import json



from dashboard.models import (Articles2, Categories, Topics, StatusPromotionTicketing,
                             AttendeeFormTypes, AttendeeFormOptions, AttendeeFormBuilder,
                             Tickets, AboutCountries, BankDetails)
from dashboard.forms import Articles2Form
from .serializers import (Articles2Serializer, CategorizedEventsSerializer,
                         StatusPromotionTicketingSerializer, TicketsSerializer,
                          BankDetailsSerializer)


from Ercesscorp.models import Users

class ArticlesCreateAPIView(ListCreateAPIView):
    renderer_classes = [TemplateHTMLRenderer]
    queryset = Articles2.objects.all()
    serializer_class= Articles2Serializer
    template_name = 'dashboard/create-event/step_1/step_one.html'

    def get(self, request, *args, **kwargs):
        if 'userid' not in request.session.keys():
            return redirect('/live/login')
        #######################contact#########################
        user = Users.objects.get(pk=request.session['userid'])
        print('\n\n\n\n\n\n',user.mobile)
        if user.mobile == '' or user.mobile == 0 :
            return redirect('dashboard:updateContact')

        #######################################################

        return Response({'dashboard': self.queryset, 'serializer':self.serializer_class})


    def post(self, request, *args, **kwargs):
        if 'userid' not in request.session.keys():
            return redirect('/live/login')
        #######################contact#########################
        user = Users.objects.get(pk=request.session['userid'])
        print('\n\n\n\n\n\n',user.mobile)
        if user.mobile == '' or user.mobile == 0 :
            return redirect('dashboard:updateContact')

        #######################################################

        event_md5 = md5(request.data.get('event_name').encode('utf-8')).hexdigest()[:34]
        print(event_md5)
        print("Up postttttttttttttttttt")
        context = {'md5' : event_md5}
        event_name=request.data.get('event_name')
        print(event_name)
        # l.append(event_name)
        serializer = Articles2Serializer(data=request.data, context=context)
        if not serializer.is_valid():
            return Response({'serializer': serializer,'flag':True,'event_name':event_name})
        print(serializer)
        print("posttttttttttttttttttttttttt")
        obj = serializer.save()

        venue_not_decided = request.data.get('venue_not_decided');
        if venue_not_decided == 'true':
            obj.venue_not_decided = True
            obj.full_address = ''
        else:
            obj.venue_not_decided = False
            obj.full_address = obj.address_line1+ "," + str(obj.address_line2)+ "," + obj.state + "," + obj.city + "," + str(obj.pincode)

        event_id = obj.id
        obj.save()
        #user_id = request.user.id
        user_id = request.session.get('userid')
        unique_id = f'EL{event_id}'
        data = {'event_id':event_id, 'unique_id':unique_id,'mode':'created',
                'private':0,'event_active':1,'approval':0, 'network_share':1,
                'ticketing':0, 'promotion':0, 'connected_user':user_id, 'complete_details':0}

        serializer = StatusPromotionTicketingSerializer(data=data)
        if not serializer.is_valid():
            return Response({'serializer': serializer,'flag':True})
        serializer.save()
        messages.success(request, f'Thank you. Event has been registered. your event id is {event_id}')
        base_url = reverse('dashboard:step_two', kwargs={'md5':event_md5, 'event_id':event_id})
        return redirect(base_url)

class CategoryCreateAPIView(ListCreateAPIView):
    renderer_classes = [TemplateHTMLRenderer]

    def get(self, request, event_id, md5, *args, **kwargs):
        #if 'userid' not in request.session.keys():
         #   return redirect('/live/login')
        request.session['event_id'] = event_id
        request.session['md5'] = md5

        qs_categories = Categories.objects.values_list('category_id', 'category')
        return Response({'context':qs_categories}, template_name = 'dashboard/create-event/step_2/step_two.html')

    def post(self, request, *args, **kwargs):
        if 'userid' not in request.session.keys():
            return redirect('/live/login')
        md5 = request.session['md5']
        event_id = request.session['event_id']
        context = {'event_id' : event_id}
        print(request.data)
        serializer = CategorizedEventsSerializer(data=request.data, context=context)
        if not serializer.is_valid():
            return Response({'serializer': serializer,'flag':True})
        serializer.save()
        print("----updated event tables")
        user_id = request.user.id
        if not user_id:
            user_id = 1
        unique_id = f'EL{event_id}'

        if request.POST.get('type1') == 'public':
            type_event = 0
        else:
            type_event = 1
        if request.POST.get('type2') == 'paid':
            ticketing = 1
        else:
            ticketing = 0
        data = {'private':type_event, 'ticketing':ticketing,}
        inst = get_object_or_404(StatusPromotionTicketing, event_id=event_id)
        print(inst)
        serializer = StatusPromotionTicketingSerializer(inst, data=data, partial=True)
        if not serializer.is_valid():
            return Response({'serializer': serializer,'flag':True})
        serializer.save()
        base_url = reverse('dashboard:step_three', kwargs={'md5':md5, 'event_id':event_id})
        return redirect(base_url)


class TopicsListAPIView(ListAPIView):
    def get(self, request):
        cat_id = request.GET.get('id')
        queryset = Topics.objects.filter(category=cat_id).order_by('topic')
        data = serializers.serialize('json', list(queryset))
        return HttpResponse(data)

class ThirdStepTemp(ListCreateAPIView):
    renderer_classes = [TemplateHTMLRenderer]

    def get(self, request, event_id, md5, *args, **kwargs):
        if 'userid' not in request.session.keys():
            return redirect('/live/login')
        request.session['event_id'] = event_id
        request.session['md5'] = md5
        return Response({}, template_name = 'dashboard/create-event/step_3/step_three_temp.html')

    def post(self, request, *args, **kwargs):
        if 'userid' not in request.session.keys():
            return redirect('/live/login')
        md5 = request.session['md5']
        event_id = request.session['event_id']
        base_url = reverse('dashboard:step_four', kwargs={'md5':md5, 'event_id':event_id})
        return redirect(base_url)

class DescriptionCreateAPIView(ListCreateAPIView):
    renderer_classes = [TemplateHTMLRenderer]

    def get(self, request, event_id, md5, *args, **kwargs):
        if 'userid' not in request.session.keys():
            return redirect('/live/login')
        request.session['event_id'] = event_id
        request.session['md5'] = md5
        inst = get_object_or_404(Articles2, id=event_id)

        # qs_india=get_object_or_404(AboutCountries, country=inst.country)
        # make country optional in step 3 
        try:
            bankInfoFilter = AboutCountries.objects.get(country=inst.country)
            bank_regex1 = bankInfoFilter.bank_regex1
            bank_regex2 = bankInfoFilter.bank_regex2
        except Exception as e:
            bank_regex1 = '/[0-9]{9,18}/'
            bank_regex2 = '/[A-Za-z]{4}[0-9]{7}/'
        # ends here ~ make country optional in step 3 
        
        descform = Articles2Form()
        return Response({'descform':descform, 'bank_regex1':bank_regex1,'bank_regex2':bank_regex2},
                        template_name = 'dashboard/create-event/step_4/step_four.html')

    def post(self, request, *args, **kwargs):
        if 'userid' not in request.session.keys():
            return redirect('/live/login')
        md5 = request.session['md5']
        event_id = request.session['event_id']
        print('== == == == == == == == == == == == == == == ==')
        print(event_id)
        print(' == Articles2 ==')
        print(Articles2)
        descform = Articles2Form(request.POST, instance = get_object_or_404(Articles2, id=event_id))

        print('descform >>',descform)
        if not descform.is_valid():
            return Response({'descform': descform,'flag':True})
        descform.save()
        tkt_type = StatusPromotionTicketing.objects.all().filter(event_id=event_id)
        type = tkt_type[0].ticketing
        if type == 0:
            base_url = reverse('dashboard:step_six', kwargs={'md5':md5, 'event_id':event_id})
        elif type == 1:
            base_url = reverse('dashboard:step_five', kwargs={'md5': md5, 'event_id': event_id})
        return redirect(base_url)


class QuestionCreateAPIView(ListCreateAPIView):
    renderer_classes = [TemplateHTMLRenderer]

    def get(self, request, event_id, md5, *args, **kwargs):
        print('--------------------')
        print(request.session.keys())
        if 'userid' not in request.session.keys():
            return redirect('/live/login')
        request.session['event_id'] = event_id
        request.session['md5'] = md5
        inst = get_object_or_404(StatusPromotionTicketing, event_id=event_id)
        print(inst)
        data={'complete_details':1}
        serializer = StatusPromotionTicketingSerializer(inst, data=data, partial=True)
        if not serializer.is_valid():
            return Response({'serializer': serializer,'flag':True})
        serializer.save()
        qs_types = AttendeeFormTypes.objects.values_list('type_id', 'name')
        return Response({'context':qs_types}, template_name = 'dashboard/create-event/step_6/step_six.html')

    def post(self, request, *args, **kwargs):
        if 'userid' not in request.session.keys():
            return redirect('/live/login')
        md5 = request.session['md5']
        event_id = request.session['event_id']
        print("-------------------------------")
        print(event_id)
        print(request.POST.items())
        for i,j in request.POST.items():
            print(i,j)
        for i,j in request.POST.items():
            if i not in ['csrfmiddlewaretoken']:
                ques = request.POST.getlist(i)
                print(ques)
                type_inst = AttendeeFormTypes.objects.get(name=ques[2])
                type_id=type_inst.type_id
                add_que = AttendeeFormBuilder(event_id=event_id, ques_title=ques[1],
                                          ques_accessibility=int(ques[0]), ques_type=type_id)
                add_que.save()
                que_id = add_que.ques_id
                if type_id == 5:
                    options = ques[-1].split(',')
                    print(options)
                    for op in options:
                        add_op = AttendeeFormOptions(event_id=event_id, ques_id=que_id, option_name=op)
                        add_op.save()
        base_url = reverse('dashboard:event_added')
        return HttpResponse(base_url)

class CreateTicketsView(ListCreateAPIView):

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'dashboard/create-event/step_5/step_five.html'
    tickets = Tickets.objects.all()
    aboutcountries = AboutCountries.objects.all()
    now = datetime.now()

    #event_id = 20

    serializer_class= TicketsSerializer(context=tickets)

    def get(self, request,event_id, md5, *args, **kwargs):    # must be included
        if 'userid' not in request.session.keys():
            return redirect('/live/login')
        request.session['event_id'] = event_id
        request.session['md5'] = md5


        inst = get_object_or_404(Articles2, id=event_id)
        print(inst.sdate)
        date = inst.sdate.strftime('%m/%d/%Y')
        sdate = inst.sdate.strftime('%d/%m/%Y')
        edate = inst.edate.strftime('%d/%m/%Y')
        eventStartTime = inst.start_time.strftime('%H:%M')
        eventEndTime = inst.end_time.strftime('%H:%M')
        # print(date,sdate)
        # sd = Articles2.objects.all().filter(id=event_id).values('sdate')
        # endDate = Articles2.objects.all().filter(id=event_id).values('edate')
        # print(endDate)
        names=[]
        prices=[]
        ticketvals= Tickets.objects.all().filter(event_id=event_id)
        print(ticketvals)
        for i in range(0,len(ticketvals)):
            names.append(ticketvals.values('ticket_name')[i]['ticket_name'])
            prices.append(ticketvals.values('ticket_price')[i]['ticket_price'])
        ticketnames = json.dumps(names)
        print(names,prices)
        ticketvalues= Tickets.objects.values()
        listdictticket = [entry for entry in ticketvalues]
        listticket=[d['event_id'] for d in listdictticket]
        flag=False
        if event_id in listticket:
            flag=True

        # print(listticket)
        # print(request.session.values())

        return Response({'ticket': ticketvalues, 'event_id': event_id , 'md5':md5,'serializer':self.serializer_class,'event_start_date':date, 'sdate':sdate, 'edate':edate,'event_start_time':eventStartTime,'event_end_time':eventEndTime,
                'a':self.aboutcountries,'cureventid':event_id,'flag':flag,'names':names,'prices':prices, 'ticketnames':ticketnames},
                 template_name = 'dashboard/create-event/step_5/step_five.html'  )

    def post(self, request, *args, **kwargs):
        if 'userid' not in request.session.keys():
            return redirect('/live/login')
        md5 = request.session['md5']
        event_id = request.session['event_id']
        now = datetime.now()
        #context = {'event_id' : event_id}
        print(request.data)
        tsd = request.data.get('start_date')
        # exd = request.data.get('start_time_step5')

        start_t = request.POST.get('start_time_step5')

        if start_t[0] == '1' and start_t[1] != ':':
            if start_t[6:] == 'AM' and start_t[:2] != '12':
                start_time = now.time().replace(hour=int(start_t[:2]), minute=int(start_t[3:5]), second=0, microsecond=0)
            elif start_t[6:] == 'AM' and start_t[:2] == '12':
                # print("herrrrrrrrrrrrreeeeeeeeeeeeeeeeeeeeeeeeeee")
                start_time = now.time().replace(hour=0, minute=int(start_t[3:5]), second=0, microsecond=0)
            elif start_t[6:] == 'PM' and start_t[:2] == '12':
                start_time = now.time().replace(hour=int(start_t[:2]), minute=int(start_t[3:5]), second=0, microsecond=0)
            else:
                start_time = now.time().replace(hour=(int(start_t[:2]) + 12), minute=int(start_t[3:5]), second=0, microsecond=0)
        else:
            if start_t[5:] == 'AM':
                start_time = now.time().replace(hour=int(start_t[0]), minute=int(start_t[2:4]), second=0, microsecond=0)
            else:
                start_time = now.time().replace(hour=(int(start_t[0]) + 12), minute=int(start_t[2:4]), second=0, microsecond=0)

        exd=str(start_time)


        sd = request.data.get('end_date')
        # xd = request.data.get('end_time_step5')

        end_t = request.POST.get('end_time_step5')


        if end_t[0] == '1' and end_t[1] != ':':
            if end_t[6:] == 'AM' and end_t[:2] != '12':
                end_time = now.time().replace(hour=int(end_t[:2]), minute=int(end_t[3:5]), second=0, microsecond=0)
            elif end_t[6:] == 'AM' and end_t[:2] == '12':
                # print("herrrrrrrrrrrrreeeeeeeeeeeeeeeeeeeeeeeeeee")
                end_time = now.time().replace(hour=0, minute=int(end_t[3:5]), second=0, microsecond=0)
            elif end_t[6:] == 'PM' and end_t[:2] == '12':
                end_time = now.time().replace(hour=int(end_t[:2]), minute=int(end_t[3:5]), second=0, microsecond=0)
            else:
                end_time = now.time().replace(hour=(int(end_t[:2]) + 12), minute=int(end_t[3:5]), second=0, microsecond=0)
        else:
            if end_t[5:] == 'AM':
                end_time = now.time().replace(hour=int(end_t[0]), minute=int(end_t[2:4]), second=0, microsecond=0)
            else:
                end_time = now.time().replace(hour=(int(end_t[0]) + 12), minute=int(end_t[2:4]), second=0, microsecond=0)


        xd=str(end_time)


        print(exd,xd)
        total_qty = request.data.get('ticket_qty')
        print(tsd + exd )
        print(exd)
        ticket_start_date = tsd +" "+ exd
        ticket_start_date = datetime.strptime(ticket_start_date, '%d/%m/%Y %H:%M:%S')
        expiry_date= sd +" "+ xd
        expiry_date= datetime.strptime(expiry_date, '%d/%m/%Y %H:%M:%S')
        context = {'ticket_start_date' : ticket_start_date,'expiry_date' :  expiry_date, 'event_id' : event_id, 'qty_left' : total_qty, 'ercess_fee': 1, 'transaction_fee':1}
        serializer = TicketsSerializer(data=request.data,  context = context)
        print("hi is this code running")
        print(serializer)
        if not serializer.is_valid():
            return Response({'serializer': serializer,'flag':True})
        serializer.save()
        print("data stored in table")
        print('md5 is {} and event_id is {}'.format(md5, event_id))
        base_url = reverse('dashboard:step_five', kwargs={'md5':md5, 'event_id':event_id})
        return redirect(base_url)
'''
class CreateTicketsView(ListCreateAPIView):

    renderer_classes = [TemplateHTMLRenderer]
#    template_name = 'dashboard/step_one.html'#templates-snippets/base.html'
    queryset = Tickets.objects.all()
    aboutcountries = AboutCountries.objects.all()
    serializer_class= TicketsSerializer(context=queryset)

    def get(self, request, event_id, md5, *args, **kwargs):#event_id, md5, must be included
        request.session['event_id'] = event_id
        request.session['md5'] = md5
        return Response({'dashboard': self.queryset, 'serializer':self.serializer_class, 'a':self.aboutcountries}, template_name = 'dashboard/create-event/step_5/step_five.html')

    def post(self, request, *args, **kwargs):
        md5 = request.session['md5'] #commented for now
        event_id = request.session['event_id']#commented fro now
        #context = {'event_id' : event_id}
        tsd = request.data.get('ticket_start_date')
        exd = request.data.get('expiry_date')

        context = {'ticket_start_date' : tsd,'expiry_date' : exd,}
        serializer = TicketsSerializer(data=request.data,context = context)
        print("hi is this code running")
        if not serializer.is_valid():
            return Response({'serializer': serializer,'flag':True})
        serializer.save()
        print("is this code running")
        base_url = reverse('dashboard:step_six', kwargs={'md5':md5, 'event_id':event_id})
        return redirect(base_url)
        return HttpResponse("Finally")
'''
class BankDetailsView(ListCreateAPIView):
    renderer_classes = [TemplateHTMLRenderer]
    serializer_class= BankDetailsSerializer
    template_name = 'dashboard/bankdetails.html'
    bankdetailscontents = BankDetails.objects.all()


    def get(self, request, *args, **kwargs):
        bankdetailscontents = BankDetails.objects.all()
        if 'userid' not in request.session.keys():
            return redirect('/live/login')
        user_id = request.session.get('userid')
        for uid in bankdetailscontents:
            if (uid.user_id==user_id):
                return Response({'serializer':self.serializer_class,'i':uid, 'flag':False}, template_name = 'dashboard/bankdetails.html')
        return Response({'serializer':self.serializer_class,'flag':True}, template_name = 'dashboard/bankdetails.html')


    def post(self, request, *args, **kwargs):
        context = {'user_id': request.session.get('userid')}
        serializer = BankDetailsSerializer(data=request.data, context=context)

        print(serializer)
        print("hi")
        print(request.data)
        if not serializer.is_valid():
            print(serializer.errors)
            return Response({'serializer': serializer,'flag':True})
        serializer.save()
        return redirect('/live/dashboard/bank-details')


# for edit bank details
class EditBankDetailsView(ListCreateAPIView):
    renderer_classes = [TemplateHTMLRenderer]
    serializer_class= BankDetailsSerializer
    template_name = 'dashboard/bankdetails.html'
    bankdetailscontents = BankDetails.objects.all()


    def get(self, request, *args, **kwargs):
        bankdetailscontents = BankDetails.objects.all()
        if 'userid' not in request.session.keys():
            return redirect('/live/login')
        user_id = request.session.get('userid')
        for uid in bankdetailscontents:
            if (uid.user_id==user_id):
                return Response({'serializer':self.serializer_class,'i':uid, 'flag':False}, template_name = 'dashboard/bankdetails.html')
        return Response({'serializer':self.serializer_class,'flag':True}, template_name = 'dashboard/bankdetails.html')


    def post(self, request, *args, **kwargs):
        if 'userid' not in request.session.keys():
            return redirect('/live/login')
        currentUserId = request.session.get('userid')
        bankDetailsData = request.data

        bankName = bankDetailsData['bank_name']
        acHolderName = bankDetailsData['ac_holder_name']
        acType = bankDetailsData['ac_type']
        acNumber = bankDetailsData['ac_number']
        ifscCode = bankDetailsData['ifsc_code']
        branch = bankDetailsData['branch']

        # print(' > currentUserId > ',currentUserId)

        BankDetails.objects.filter(user_id=currentUserId).update(bank_name=bankName, ac_holder_name=acHolderName, ac_type=acType, ac_number=acNumber, ifsc_code=ifscCode, branch=branch)

        return redirect('/live/dashboard/bank-details')
        
        # serializer = BankDetailsSerializer(data=request.data, context=context)

        # print(serializer)
        # print("hi")
        # print(request.data)
        # if not serializer.is_valid():
        #     print(serializer.errors)
        #     return Response({'serializer': serializer,'flag':True})
        # serializer.save()
        # return redirect('/live/dashboard/bank-details')
# ends here ~ for edit bank details