from django import forms
from django.core.validators import ValidationError
from dashboard.models import PartnerSites, Tickets, TicketsSale
# from admin_panel.models import AddUser,choice
from admin_panel.models import choice

class LoginForm(forms.Form):
    email= forms.EmailField(label='Email',
        widget=forms.EmailInput(
            attrs={'class':'',
                   'placeholder':'Admin Email *'
                   }

        )
    )

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class':'',
                   'placeholder':'Password *'}
        )
    )

    def clean_email(self):
        mail = self.cleaned_data['email']
        if len(mail)==0:
            raise ValidationError('Enter your Email')

    def clean_password(self):
        password = self.cleaned_data['password']
        if len(password)==0:
            raise ValidationError('Enter our Password')


class EditForm(forms.Form):
    partner = PartnerSites.objects.all().order_by('table_id')
    # print(partner)
    websites = []
    for x in partner:
        websites.append((x.table_id,x.site_name))
    print(websites)

    status = [('pending','Pending'),
              ('published','Published'),
              ('ready to upload','Ready to upload'),
              ('already published','Already published'),
              ('uploaded','Uploaded but not published')]

    p_status = [('approved','Approved'),
                ('pending','Pending'),
                ('rejected','Rejected')]

    website_name = forms.CharField(widget=forms.Select(choices=websites))
    link = forms.URLField(required=False,widget=forms.URLInput(attrs={'class':''}))
    promotion_status = forms.CharField(widget=forms.Select(choices=status))
    partner_status = forms.CharField(widget=forms.Select(choices=p_status))

    def clean_link(self):
        link = self.cleaned_data['link']
        if not "https://" in link:
            return "https://"+ link
        else:
            return link


class AddRsvpForm(forms.Form):
    partner_sites = PartnerSites.objects.filter(active_state=1)
    sites = []

    for i in partner_sites:
        sites.append((i.site_name, i.site_name))

    sitename = forms.CharField(widget=forms.Select(choices=sites))

    name = forms.CharField(max_length=30,label='Name',
                    widget=forms.TextInput(attrs={'placeholder': 'Name*'}))
    email = forms.EmailField(label='Email',
        widget=forms.EmailInput(
            attrs={'class':'',
                   'placeholder':'Email *'
                   }
        ))
    number = forms.IntegerField(widget=forms.NumberInput(
            attrs={'class':'',
                   'placeholder':'Contact Number *'
                   }
        ))

class AddSalesDetailsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.event_id = kwargs.pop('event_id', None)
        super(AddSalesDetailsForm, self).__init__(*args, **kwargs)

        tickets = Tickets.objects.all().filter(event_id=self.event_id)
        t_name = []
        print(tickets)

        for i in tickets:
            t_name.append((i.ticket_name,i.ticket_name))
        self.fields['ticket_name'].widget  = forms.Select(choices=t_name)

    partner_site = PartnerSites.objects.all()
    website_name = []

    for i in partner_site:
        website_name.append((i.site_name, i.site_name))

    ticket_name = forms.CharField()

    booking_id = forms.CharField(required=False, max_length=25, label='Booking id',
                    widget=forms.TextInput(attrs={'placeholder': 'Booking id'}))
    purchase_date_time = forms.DateTimeField(required=False, widget=forms.DateTimeInput(attrs={'type': 'date'}))
    purchase_time = forms.TimeField(required=False, widget=forms.TimeInput(format='%H:%M',attrs={'type':'time'}))
    amount_paid = forms.FloatField(required=False, widget=forms.NumberInput(attrs={'placeholder*': 'Amount*'}))
    quantity = forms.IntegerField(required=False, widget=forms.NumberInput(
            attrs={'class':'',
                   'placeholder':'Quantity'
                   }
        ))
    attendee_name = forms.CharField(required=False, max_length=25, widget=forms.TextInput(attrs={'placeholder': 'Attendee Name*'}))
    attendee_contact_number = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'placeholder':'contact number*'}))
    attendee_email_id = forms.EmailField(required=False, label='Email', widget=forms.EmailInput(attrs={'placeholder': 'attendee email*'}))
    websitename = forms.CharField(required=False, widget=forms.Select(choices= website_name))

# class AddUserForm(forms.ModelForm):
#     gender = forms.ChoiceField(choices = choice)
#     alpha = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
#              'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N',
#              'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']


#     class Meta:
#         model = AddUser
#         fields = ['first_name','last_name','email','gender','location','mobile_no','organization']
#         widgets = {
#             'mobile_no': forms.TextInput(attrs = {'placeholder' : 'optional'}),
#             'organization': forms.TextInput(attrs = {'placeholder' : 'optional'}),
#             'email' : forms.TextInput(attrs = {'placeholder' : 'email'})
#         }


#     def clean_mobile_no(self):
#         sf = self.cleaned_data['mobile_no']

#         l = ['0','1','2','3','4','5','6','7','8','9']
#         if(sf is not None):
#             for i in range(len(sf)):
#                 if(sf[i] not in l):
#                     raise forms.ValidationError('Not a valid mobile no.')

#             if(len(sf) is not 10):
#                 raise forms.ValidationError('Mobile No should be 10 digits long')

#         return sf


#     def clean_first_name(self):
#         fname = self.cleaned_data['first_name']


#         for i in fname:
#             if (i not in self.alpha):
#                 raise forms.ValidationError('Please enter a valid name')


#         return fname


#     def clean_last_name(self):
#         lname = self.cleaned_data['last_name']

#         for i in lname:
#             if (i not in self.alpha):
#                 raise forms.ValidationError('Please enter a valid name')

#         return lname


#     def clean_location(self):
#         loca = self.cleaned_data['location']



#         for i in loca:
#             if (i not in self.alpha):
#                 raise forms.ValidationError('Please enter a valid location')

#         return loca


#     def clean_email(self):
#         mail = self.cleaned_data['email']


#         if AddUser.objects.filter(email = mail).exists():
#             raise forms.ValidationError('Email already exists')

#         return mail
