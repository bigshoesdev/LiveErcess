from django import forms
from ckeditor.widgets import CKEditorWidget
from Ercesscorp.porter import HOW__CHOICES
from django import forms
from django.core.files import File
from .models import Articles2,BoostEvent #,Photo




class HowForm(forms.Form):

    choices =  forms.ChoiceField(choices=HOW__CHOICES)
    other =  forms.CharField(widget=forms.Textarea(
        attrs={
            # 'class': 'form-control',
            'placeholder': 'if Others fill this *'
        }
    ))


class Articles2Form(forms.ModelForm):
    description = forms.CharField(widget=CKEditorWidget())
    class Meta:
        model = Articles2
        fields = ('description',)

class BoostEventForm(forms.ModelForm):
    city=forms.CharField(max_length=500, widget=forms.TextInput(attrs={'id':"where_load",'class':"form-control form-control-lg"}))
    class Meta:
        model = BoostEvent
        fields = ['city',]


class ChangePasswordForm(forms.Form):
	oldpassword = forms.CharField(
			widget=forms.PasswordInput(

				attrs={
					'class': 'form-control',
					'placeholder': 'Your old Password *'

				}
			)
		)
	newpassword1 = forms.CharField(
        widget=forms.PasswordInput(

            attrs={
                'class': 'form-control',
                'placeholder': 'New Password *'

            }
        )
    )
	newpassword2 = forms.CharField(
        widget=forms.PasswordInput(

            attrs={
                'class': 'form-control',
                'placeholder': 'Confirm New Password *'

            }
        )
    )
	def clean(self):
            if len(self.cleaned_data['newpassword1'])<8:
                raise forms.ValidationError("New password is less than 8 characters")
            if self.cleaned_data['newpassword1'] != self.cleaned_data['newpassword2']:
                raise forms.ValidationError("The two password fields did not match.")
            return self.cleaned_data

'''
class PForm(forms.ModelForm):
    x = forms.FloatField(widget=forms.HiddenInput())
    y = forms.FloatField(widget=forms.HiddenInput())
    width = forms.FloatField(widget=forms.HiddenInput())
    height = forms.FloatField(widget=forms.HiddenInput())

    class Meta:
        model = Articles2
        fields = ('company_logo','event_banner','editable_image','x', 'y', 'width', 'height', )

    def save(self):
        photo = super(PForm, self).save()

        x = self.cleaned_data.get('x')
        y = self.cleaned_data.get('y')
        w = self.cleaned_data.get('width')
        h = self.cleaned_data.get('height')

        image = Image.open(photo.company_logo)

        print('photo.file in form' +str(photo.company_logo))
        cropped_image = image.crop((x, y, w+x, h+y))
        print('cropped image in form' + str(cropped_image))
        resized_image = cropped_image.resize((200, 200), Image.ANTIALIAS)
        print('resize image in form' + str(resized_image))
        resized_image.save(photo.company_logo.path)
        print(photo.company_logo.path)
        # print(photo)
        return photo




class PhotoForm(forms.ModelForm):
    x = forms.FloatField(widget=forms.HiddenInput())
    y = forms.FloatField(widget=forms.HiddenInput())
    width = forms.FloatField(widget=forms.HiddenInput())
    height = forms.FloatField(widget=forms.HiddenInput())

    class Meta:
        model = Photo
        fields = ('file','x', 'y', 'width', 'height', )

    def save(self):
        photo = super(PhotoForm, self).save()

        x = self.cleaned_data.get('x')
        y = self.cleaned_data.get('y')
        w = self.cleaned_data.get('width')
        h = self.cleaned_data.get('height')

        image = Image.open(photo.file)
        print(image)
        print('photo.file in form' +str(photo.file))
        cropped_image = image.crop((x, y, w+x, h+y))
        print('cropped image in form' + str(cropped_image))
        resized_image = cropped_image.resize((200, 200), Image.ANTIALIAS)
        print('resize image in form' + str(resized_image))
        resized_image.save(photo.file.path)
        print(photo.file.path)
        return photo


'''
