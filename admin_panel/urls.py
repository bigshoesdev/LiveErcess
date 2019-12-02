from django.urls import path
from admin_panel import views

app_name = 'admin-panel'

urlpatterns =[
    path('',views.admin_home,name = 'home'),
    #path('edit/<int:event_id>',views.editButton,name='edit'),
    path('event-lists/',views.eventList,name='eve_list'),
    path('past-event-lists/',views.pastEventList,name='past_list'),
    path('event-details/<int:event_id>',views.EventDetailView.as_view(),name='details'),
    path('event-promotion-upcoming/',views.promotionUpcoming,name='up_prom'),
    path('event-promotion-past/',views.promotionPast,name='past_prom'),
    path('login/',views.admin_login,name = 'admin_login'),
    path('partner-sites/', views.partner_sites, name = 'test'),
    path('user-detail/', views.user_detail, name = 'user-detail'),
    path('add-rsvp/<int:event_id>', views.add_rsvp, name = 'add-rsvp'),
    path('add-sales/<int:event_id>', views.add_sales, name='add-sales'),

    path('sale-settled/', views.sale_settled.as_view(), name ='sale-settled'),
    path('sale-pending/',views.sale_pending.as_view(),name = 'sale-pending'),
    path('sale-list/', views.sale_settled.as_view(), name ='sale-list'),
    path('sale-list/<int:table_id>', views.sale_details, name='sale-details'),

    path('booking_details/<int:booking_id>',views.booking_details,name='booking-details'),
    # path('sale-list/edit/<int:table_id>', views.edit_sales, name='sale-edit'),
    # path('sale-settled-edit/<int:pk>', views.Sale_Edit.as_view(), name='sale-details')
    path('sale-list/<int:table_id>', views.sale_details, name='sale-details'),
    path('sale-list/<str:booking_id>',views.booking_details,name='booking-details'),
    path('details-partner/<int:table_id>',views.partner_site_details,name='details-page'),
    # path('adduser/',views.UserRegister.as_view(),name = 'add'),

]
