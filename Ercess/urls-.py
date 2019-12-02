"""Ercess URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""



from django.contrib import admin
from django.conf.urls import  url
from Ercesscorp import  views
from django.urls import  path ,re_path ,include
from django.conf import settings
from django.contrib.staticfiles.urls import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from Ercesscorp.apiviews import *

# app_name = 'Ercess'
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^admin-site/',include('admin_panel.urls')),

    url(r'^$', views.home , name='home'),
    url(r'^accounts/login/$',views.loginview ,name='login'),
    url(r'^live/dashboard/', include('dashboard.urls')),
   # url(r'^live/dashboard/organizer_dashboard',views.manageevents),
    url(r'^home/$', views.home, name='home'),
    url(r'^live/$',views.home , name='home'),
    url(r'^live/verify_email/(?P<slug>[\w-]+)/$', views.verify_mail),
#    url(r'^live/verify_email/$', views.verify_mail, name='verify-email'),
    url(r'^live/forgot_password/$', views.forgotPassword, name='forgot-password'),
    url(r'^live/reset_password/(?P<slug>[\w-]+)/$', views.resetPassword),
    url(r'^live/set_new_password/$', views.setNewPassword),
#    url(r'^live/reset_password/$', views.resetPassword,name='reset-password'),
    url(r'^live/login/$', views.loginview, name='login'),
    url(r'^live/logout/$', views.logoutview, name='logout'),
    url(r'^live/signup/$', views.registration,name='signup'),
    url(r'^live/multichannel/$',views.multichannelpromotion,name='multichannel-promotion'),
    url(r'^live/sell-event-stalls/$',views.sellstallspaces, name='sell-event-stalls'),
    url(r'^live/paid-advertisement/$', views.advertisement,name='advertisement'),
    url(r'^live/how-it-works/$',views.howitworks, name='how-it-works'),
    url(r'^live/about/$',views.aboutus,name='about-us'),
    url(r'^live/contact/$',views.contactus,name='contact-us'),
    url(r'^live/blogs/$', views.blog, name='blog'),
    url(r'^live/blog-post/(?P<pk>[0-9]+)$', views.blogpost,name='blog-post'),
    url(r'^live/careers/$', views.career, name='careers'),
    url(r'^live/pricing/$', views.pricing, name='pricing'),
    url(r'^live/partners/$', views.partners, name='partners'),
    url(r'^live/privacy-policy/$', views.privacypolicy , name='privacy-policy'),
    url(r'^live/api/blogs/$' , BlogDetails.as_view(),name='blog-details'),
    url(r'^live/api/blogs/(?P<pk>[0-9]+)$', BlogSpecific.as_view(),name='blogspecific'),
    url(r'^live/api/users/$', Reg.as_view(),name='reg'),
    url(r'^live/api/login/$', LoginView.as_view(),'loginview'),
]

if settings.DEBUG:

    import debug_toolbar

    urlpatterns += [
        url(r'^_debug_/', include(debug_toolbar.urls)),
    ]
    #urlpatterns = [
    #   url(r'^__debug__/', include(debug_toolbar.urls)),
    #] + urlpatterns

    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
