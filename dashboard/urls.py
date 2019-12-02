from django.urls import path, include
from django.conf.urls import  url
from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles.urls import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.views.generic import TemplateView

from Ercesscorp.third_party_security import smartlogin
from Ercesscorp import views
from Ercesscorp.views import edit_event,step_three,edit_event_two,edit_event_four,edit_event_five,edit_action_four,edit_action_four,edit_action_five,new_ticket
from dashboard.views import  getHow, change_password #, third_step#,photo_list ,fourth_step
from .api.views import ( ArticlesCreateAPIView, CategoryCreateAPIView,
                        TopicsListAPIView, DescriptionCreateAPIView,
                        ThirdStepTemp, QuestionCreateAPIView,
                        CreateTicketsView, BankDetailsView, EditBankDetailsView)

from .views import  EditDetailView


app_name = 'dashboard'

urlpatterns = [
    url(r'^$', getHow, name='how'),
    path('add-event', ArticlesCreateAPIView.as_view(), name="step_one"),
    path('add-event-types/<str:md5>/<int:event_id>', CategoryCreateAPIView.as_view(), name="step_two"),
    path('add-event-images/<str:md5>/<int:event_id>', views.step_three, name="step_three"),
    # path('add-event-images-action/<str:md5>/<int:event_id>', views.step_three_action, name="step_three_action"),
    path('ajax/topics', TopicsListAPIView.as_view()),
    path('add-event-description/<str:md5>/<int:event_id>', DescriptionCreateAPIView.as_view(), name="step_four"),
    path('add-event-tickets/<str:md5>/<int:event_id>', CreateTicketsView.as_view(), name="step_five"),
    path('add-event-question/<str:md5>/<int:event_id>', QuestionCreateAPIView.as_view(), name="step_six"),
    path('event_added', TemplateView.as_view(template_name='dashboard/event_success.html'), name='event_added'),
    path('RSVP',views.RSVP,name='leads'),
    path('updateContact/',views.updateMobileNo, name="updateContact"),
    path('rsvp/<int:event_id>',views.rsvp_event,name='rsvp-event'),
    path('organizer_dashboard',views.manageevents, name='organizer-dashboard'),
    path('event-details/<int:event_id>',views.event_details, name='event-details'),
    path('sales', views.getSales, name='sales'),
    path('sales_details/<int:event_id>/',views.getSalesDetails, name ='sale_details'),
    path('inquiries', views.getInquiries, name='inquiries'),
    path('help',views.getHelp,name='help'),
    path('profile',views.profile,name='profile'),
    path('settings', change_password,name='settings'),
    path('legal',views.legal,name='legal'),
    path('organizer-agreement',views.organizer_agreement,name='organizer-agreement'),
    path('bank-details',BankDetailsView.as_view(), name="bank_details"),
    path('create-stalls',views.create_stall, name="create_stall"),
    path('edit-event/<int:event_id>', EditDetailView.as_view(), name="detail"),
    path('boost-event/<int:event_id>', views.boost, name="boost-event"),
    path('edit-event/basic/<int:event_id>',views.edit_event, name='edit-event'),
    path('edit-event-two/<int:event_id>',views.edit_event_two, name='edit-event-two'),
    # path('edit-event-three/<int:event_id>',views.edit_event_three, name='edit-event-three'),
    path('edit-event-four/<int:event_id>',views.edit_event_four, name='edit-event-four'),
    path('edit-event-five/<int:event_id>/<int:ticket_id>',views.edit_event_five, name='edit-event-five'),
    path('edit_event_ticket/<event_id>',views.edit_event_ticket, name='edit-event-ticket'),
    path('new_ticket/<int:event_id>',views.new_ticket, name='new-ticket'),
    path('edit_action_two/<event_id>',views.edit_action_two, name='edit-action-two'),
    path('edit_action_five/<event_id>/<int:ticket_id>',views.edit_action_five, name='edit-action-five'),
    path('edit_action_four/<event_id>',views.edit_action_four, name='edit-action-four'),
    path('delete_ticket/<str:md5>/<int:event_id>/<int:ticket_id>/<int:return_page>',views.delete_ticket, name='delete-ticket'),
    path('update_event_tickets/<str:md5>/<int:event_id>/<int:ticket_id>',views.update_event_tickets, name='update-event-tickets'),
    path('edit_event_three/<int:event_id>',views.edit_event_three, name='edit-event-three'),
    path('edit-bank-details',EditBankDetailsView.as_view(), name="edit_bank_details"),

    # path('edit-event-five/<int:event_id>/<int:ticket_id>/<str:md5>/<int:return_page>',views.edit_event_five, name='edit-event-five'),
    
    # path('delete_ticket/<int:event_id>/<int:ticket_id>',views.delete_ticket, name='delete-ticket'),



    #path('legal',views.legal,name='legal'),
    #url(r'create-event/step-three/(?P<eventid>[0-9]+)$',login_required(third_step),name='third-step'),
    #url(r'test$',photo_list),
    #url(r'create-event/step-four/$',login_required(fourth_step),name='fourth-step')
    # url(r'^home',home,name='home'),

    # url(r'^live/dashboard/organizer_dashboard',views.manageevents),
    # url(r'^live/dashboard/sales',views.salesreport),

    #path('boost_event/<int:event_id>',views.boost,name='boost-event'),
]
urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
