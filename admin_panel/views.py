from django.shortcuts import render,HttpResponse,redirect,HttpResponseRedirect,reverse,get_object_or_404
# Create your views here.
# from admin_panel.forms import LoginForm,EditForm,AddRsvpForm,AddSalesDetailsForm,AddUserForm
from admin_panel.forms import LoginForm,EditForm,AddRsvpForm,AddSalesDetailsForm

from dashboard.models import Admin,AdminAccesses,AdminActionLog,StatusPromotionTicketing,Articles2,AttendeeFormBuilder,AttendeeFormOptions, AttendeeFormTypes, Tickets,AboutCountries ,TicketsSale,Categories,CategorizedEvents,Topics,EventVerificationResult,EventProcesses,StatusOnChannel,EventStatusOnChannel, PartnerSites,Rsvp,AdminAccessTypes,PaymentSettlement,BankDetails,ErcessIndiaeveStates,ErcessPartnersCategories,ErcessPartnersSubcategories,PartnerCurrencies,PartnerTimezones,ErcessOtherMappings
from django.core.exceptions import ObjectDoesNotExist
from Ercesscorp.models import Users
from datetime import datetime
from django.contrib import messages
from django.utils import timezone
from django.core.validators import ValidationError
from Ercesscorp.models import UserRegistrationToken

from dashboard.serializers import EditViewSerializer,EditTicketSerializer
from rest_framework.views import APIView
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from django.conf import settings
from django.core.mail import  send_mail
from django.template.loader import render_to_string
from django.core.mail import EmailMessage

from smtplib import SMTPException
from django.views import View
from django.views.generic import  UpdateView
from django.urls import reverse_lazy
from django.views import generic
from django.core.mail import EmailMultiAlternatives
import hashlib
import string
import random




def admin_login(request):

    form = LoginForm()

    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            email = request.POST.get('email')
            password = request.POST.get('password')
            print(email)

            if Admin.objects.filter(email_id = email).exists():
                print("1st stage")

                if Admin.objects.filter(email_id = email , password = password).exists():
                    print("2nd stage")
                    admin_user = Admin.objects.get(email_id = email)
                    print(admin_user)

                    if admin_user.admin_active == 1:

                        #grabbing sessions from Admin model
                        request.session['admin_id'] = admin_user.table_id
                        request.session['fname'] = admin_user.fname
                        request.session['lname'] = admin_user.lname
                        request.session['mobile'] = admin_user.mobile
                        print(request.session['admin_id'])
                        print(request.session['fname'])

                        access = AdminAccesses.objects.filter(admin_id = admin_user.table_id).order_by('access_type')


                        # grabbing sessions from AdminAccess model
                        print(access)

                        for i in access:
                            type = AdminAccessTypes.objects.all().filter(table_id= i.access_type)
                            request.session['para_'+str(i.access_type)] = type[0].parameter
                            request.session['read_'+str(i.access_type)] = i.read_access
                            request.session['write_'+str(i.access_type)] = i.write_access
                            request.session['delete_'+str(i.access_type)] = i.delete_access
                        print("access is working")

                        for i,j in request.session.items():
                            print(str(i) +" : " +str(j))



                        #storing in access action log
                        access_log = AdminActionLog()
                        access_log.admin_id = request.session['admin_id']
                        access_log.timestamp = datetime.now()
                        access_log.parameter = "log-in"
                        access_log.action_taken = "logged-in"
                        access_log.event_id = 0
                        access_log.save()

                        return redirect('admin-panel:home')
                    else:
                        messages.error(request,"Sorry you dont have admin access")
                else:
                    messages.error(request,'Wrong Password')
            else:
                messages.error(request,'Wrong Admin')
        else:
            messages.error(request,'Form looks invalid')

    return render(request, 'admin_panel/login_admin.html',{'form':form})


def admin_home(request):
    if 'admin_id' not in request.session.keys():
        return redirect('/admin-site/login')
    return render(request,'admin_panel/admin_home.html')


def eventList(request):
    if 'admin_id' not in request.session.keys():
        return redirect('/admin-site/login')



    new_stat =StatusPromotionTicketing.objects.all().filter(complete_details=1,approval = 0).\
        exclude(event_active =5).order_by('-event_id')

    app_stat =StatusPromotionTicketing.objects.all().filter(complete_details=1,approval=1).\
        exclude(event_active=5).order_by('-event_id')

    unapp_stat =StatusPromotionTicketing.objects.all().filter(complete_details=1,approval=0,event_active=5)

    drafts_stat =StatusPromotionTicketing.objects.all().exclude(complete_details=1)

    time =timezone.now()

    ############################################################---------------------------    UPCOMING TAB
    ###########   NEW EVENT   ###########
    print("NEW EVENT ----------------------------------")
    new_id =[]
    new_name=[]
    new_create =[]
    new_start =[]
    new_username = []

    for i in new_stat:
        print(i.event_id)
        print(i.connected_user)
        event = Articles2.objects.all().filter(id = i.event_id)
        user =  Users.objects.all().filter(id=i.connected_user)
        print(user)
        if len(event)!=0:
            if event[0].edate>=time:
                new_id.append(event[0].id)
                new_name.append(event[0].event_name)
                new_create.append(event[0].date_added)
                new_start.append(event[0].sdate)

                if len(user)!=0:
                    new_username.append(user[0].firstname + " " +user[0].lastname)
                else:
                    new_username.append(0)
    print(new_name)
    print(new_username)

    new_items = zip(new_id,new_name,new_create,new_start,new_username)

    #############   APPROVED EVENTS   ###############
    print("APPROVED     ----------------------------------")
    print(app_stat)
    app_id=[]
    app_name=[]
    app_create=[]
    app_start=[]
    app_user=[]
    for i in app_stat:
        event = Articles2.objects.all().filter(id = i.event_id)
        user = Users.objects.all().filter(id = i.connected_user)

        if len(event)!=0:
            if event[0].edate >= time:
                app_id.append(event[0].id)
                app_name.append(event[0].event_name)
                app_create.append(event[0].date_added)
                app_start.append(event[0].sdate)
                if len(user)!=0:
                    app_user.append(user[0].firstname + " " + user[0].lastname)
                else:
                    app_user.append(0)
    print(app_name)
    print(app_user)

    app_items = zip(app_id,app_name,app_create,app_start,app_user)

    ##############    UNAPPROVED EVENTS   ####################
    print("UNAPPROVED              ----------------------------------")
    print(unapp_stat)
    unapp_id=[]
    unapp_name = []
    unapp_create =[]
    unapp_start =[]
    unapp_user = []

    for i in unapp_stat:

        event = Articles2.objects.all().filter(id = i.event_id)
        user = Users.objects.all().filter(id = i.connected_user)

        if len(event)!=0:
            if event[0].edate >= time:
                unapp_id.append(event[0].id)
                unapp_name.append(event[0].event_name)
                unapp_create.append(event[0].date_added)
                unapp_start.append(event[0].sdate)
                if len(user)!=0:
                    unapp_user.append(user[0].firstname +" "+user[0].lastname)
                else:
                    unapp_user.append(0)
    print(unapp_name)
    print(unapp_user)

    unapp_items = zip(unapp_id,unapp_name,unapp_create,unapp_start,unapp_user)

    ###################    DRAFTS    ######################
    print("DRAFTS      ----------------------------------")
    print(drafts_stat)
    d_id =[]
    d_name = []
    d_create = []
    d_start = []
    d_user = []

    for i in drafts_stat:

        event = Articles2.objects.all().filter(id=i.event_id)
        user = Users.objects.all().filter(id=i.connected_user)

        if len(event) != 0:
            if event[0].edate >= time:
                d_id.append(event[0].id)
                d_name.append(event[0].event_name)
                d_create.append(event[0].date_added)
                d_start.append(event[0].sdate)
                if len(user) != 0:
                    d_user.append(user[0].firstname + " " + user[0].lastname)
                else:
                    d_user.append(0)
    print(d_name)
    print(d_user)

    draft = zip(d_id,d_name,d_create,d_start,d_user)

    return render(request,'admin_panel/event_list.html',{'new':new_items,'app':app_items,
                                                        'unapp':unapp_items,'draft':draft})



def pastEventList(request):
    if 'admin_id' not in request.session.keys():
        return redirect('/admin-site/login')

    app_stat = StatusPromotionTicketing.objects.all().filter(complete_details=1, approval=1). \
        exclude(event_active=5).order_by('-event_id').order_by('-event_id')

    unapp_stat = StatusPromotionTicketing.objects.all().filter(complete_details=1, approval=0, event_active=5).order_by('-event_id')

    drafts_stat = StatusPromotionTicketing.objects.all().exclude(complete_details=1).order_by('-event_id')

    time = timezone.now()

    #############   APPROVED EVENTS   ###############
    print("APPROVED     ----------------------------------")
    print(app_stat)
    past_app_id = []
    past_app_name = []
    past_app_create = []
    past_app_start = []
    past_app_user = []
    for i in app_stat:
        event = Articles2.objects.all().filter(id=i.event_id)
        user = Users.objects.all().filter(id=i.connected_user)

        if len(event) != 0:
            if event[0].edate < time:
                past_app_id.append(event[0].id)
                past_app_name.append(event[0].event_name)
                past_app_create.append(event[0].date_added)
                past_app_start.append(event[0].sdate)
                if len(user) != 0:
                    past_app_user.append(user[0].firstname + " " + user[0].lastname)
                else:
                    past_app_user.append(0)
    print(past_app_name)
    print(past_app_user)

    past_app_items = zip(past_app_id, past_app_name, past_app_create, past_app_start, past_app_user)

    ##############    UNAPPROVED EVENTS   ####################
    print("UNAPPROVED              ----------------------------------")
    print(unapp_stat)
    past_unapp_id = []
    past_unapp_name = []
    past_unapp_create = []
    past_unapp_start = []
    past_unapp_user = []

    for i in unapp_stat:

        event = Articles2.objects.all().filter(id=i.event_id)
        user = Users.objects.all().filter(id=i.connected_user)

        if len(event) != 0:
            if event[0].edate < time:
                past_unapp_id.append(event[0].id)
                past_unapp_name.append(event[0].event_name)
                past_unapp_create.append(event[0].date_added)
                past_unapp_start.append(event[0].sdate)
                if len(user) != 0:
                    past_unapp_user.append(user[0].firstname + " " + user[0].lastname)
                else:
                    past_unapp_user.append(0)
    print(past_unapp_name)
    print(past_unapp_user)

    past_unapp_items = zip(past_unapp_id, past_unapp_name, past_unapp_create, past_unapp_start, past_unapp_user)

    ###################    DRAFTS    ######################
    print("DRAFTS      ----------------------------------")
    print(drafts_stat)
    past_d_id = []
    past_d_name = []
    past_d_create = []
    past_d_start = []
    past_d_user = []

    for i in drafts_stat:

        event = Articles2.objects.all().filter(id=i.event_id)
        user = Users.objects.all().filter(id=i.connected_user)

        if len(event) != 0:
            if event[0].edate < time:
                past_d_id.append(event[0].id)

                past_d_name.append(event[0].event_name)
                past_d_create.append(event[0].date_added)
                past_d_start.append(event[0].sdate)
                if len(user) != 0:
                    past_d_user.append(user[0].firstname + " " + user[0].lastname)
                else:
                    past_d_user.append(0)

    past_draft = zip(past_d_id, past_d_name, past_d_create, past_d_start, past_d_user)

    return render(request,'admin_panel/past_event_list.html',{'past_app':past_app_items,
                                                         'past_unapp':past_unapp_items,'past_draft':past_draft})




class EventDetailView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'admin_panel/event_details.html'

    def get_object(self, event_id):
        try:
            return Articles2.objects.get(pk=event_id)
        except Articles2.DoesNotExist:
            raise Http404

    def get(self, request,event_id):
        if 'admin_id' not in request.session.keys():
            return redirect('/admin-site/login')

        form = EditForm()

        id = event_id
        article = self.get_object(event_id)
        serializer = EditViewSerializer(article)
        country=article.country
        pro_image= article.profile_image
        banner = article.banner
        edit_image = article.editable_image
        website = article.website

        images = [pro_image,banner,edit_image]

        #Target Tab----------------------------------------------------------
        s_p_tkt = StatusPromotionTicketing.objects.all().filter(event_id=event_id)
        print(s_p_tkt)
        types=''
        tkt_typ=''
        for i in s_p_tkt:
            types = i.private
            tkt_typ = i.ticketing
        print(types)
        if types == 0 :
            types = 'public'
        else:
            types = 'private'

        if tkt_typ == 0:
            tkt_typ = 'free'
        else:
            tkt_typ = 'paid'
        print(types)
        print(tkt_typ)

        cat_event = CategorizedEvents.objects.all().filter(event_id = event_id)
        print(cat_event)
        cat_id = cat_event[0].category_id
        top_id = cat_event[0].topic_id

        topic = Topics.objects.all().filter(topics_id = top_id)
        category = Categories.objects.all().filter(category_id = cat_id)

        main_category = category[0].category
        print(main_category)
        sub_category=''
        if len(topic)!=0:
            sub_category = topic[0].topic
        elif len(topic)==0:
            sub_category = " "
        print(sub_category)
        cat = (main_category,sub_category)

        #Tickets Tab--------------------------------------------------------
        free =False
        if s_p_tkt[0].ticketing == 0:
            free = True

        tkts = Tickets.objects.all().filter(event_id = event_id)
        print(tkts)
        tkt_name = []
        tkt_price = []
        oth_chrgs = []
        oth_chrgs_type =[]
        tkt_qty = []
        min_qty = []
        max_qty = []
        tkt_left = []
        tkt_msg = []
        s_date = []
        e_date = []
        e_fee = []
        trans_fee = []
        tkt_lbl = []
        activ = []

        for i in tkts:
            tkt_name.append(i.ticket_name)
            tkt_price.append(i.ticket_price)
            oth_chrgs.append(i.other_charges)
            oth_chrgs_type.append(i.other_charges_type)
            tkt_qty.append(i.ticket_qty)
            min_qty.append(i.min_qty)
            max_qty.append(i.max_qty)
            tkt_left.append(i.qty_left)
            tkt_msg.append(i.ticket_msg)
            s_date.append(i.ticket_start_date)
            e_date.append(i.expiry_date)
            e_fee.append(i.ercess_fee)
            trans_fee.append(i.transaction_fee)
            tkt_lbl.append(i.ticket_label)
            activ.append(i.active)
        print(oth_chrgs)
        print("message-------------")
        print(tkt_msg)
        msg1=[]
        for i in tkt_msg:
            if (i == None or i == "" or i =="None" or i == "NULL" or i == "none"):
                msg1.append(0)
            else:
                msg1.append(i)
        print(msg1)
        print("message code------------------ends")
        oth_chrgs2=[]
        for i in oth_chrgs:
            if i == '':
                oth_chrgs2.append(0)
            else:
                oth_chrgs2.append(i)
        print(oth_chrgs2)

        print(oth_chrgs_type)
        oth_chrgs_type2=[]
        for i in oth_chrgs_type:
            if i == 0:
                oth_chrgs_type2.append(0)
            elif i == 1:
                oth_chrgs_type2.append(1)
            elif i == 2 :
                oth_chrgs_type2.append(2)
        print(oth_chrgs_type2)

        print(activ)
        activ2=[]
        for i in activ:
            if i == 0:
                activ2.append('inactive')
            elif i == 1:
                activ2.append('active')
            elif i == 2:
                activ2.append("deleted")
        print(activ2)
        print(country)

        currency = AboutCountries.objects.all().filter(country= country).values('currency')
        print(currency)
        currency = currency[0]['currency']
        print(currency)

        print("Question tab---------------------------")
        # Question Tab
        builder = AttendeeFormBuilder.objects.all().filter(event_id=event_id)
        print(builder)
        title = []
        mand = []
        q_type = []
        q_id = []
        if len(builder) != 0:
            for i in builder:
                title.append(i.ques_title)
                mand.append(i.ques_accessibility)
                q_type.append(i.ques_type)
                q_id.append(i.ques_id)
        print(title)

        print(mand)

        name = []
        type_id = []
        for i in q_type:
            form_type = AttendeeFormTypes.objects.all().filter(type_id=i)
            name.append(form_type[0].name)
            type_id.append(form_type[0].type_id)
        print(name)

        optn_name = []
        for i in q_id:
            form_option = AttendeeFormOptions.objects.all().filter(ques_id=i)
            if len(form_option) != 0:
                if form_option[0].event_id == event_id:
                    optn_name.append(form_option[0].option_name)
                else:
                    optn_name.append(" ")
            else:
                optn_name.append(" ")
        print(optn_name)

        x = zip(title, mand, name, optn_name)

        items = zip(tkt_name, tkt_price, oth_chrgs2,
                    oth_chrgs_type2, tkt_qty, min_qty,
                    max_qty, tkt_left, msg1, s_date, e_date,
                    e_fee, trans_fee, tkt_lbl, activ2)

        #################     for fail errors   #####################
        print("Fail errors---------------------------")
        veri_res = EventVerificationResult.objects.all().filter(event_id=event_id)
        print(veri_res.values('event_id'))
        veri_id = []
        pass_id =[]
        if len(veri_res) != 0:
            for i in veri_res:
                if i.status == 'fail':
                    veri_id.append(i.verified_against)
                elif i.status == 'pass':
                    pass_id.append(i.verified_against)
        veri_count = len(veri_id)
        pass_count = len(pass_id)

        print(veri_id)
        print(pass_id)
        msg_to_org = []
        for i in veri_id:
            process = EventProcesses.objects.all().filter(process_id=i)
            msg_to_org.append(process[0].msg_to_org)
        msg_to_org_pass =[]
        for i in pass_id:
            process= EventProcesses.objects.all().filter(process_id=i)
            msg_to_org_pass.append(process[0].msg_to_org)
        print(msg_to_org)
        print("-------------------------fail errors")

        ###################################### for sales box    ##################################
        sales = TicketsSale.objects.all().filter(event_id=event_id)
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
        contact = []
        email = []
        recieve = []
        forward = []

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
                contact.append(i.attendee_contact)
                email.append(i.attendee_email)



        details = zip(tkt_type, tkt_book_id, tkt_amt, tkt_qty, tkt_p_date, tkt_s_site, tkt_atendee,contact
                      ,email)

        ##########################  RSVP  BOX    ############################################

        name_r = []
        cont = []
        email = []
        e_r = Rsvp.objects.all().filter(event_id=event_id).order_by('-date_added').values('table_id')
        for i in range(0, len(e_r)):
            d = Rsvp.objects.all().filter(table_id=e_r[i]['table_id'])
            name_r.append(d.values('attendee_name')[0]['attendee_name'])
            cont.append(d.values('attendee_contact')[0]['attendee_contact'])
            email.append(d.values('attendee_email')[0]['attendee_email'])

        rsvp_d = zip(name_r, cont, email)
        c_r = [len(e_r)]

    #######################################     SITE   TABLE   ######################################

        s_n = []
        c_l = []
        c_ps = []
        c_p = []

        s = EventStatusOnChannel.objects.all().filter(event_id=event_id).values('table_id')
        s_len = len(s)
        print(s)
        for i in s:
            d = EventStatusOnChannel.objects.all().filter(table_id=i['table_id'])
            s_i = PartnerSites.objects.all().filter(table_id=(d.values('site_id')[0]['site_id']))
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


        ''' Status promotion ticket table , fetching approval of event '''

        status = StatusPromotionTicketing.objects.get(event_id = event_id)



        return Response({'id':id,'form':form,'article': article,'cat':cat,'images':images,'detail':details,'rsvp':rsvp_d,
                         'c_r':c_r,'site':site,'s_len':s_len,'website':website,
                         'types':types ,'currency':currency,'free':free,
                         'tkt_typ':tkt_typ,'items':items,'x':x,'fail':msg_to_org,'pass':msg_to_org_pass, 'status':status})

    def post(self,request ,event_id):
        if 'admin_id' not in request.session.keys():
            return redirect('/admin-site/login')
        time = timezone.now()
        status = False
        if request.method == 'POST':
            form = EditForm(request.POST)
            if form.is_valid():
                name = request.POST.get('website_name')
                link = request.POST.get('link')
                prom = request.POST.get('promotion_status')
                part = request.POST.get('partner_status')

                print(name)
                print(prom)
                print(part)

                eve_channel = EventStatusOnChannel.objects.all().filter(event_id=event_id, site_id=name)
                if len(eve_channel) != 0:
                    ############################  UPDATING THE ROW   ######################################

                    print(eve_channel)
                    print(eve_channel[0].promotion_status)
                    print(eve_channel[0].partner_status)
                    eve_channel[0].promotion_status = prom
                    eve_channel[0].partner_status = part
                    eve_channel[0].link = link
                    eve_channel[0].last_updated = time
                    print("new----------")
                    print(eve_channel[0].promotion_status)
                    print(eve_channel[0].partner_status)
                    eve_channel[0].save()
                    status = True
                else:
                    ################################     NEW ROW CREATING    ##################################

                    eve_c = EventStatusOnChannel()
                    eve_c.event_id = event_id
                    eve_c.last_updated = time
                    eve_c.site_id = name
                    eve_c.admin_id = request.session['admin_id']
                    eve_c.link = link
                    eve_c.promotion_status = prom
                    eve_c.partner_status = part
                    eve_c.save()
                    status = True

                #########################  SAVING ADMIN ACTION LOG   ########################################

                action = AdminActionLog()
                action.admin_id = request.session['admin_id']
                action.timestamp = time
                action.parameter = "promotion link"
                action.event_id = event_id
                p = PartnerSites.objects.get(table_id=name)
                print(p)
                action.action_taken = "updated the details of " + p.site_name
                action.save()

                return redirect('admin-panel:details',event_id=event_id)
            else:
                status=False
                messages.error(request,"Something went wrong")




def promotionUpcoming(request):
    if 'admin_id' not in request.session.keys():
        return redirect('/admin-site/login')

    app_stat = StatusPromotionTicketing.objects.all().order_by('-event_id')

    time = timezone.now()
        #############   ALL EVENTS   ###############
    print("ALL    ----------------------------------")
    print(app_stat)
    app_id = []

    for i in app_stat:
        event = Articles2.objects.all().filter(id=i.event_id)


        if len(event) != 0:
            if event[0].edate >= time:
                app_id.append(event[0].id)
    print(app_id)

    eve_id =[]
    eve_name = []
    site_name = []
    link = []
    prom_stat = []
    partner = []

    for i in app_id:
        status = EventStatusOnChannel.objects.all().filter(event_id=i)

        for i in status:
            event2= Articles2.objects.all().filter(id = i.event_id)
            site = PartnerSites.objects.all().filter(table_id=i.site_id)
            if len(event2)!=0:
                eve_id.append(i.event_id)
                eve_name.append(event2[0].event_name)
                site_name.append(site[0].site_name)
                link.append(i.link)
                prom_stat.append(i.promotion_status)
                partner.append(i.partner_status)
    print(eve_id)
    print(eve_name)
    print(len(eve_id),len(eve_name), len(site_name), len(link), len(prom_stat), len(partner))

    up =zip(eve_id,eve_name,site_name,link,prom_stat,partner)
    return render(request,'admin_panel/prom_upcoming.html',{'up':up})


def promotionPast(request):
    if 'admin_id' not in request.session.keys():
        return redirect('/admin-site/login')
    app_stat = StatusPromotionTicketing.objects.all().order_by('-event_id')

    print(request.session['fname'])

    time = timezone.now()

    #############   ALL EVENTS   ###############
    print("ALL    ----------------------------------")
    print(app_stat)
    app_id = []

    for i in app_stat:
        event = Articles2.objects.all().filter(id=i.event_id)

        if len(event) != 0:
            if event[0].edate < time:
                app_id.append(event[0].id)
    print(app_id)

    eve_id = []
    eve_name = []
    site_name = []
    link = []
    prom_stat = []
    partner = []

    for i in app_id:
        status = EventStatusOnChannel.objects.all().filter(event_id=i)

        for i in status:
            event2 = Articles2.objects.all().filter(id=i.event_id)
            site = PartnerSites.objects.all().filter(table_id=i.site_id)
            if len(event2) != 0:
                eve_id.append(i.event_id)
                eve_name.append(event2[0].event_name)
                site_name.append(site[0].site_name)
                link.append(i.link)
                prom_stat.append(i.promotion_status)
                partner.append(i.partner_status)
    print(eve_id)
    print(eve_name)
    print(len(eve_id), len(eve_name), len(site_name), len(link), len(prom_stat), len(partner))

    past = zip(eve_id, eve_name, site_name, link, prom_stat, partner)

    return render(request,'admin_panel/prom_past.html',{'past':past})


def partner_sites(request):
    if 'admin_id' not in request.session.keys():
        return redirect('/admin-site/login')

    all = PartnerSites.objects.all()

    partners_site = []
    for i in all:
        partners_site.append(i)

    acount = 0
    dcount = 0
    for i in partners_site:
        if i.active_state == 1:
            acount+=1
        else:
            dcount +=1

    return render(request, 'admin_panel/partnersites.html', {'partners_site':partners_site, 'acount':acount, 'dcount':dcount} )

def user_detail(request):
    if 'admin_id' not in request.session.keys():
        return redirect('/admin-site/login')

    users = Users.objects.all()

    user= []

    for i in users:
        user.append(i)
    no_of_user = len(user)

    return render(request, 'admin_panel/users_detail.html', {'users': user, 'no_of_user':no_of_user})


def add_rsvp(request, event_id):
    if 'admin_id' not in request.session.keys():
        return redirect('/admin-site/login')

    if request.method == 'POST':
        form = AddRsvpForm(request.POST)
        if form.is_valid():
            sitename = form.cleaned_data['sitename']
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            number = form.cleaned_data['number']





            rsvp_var = rsvp()
            print(rsvp)

            rsvp_var.date_added = datetime.now()
            rsvp_var.event_id = event_id
            rsvp_var.uniq_id = 'EL' + str(event_id)
            rsvp_var.supplied_by = sitename
            rsvp_var.attendee_name = name
            rsvp_var.attendee_contact = number
            rsvp_var.attendee_email = email
            print(rsvp_var.uniq_id)
            rsvp_var.save()


            id = rsvp.objects.latest('table_id')
            print('this is the latest id',id)

            admin_log = AdminActionLog()

            print(admin_log)
            print(AdminActionLog)
            # print('######################################### object created')
            admin_log.admin_id = request.session['admin_id']
            print('######################################################################################')
            admin_log.timestamp = timezone.now()
            admin_log.parameter = 'Added RSVP'
            admin_log.event_id = event_id
            print(rsvp_var.table_id)
            admin_log.action_taken = "Added RSVP at id"+' '+str(rsvp_var.table_id)

            #This is last inserted id
            print(type(admin_log.action_taken))
            print(admin_log.admin_id , admin_log.timestamp, admin_log.parameter, admin_log.event_id,  admin_log.action_taken)
            admin_log.save()

            print('successfully data added in ADMINACTIONLOG')



            # connected user

            con_user = []
            for i in StatusPromotionTicketing.objects.all().filter(event_id= event_id):
                con_user.append(i)

            print(con_user)
            connected_user = 0
            for i in con_user:
                connected_user = i.connected_user
            print('connected user no',connected_user)

            users = Users.objects.all().filter(id=connected_user)
            print(users)
            mail = ''
            for j in users:
                mail = j.user

            print('mail is ',mail)

            article = Articles2.objects.all().filter(id = event_id)

            event = ''

            for i in article:
                event = i.event_name

            print(event)


            subject = sitename
            message = 'Get in touch with the person by just replying to this email'

            html_message = render_to_string('static/common/Add_rsvp_confirmation.html',
                                                   {
                                                       'name': name,
                                                       'number': number,
                                                       'email': email,
                                                       'message':message,
                                                       'event':event
                                                   })



            email_from = 'info@ercess.com'
            recipient_list = [mail]
            headers ={'Reply-To':email}

            # send_mail(subject, message, email_from, recipient_list,html_message=html_message)

            msg = EmailMessage(subject,html_message, email_from, recipient_list, headers={'Reply-To':email})
            msg.content_subtype = "html"

            msg.send(fail_silently=False)
            print('mail is send to your account')

            return redirect('admin-panel:details',event_id)


    else:
        form = AddRsvpForm()

    return render(request, 'admin_panel/add_rsvp.html', {'form': form})



def add_sales(request, event_id):

    if 'admin_id' not in request.session.keys():
        return redirect('/admin-site/login')

    if request.method == 'POST':
        form = AddSalesDetailsForm(request.POST)
        if form.is_valid():
            ticket_name = form.cleaned_data['ticket_name']
            booking_id = form.cleaned_data['booking_id']
            purchase_date_time = form.cleaned_data['purchase_date_time']
            purchase_time = form.cleaned_data['purchase_time']
            amount_paid = form.cleaned_data['amount_paid']
            quantity = form.cleaned_data['quantity']
            attendee_name = form.cleaned_data['attendee_name']
            attendee_contact_number = form.cleaned_data['attendee_contact_number']
            attendee_email_id = form.cleaned_data['attendee_email_id']
            website_name = form.cleaned_data['websitename']
            try:
                ticket = Tickets.objects.all().filter(event_id=event_id)
                eid = 0
                ticketid = 0
                for i in ticket:
                    eid = i.event_id
                    ticketid = i.tickets_id
            except Tickets.DoesNotExist:
                 raise Http404


            print(eid, ticketid)

            #connected user from status promotion ticketing table
            try:
                statusPromotions = StatusPromotionTicketing.objects.all().filter(event_id= event_id)

                connecteduser = 0
                for i in statusPromotions:
                    connecteduser = i.connected_user
            except StatusPromotionTicketing.DoesNotExist:
                raise Http404

            # email id of connected user from user table
            try:
                users = Users.objects.all().filter(id=249)
                user_mail = ''
                organization_name = str()
                contact_number = str()

                for i in users:
                    user_mail = i.user
                    organization_name = i.organization_name
                    contact_number = i.mobile



            except Users.DoesNotExist:
                raise Http404

            print('print user mail',user_mail)
            date = str(purchase_date_time)
            # print('date',purchase_date_time)
            # print('time',purchase_time)
            time = str(purchase_time)
            date = date[:-15]
            # print(date)

            new_date_time=str(date)+' ' +time

            # print('#########################', type(new_date_time),new_date_time)
            if (new_date_time != None and new_date_time != ''):
                print('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA',new_date_time)
                date_object = None
            else:
                print('BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB')
                date_object = datetime.strptime(new_date_time, "%Y-%m-%d %H:%M:%S")
            print(date_object, type(date_object))

            # ticketsale = Tickets_Sale()
            ticketsale = TicketsSale()


            ticketsale.event_id = eid
            ticketsale.ticket_id = ticketid
            ticketsale.oragnizer = connecteduser
            ticketsale.ticket_type = ticket_name
            ticketsale.booking_id = booking_id
            ticketsale.purchase_date = date_object
            ticketsale.ampunt_paid = amount_paid
            ticketsale.qty = quantity
            ticketsale.attendee_name = attendee_name
            ticketsale.attendee_contact = attendee_contact_number
            ticketsale.attendee_email = attendee_email_id
            ticketsale.seller_site = website_name
            ticketsale.ticket_handover = 'mail sent'
            ticketsale.save()



            ''' payment table data are adding here '''
            eve = TicketsSale.objects.all().filter(event_id=event_id)
            amountpaid = float()
            ticket_sale_id = str()
            for i in eve:
                ticket_sale_id = i.table_id
                amountpaid = i.ampunt_paid

            # print('type of amount ', amountpaid, type(amountpaid))

            partner_site = PartnerSites.objects.all().filter(site_name = website_name)

            negotiated_convenience_fees = float()
            negotiated_transaction_fees = float()
            negotiated_tax_charges = float()
            negotiated_flat_charges = float()


            for data in partner_site:
                partner_id = data.table_id
                if data.negotiated_transaction_fee == '':
                    negotiated_transaction_fees = 0.0
                else:
                    negotiated_transaction_fees = float(data.negotiated_transaction_fee)

                if data.negotiated_convenience_fee == '':
                    negotiated_convenience_fees = 0.0

                else:
                    negotiated_convenience_fees = float(data.negotiated_convenience_fee)

                if data.negotiated_flat_charges == '':
                    negotiated_flat_charges = 0.0
                else:
                    negotiated_flat_charges = float(data.negotiated_flat_charges)

                if data.negotiated_tax_charges == '':
                    negotiated_tax_charges = 0.0

                else:
                    negotiated_tax_charges = float(data.negotiated_tax_charges)
            sum_in_percentage = negotiated_convenience_fees + negotiated_transaction_fees + negotiated_tax_charges
            print(amountpaid, ' >> << ',sum_in_percentage)
            if (amountpaid != None and amountpaid != ''):
                deduct_sum_percentage = amountpaid - (amountpaid*sum_in_percentage/100)
                expected_amnt_partner = deduct_sum_percentage - negotiated_flat_charges
                # @author Shubham
                expected_amnt_partner = round(expected_amnt_partner, 2)
                # ends here ~ @author Shubham
            else:
                expected_amnt_partner = None

            payment_table = PaymentSettlement()
            payment_table.date_added = datetime.now()
            payment_table.date_modified = datetime.now()
            payment_table.booking_id = booking_id
            payment_table.ticket_sale_id = ticket_sale_id
            payment_table.added_by = request.session['admin_id']
            payment_table.modified_by = request.session['admin_id']
            payment_table.receival_status = 'pending'
            payment_table.expected_amnt_partner = expected_amnt_partner
            payment_table.rcvd_amnt_partner = 0
            payment_table.receival_date = None
            payment_table.receival_invoice = ''
            payment_table.partner_dispute = ''
            payment_table.process_status = 'pending'
            payment_table.amount_processed = 0
            payment_table.process_date = None
            payment_table.organizer_dispute = ''
            payment_table.save()

            event_table = Articles2.objects.get(id = event_id)
            event_name = str()
            location = str()



            event_name = event_table.event_name
            location = event_table.full_address


            subject = 'Confirmation'
            message = 'You purchase the ticket'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [user_mail, 'track@ercess.com']
            # headers = {'Reply-To': attendee_email_id}

            # send_mail(subject, message, email_from, recipient_list)

            html_message = render_to_string('static/common/new_sales_to_organizers.html',
                                            {
                                                'event_name': event_name,
                                                'revenue': amount_paid,
                                                'sold': quantity,
                                                'name': attendee_name,
                                                'contactnumber': attendee_contact_number,
                                                'email': attendee_email_id,
                                                'booking_id': booking_id,
                                                'ticket_name': ticket_name
                                            })

            msg = EmailMessage(subject, html_message, email_from, recipient_list, headers={'Reply-To': attendee_email_id})
            msg.content_subtype = "html"
            msg.send(fail_silently=False)

            subject = 'Confirmation'
            # email_from = 'info@ercess.com'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [attendee_email_id, 'track@ercess.com']
            html_message = render_to_string('static/common/PURCHASE_CONFIRMATION.html',
                                            {
                                                'event_name': event_name,
                                                'amount_paid': expected_amnt_partner,
                                                'sold': quantity,
                                                'name': attendee_name,
                                                'contactnumber': attendee_contact_number,
                                                'email':attendee_email_id,
                                                'organizer_email': user_mail,
                                                'booking_id': booking_id,
                                                'organizer_name': organization_name,
                                                'organizer_location':location,
                                                'organization_contact_number':contact_number
                                            })
            msg = EmailMessage(subject, html_message, email_from, recipient_list, headers={'Reply-To': attendee_email_id})
            msg.content_subtype = "html"
            msg.send(fail_silently=False)
            return redirect('admin-panel:details', event_id)



    else:
        # @author Shubham
        form = AddSalesDetailsForm(event_id = event_id)
        # ends here ~ @author Shubham


    return render(request, 'admin_panel/add_sales.html',{'form': form})

class sale_settled(View):
    def get(self,request):
        if 'admin_id' not in request.session.keys():
            return redirect('/admin-site/login')

        ''' model is used to fetch the event Name '''
        ticketsale = TicketsSale.objects.all().order_by('purchase_date')
        booking_id = list()
        amount_paid = list()
        purchase_date = list()
        attendee_name = list()
        event_id = list()
        table_id = list()
        payment_receival = list()
        payment_process =list()
        for ticket  in ticketsale:
            payment = PaymentSettlement.object.get(ticket_sale_id=ticket.table_id)
            if payment.receival_status == 'settled' and payment.process_status == 'settled':
                table_id.append(ticket.table_id)
                booking_id.append(ticket.booking_id)
                amount_paid.append(ticket.ampunt_paid)
                purchase_date.append(ticket.purchase_date)
                attendee_name.append(ticket.attendee_name)
                event_id.append(ticket.event_id)
                payment_receival.append(payment.receival_status)
                payment_process.append(payment.process_status)

        event_name = list()
        article_list = list()
        for id in event_id:
            article_list.append(Articles2.objects.get(id=id))


        for i in article_list:
            event_name.append(i.event_name)

        # print(article_list)
        sales = zip(booking_id, amount_paid, purchase_date, attendee_name,event_name,table_id,event_id,payment_receival,payment_process)

        return render(request, 'admin_panel/sale_settled.html',{'sales': sales})

class sale_pending(View):
    def get(self,request):
        if 'admin_id' not in request.session.keys():
            return redirect('/admin-site/login')

        ''' model is used to fetch the event Name '''
        ticketsale = TicketsSale.objects.all().order_by('purchase_date')
        booking_id = list()
        amount_paid = list()
        purchase_date = list()
        attendee_name = list()
        event_id = list()
        table_id = list()
        payment_receival = list()
        payment_process = list()
        for ticket  in ticketsale:
            payment = PaymentSettlement.object.get(ticket_sale_id=ticket.table_id)
            if payment.receival_status == 'pending' or payment.receival_status == 'settled' and payment.process_status == 'pending' :
                table_id.append(ticket.table_id)
                booking_id.append(ticket.booking_id)
                amount_paid.append(ticket.ampunt_paid)
                purchase_date.append(ticket.purchase_date)
                attendee_name.append(ticket.attendee_name)
                event_id.append(ticket.event_id)
                payment_receival.append(payment.receival_status)
                payment_process.append(payment.process_status)

        event_name = list()
        article_list = list()
        for id in event_id:
            article_list.append(Articles2.objects.get(id=id))


        for i in article_list:
             event_name.append(i.event_name)
        # print(event_id)

        # print(article_list)
        # print(event_name)
        sales = zip(booking_id, amount_paid, purchase_date, attendee_name,event_name,table_id,event_id,payment_receival,payment_process)

        return render(request, 'admin_panel/sale_pending.html',{'sales': sales})


def sale_details(request,table_id):
    sales = TicketsSale.objects.get(table_id=table_id)
    payment = PaymentSettlement.object.get(ticket_sale_id = table_id)
    receival_status = payment.receival_status
    process_status = payment.process_status
    return render(request,'admin_panel/sale-details.html',{'sales':sales, 'payment':payment})


def booking_details(request,booking_id):
    tickets_sale=TicketsSale.objects.get(booking_id=booking_id)
    payment_settlement_table=PaymentSettlement.object.get(booking_id=booking_id)
    event_id = tickets_sale.event_id
    status = StatusPromotionTicketing.objects.get(event_id=tickets_sale.event_id)
    user_id = status.connected_user
    bankdetails = BankDetails.objects.get(user_id=user_id)
    if bankdetails is not None:
        try:
            user=Users.objects.get(id=user_id)
            content={
            'tickets_sale':tickets_sale,
            'payment_settlement':payment_settlement_table,
            'name':user.user,
            'event_id':event_id,
            'bankdetails':bankdetails
            }
            return render(request, 'admin_panel/event-details-page.html', content)
        except Users.DoesNotExist:
            print('no user exist')
    # if user bank details are missing
    content={
    'tickets_sale':tickets_sale,
    'payment_settlement':payment_settlement_table,
    'event_id': event_id
        }
    return render(request,'admin_panel/event-details-page.html',content)


def partner_site_details(request,table_id):
    if 'admin_id' not in request.session.keys():
        return redirect('/admin-site/login')

    partner = PartnerSites.objects.get(table_id=table_id)
    #########################################
    """  partner's category """
    try:
        partners_site=ErcessPartnersCategories.objects.get(table_id=table_id)
    except ObjectDoesNotExist:
        partners_site=0

    ##########################################
    """ partner's curencies """
    try:
        currency=PartnerCurrencies.objects.get(table_id=table_id)
    except ObjectDoesNotExist:
        currency=0
    ############################################
    """ Indiave states ercess """
    # try:
    #     states=ErcessIndiaeveStates.objects.get(table_id=table_id)
    # except ObjectDoesNotExist:
    #     states=0
    ##############################################
    """ TimeZones """
    if currency!=0:
        try:
            timezones=PartnerTimezones.objects.filter(partner_id=currency.partner_id)
        except ObjectDoesNotExist:
            timezones=0
        timez=[]
        if timezones:
            if len(timezones)>1:
                for time in timezones:
                    timez.append(time.timezone)
                timezone=', '.join(timez)
            else:
                timezone=timezones[0].timezone
    else:
        timezone=''
    ##############################################
    """ ercess other mappings """
    ercess_other=0
    try:
        ercess_other=ErcessOtherMappings.objects.get(table_id=table_id)
    except ObjectDoesNotExist:
        ercess_other=0
    ##############################################
    """ partner's subcategories """
    partner_sub=[]
    try:
        sub=ErcessPartnersSubcategories.objects.all()
        partner_sub.append(sub)
    except ObjectDoesNotExist:
        partner_sub.append('')

    return render(request,'admin_panel/partner-sites-details.html',{'partners_site':partner,'partner_cat':partners_site,\
    'currency':currency,'ercess_other':ercess_other,'timezone':timezone})

# class UserRegister(generic.View):

#     form_class = AddUserForm
#     template_name = 'admin_panel/add_user.html'

#     def get(self,request):
#         form = self.form_class(None)
#         return render(request,self.template_name,{'form':form})



#     def post(self,request):
#         form = self.form_class(request.POST)

#         if form.is_valid():
#             post = form.save(commit = False)

#             st = post.email
#             h = hashlib.md5(st.encode())
#             post.md5 = h.hexdigest()


#             alpha = string.ascii_letters + string.digits
#             passw = ''.join(random.choice(alpha) for i in range(8))
#             x = hashlib.md5(passw.encode())
#             post.password = x.hexdigest()

#             subject = "Thanks for registration"
#             text_content = "Hi {}, you have successfully registered.Here is your login password - {}".format(post.first_name,passw)
#             from_mail = settings.EMAIL_HOST_USER
#             to = post.email


#             msg = EmailMultiAlternatives(subject, text_content, from_mail, [to],cc = ["track@ercess.com"] )
#             msg.send(fail_silently=True)

#             post.save()



#         return render(request,self.template_name,{'form':form})
