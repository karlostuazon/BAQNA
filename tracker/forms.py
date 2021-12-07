from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core import validators
from django.conf import settings
from django.db.models import fields
from django.db.models.fields import files
from django.db.models.fields.related import ForeignKey
from django.db.models.fields.reverse_related import OneToOneRel
from django.forms import ModelForm, widgets
from django.forms.fields import DateField, IntegerField
from django.forms.widgets import *
from .models import *
from django.core.validators import *
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberInternationalFallbackWidget, PhoneNumberPrefixWidget



class RegisterForm(UserCreationForm):
    last_name = forms.CharField(max_length=30, required=True,widget=forms.TextInput(attrs={'placeholder': 'Last Name..'}))
    first_name = forms.CharField(max_length=30, required=True,widget=forms.TextInput(attrs={'placeholder': 'First Name..'}))
    email = forms.EmailField(max_length=254, help_text='Required. Input a valid email address.',widget=forms.TextInput(attrs={'placeholder': 'Email..'}) )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

class PhysicianForm(ModelForm):
    cell_no = PhoneNumberField(
        widget=PhoneNumberInternationalFallbackWidget, required=False
    )
    class Meta:
        model = Physician
        fields = "__all__"

class CreateRecordFormPatient(ModelForm):
    cell_no = PhoneNumberField(
        widget=PhoneNumberInternationalFallbackWidget, required=False,
    )
    cell_no.widget.attrs = {'class': 'form-control', 'placeholder': '+63'}

    mcontact = PhoneNumberField(
        widget=PhoneNumberInternationalFallbackWidget, required=False 
    )
    mcontact.widget.attrs = {'class': 'form-control', 'id': 'mcontact', 'placeholder': '+63'}

    fcontact = PhoneNumberField(
        widget=PhoneNumberInternationalFallbackWidget, required=False 
    )
    fcontact.widget.attrs = {'class': 'form-control', 'id': 'fcontact', 'placeholder': '+63'}

    c1contact = PhoneNumberField(
        widget=PhoneNumberInternationalFallbackWidget, required=False
    )
    c1contact.widget.attrs = {'class': 'form-control', 'id': 'c1contact', 'placeholder': '+63'}

    c2contact = PhoneNumberField(
        widget=PhoneNumberInternationalFallbackWidget, required=False
    )
    c2contact.widget.attrs = {'class': 'form-control', 'id': 'c2contact', 'placeholder': '+63'}

    birthdate = forms.DateField(
        widget=DateInput(
            attrs={'class': 'form-control datetimepicker-input', 'id': 'dob', 'placeholder': 'mm-dd-yyyy',
                     'data-target': '#datetimepicker1'},
                     format='%m/%d/%y'
        ),
    )
    class Meta:
        model = Patient
        fields = '__all__'
        widgets = {
            'last_name': TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'first_name': TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'middle_name': TextInput(attrs={'class': 'form-control', 'placeholder': 'Middle Name'}),
            'suffix': TextInput(attrs={'class': 'form-control', 'placeholder': 'Suffix'}),
            'nick_name': TextInput(attrs={'class': 'form-control', 'placeholder': 'Nickname'}),
            'sex': Select(attrs={'class': 'form-control', 'placeholder': 'Sex'}),
            'age': HiddenInput(attrs={'type': 'hidden'}),

            'username': HiddenInput(attrs={'type': 'hidden'}),
            'relationship': TextInput(attrs={'class': 'form-control', 'placeholder': 'Relationship'}),

            'cert_date': HiddenInput(attrs={'type': 'hidden'}),
            
            'attending_doctor': Select(attrs={'class': 'form-control', 'placeholder': 'Attending Doctor'}),
            'landline': TextInput(attrs={'class': 'form-control', 'placeholder': 'Home/Landline'}),
            'email': EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            
            'house_no': TextInput(attrs={'class': 'form-control', 'placeholder': 'House/Unit no/LtBlk/Street'}),
            'barangay': TextInput(attrs={'class': 'form-control', 'placeholder': 'Barangay'}),
            'city': TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'region': TextInput(attrs={'class': 'form-control', 'placeholder': 'Region'}),
            'zip': TextInput(attrs={'class': 'form-control', 'placeholder': 'Zip Code'}),

            'mfname': TextInput(attrs={'class': 'form-control', 'id': 'mfname', 'placeholder': 'First Name'}),
            'mlname': TextInput(attrs={'class': 'form-control', 'id': 'mlname', 'placeholder': 'Last Name'}),
            'memail': TextInput(attrs={'class': 'form-control', 'id': 'memail', 'placeholder': 'Email'}),

            'ffname': TextInput(attrs={'class': 'form-control', 'id': 'ffname', 'placeholder': 'First Name'}),
            'flname': TextInput(attrs={'class': 'form-control', 'id': 'flname', 'placeholder': 'Last Name'}),
            'femail': TextInput(attrs={'class': 'form-control', 'id': 'femail', 'placeholder': 'Email'}),

            'c1full_name': TextInput(attrs={'class': 'form-control', 'id': 'c1full_name', 'placeholder': 'Full Name'}),
            'relation1': TextInput(attrs={'class': 'form-control', 'id': 'relation1', 'placeholder': 'Relation'}),
            'c2full_name': TextInput(attrs={'class': 'form-control', 'id': 'c2full_name', 'placeholder': 'Full Name'}),
            'relation2': TextInput(attrs={'class': 'form-control', 'id': 'relation2', 'placeholder': 'Relation'}),   
        }

class CertDateForm(ModelForm):
    cert_date = forms.DateField(
        widget=DateInput(
            attrs={'class': 'form-control datetimepicker-input', 'placeholder': 'mm-dd-yyyy',
                     'data-target': '#datetimepicker1'},
                     format='%m/%d/%y'
        ),
    )
    class Meta:
        model = Patient
        fields = ('cert_date',)

class AppointmentForm(ModelForm):
    date = forms.DateField(
        widget=DateInput(
            attrs={'class': 'form-control datetimepicker-input', 'placeholder': 'mm/dd/yyyy',
                     'data-target': '#datetimepicker1'},
                     format='%m/%d/%y'
        ),
    )
    class Meta:
        model = Appointment
        fields = '__all__'
        widgets = {
            'patient': HiddenInput(attrs={'type': 'hidden'}),
            'status': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Status', 'id':'status'}),
            'time': forms.NumberInput(attrs={'type': 'time', 'class': 'form-control', 'placeholder': 'Time', 'format': '%I:%M %p', 'id':'time'}),
            'doctor': HiddenInput(attrs={'type': 'hidden'}),
            'visit': TextInput(attrs={'class': 'form-control', 'placeholder': 'Visit', 'id':'visit'}),
            'location': TextInput(attrs={'class': 'form-control', 'placeholder': 'Location', 'id':'location'}),
        }

class AppointmentFormPatient(ModelForm):
    date = forms.DateField(
        widget=DateInput(
            attrs={'class': 'form-control datetimepicker-input', 'placeholder': 'mm/dd/yyyy',
                     'data-target': '#datetimepicker1'},
                     format='%m/%d/%y'
        ),
    )
    class Meta:
        model = Appointment
        fields = '__all__'
        widgets = {
            'patient': HiddenInput(attrs={'type': 'hidden'}),
            'status': HiddenInput(attrs={'type': 'hidden'}),
            'time': forms.NumberInput(attrs={'type': 'time', 'class': 'form-control', 'placeholder': 'Time', 'format': '%I:%M %p'}),
            'doctor': HiddenInput(attrs={'type': 'hidden'}),
            'visit': TextInput(attrs={'class': 'form-control', 'placeholder': 'Visit'}),
            'location': TextInput(attrs={'class': 'form-control', 'placeholder': 'Location'}),
        }

class PortalForm(UserCreationForm):
    password1 = forms.CharField(widget=PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password', 'required': True,}))
    password2 = forms.CharField(widget=PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password', 'required': True,}))
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        widgets = {
            'username': TextInput(attrs={'class': 'form-control', 'placeholder': 'Username', 'required': True}),
            'email': TextInput(attrs={'class': 'form-control', 'placeholder': 'Email Address', 'required': True,}),
        }

class PortalFormEdit(ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email')
        widgets = {
            'username': TextInput(attrs={'class': 'form-control', 'placeholder': 'Username', 'required': True}),
            'email': TextInput(attrs={'class': 'form-control', 'placeholder': 'Email Address', 'required': True,}),
        }

class PatientUserForm(ModelForm):
    class Meta:
        model = PatientUser
        fields = ('relationship',)
        widgets = {
            'relationship': TextInput(attrs={'class': 'form-control', 'placeholder': 'Relationship'}),
        }

class VaccineForm(ModelForm):
    VACCINES = (
        ('BCG', 'BCG'), ('Hepatitis B #1', 'Hepatitis B #1'), ('Hepatitis B #2', 'Hepatitis B #2'), ('DTaP/DTwP #1', 'DTaP/DTwP #1'), ('IPV/OPV #1', 'IPV/OPV #1'),
        ('HiB #1', 'HiB #1'), ('PCV #1', 'PCV #1'), ('Rotavirus #1', 'Rotavirus #1'), ('DTaP/DTwP #2', 'DTaP/DTwP #2'), ('IPV/OPV #2', 'IPV/OPV #2'),
        ('HiB #2', 'HiB #2'), ('PCV #2', 'PCV #2'), ('Rotavirus #2', 'Rotavirus #2'), ('Hepatitis B #3', 'Hepatitis B #3'), ('DTaP/DTwP #3', 'DTaP/DTwP #3'),
        ('IPV/OPV #3', 'IPV/OPV #3'), ('HiB #3', 'HiB #3'), ('PCV #3', 'PCV #3'), ('Rotavirus #3', 'Rotavirus #3'), ('Influenza #1', 'Influenza #1'),
        ('Measles', 'Measles'), ('Japanese Encephalitis B #1', 'Japanese Encephalitis B #1'), ('Influenza #1', 'Influenza #1'), ('MMR #1', 'MMR #1'), ('Varicella #1', 'Varicella #1'),
        ('DTaP/DTwP Booster #1', 'DTaP/DTwP Booster #1'), ('IPV/OPV Booster #1', 'IPV/OPV Booster #1'), ('HiB Booster #1', 'HiB Booster #1'), ('PCV Booster #1', 'PCV Booster #1'), ('Inactivated Hepatitis A #1', 'Inactivated Hepatitis A #1'),
        ('Inactivated Hepatitis A #2', 'Inactivated Hepatitis A #2'), ('Meninggococcal vaccine', 'Meninggococcal vaccine'), ('Typhoid', 'Typhoid'), ('Japanese Encephalitis B #2', 'Japanese Encephalitis B #2'), ('DTaP/DTwP Booster #2', 'DTaP/DTwP Booster #2'),
        ('IPV/OPV Booster #2', 'IPV/OPV Booster #2'), ('MMR #2', 'MMR #2'), ('Varicella #2', 'Varicella #2'), ('Td/Tdap Booster #3', 'Td/Tdap Booster #3'), ('HPV #1', 'HPV #1'),
        ('HPV #2', 'HPV #2'), ('HPV #1', 'HPV #1'), ('HPV #2', 'HPV #2'), ('HPV #3', 'HPV #3'), ('Influenza', 'Influenza'),
    )
    AGE = (
        ('Birth', 'Birth'), ('2 to 3 months', '2 to 3 months'), ('4 to 5 months', '4 to 5 months'), ('6 to 7 months', '6 to 7 months'), ('9 months', '9 months'), 
        ('12 to 15 months', '12 to 15 months'), ('18 to 21 months', '18 to 21 months'), ('24 months', '24 months'), ('4 to 6 yrs ', '4 to 6 yrs '), 
        ('10 yrs', '10 yrs'), ('9-14 yrs', '9-14 yrs'), ('15 and up', '15 and up'), ('Annual', 'Annual'),
    )
    DOSE = (
        ('1 of 1', '1 of 1'), ('1 of 2', '1 of 2'), ('1 of 3', '1 of 3'), ('1 of 4', '1 of 4'), ('1 of 5', '1 of 5'),
        ('2 of 2', '2 of 2'), (' 2 of 3', '2 of 3'), ('2 of 4', '2 of 4'), ('2 of 5', '2 of 5'),
        ('3 of 3', '3 of 3'), ('3 of 4', '3 of 4'), ('3 of 5', '3 of 5'),
        ('4 of 4', '4 of 4'), ('4 of 5', '4 of 5'),
        ('5 of 5', '5 of 5'), ('every 10 years', 'every 10 years'),
    )
    LOCATION = (
        ('R thigh', 'R thigh'), ('L thigh', 'L thigh'), ('R arm ', 'R arm'),
        ('L arm', 'L arm'), ('R buttocks', 'R buttocks'), ('L buttocks', 'L buttocks'),
    )
    age = ChoiceField(choices=AGE, widget=Select(attrs={'class': 'form-control', 'placeholder': 'Age'}))
    name = ChoiceField(choices=VACCINES, widget=Select(attrs={'class': 'form-control', 'placeholder': 'Vaccine'}))
    dose = ChoiceField(choices=DOSE, widget=Select(attrs={'class': 'form-control', 'placeholder': 'Dose'}))
    #location = forms.ChoiceField(choices=LOCATION, widget=Select(attrs={'class': 'form-control', 'placeholder': 'Location'}))
    date = forms.DateField(
        widget=DateInput(
            attrs={'class': 'form-control datetimepicker-input', 'placeholder': 'mm/dd/yyyy',
                     'data-target': '#datetimepicker1'},
                     format='%m/%d/%y'
        ),
        required=False
    )
    class Meta:
        model = Vaccine
        fields = ('patient', 'age', 'name', 'dose', 'brand', 'date', 'location', 'remarks')
        widgets = {
            'patient': HiddenInput(attrs={'type': 'hidden'}),
            'location': Select(attrs={'class':'form-control', 'placeholder': 'Location'}),
            'brand': TextInput(attrs={'class': 'form-control', 'placeholder': 'Brand'}),
            'remarks': TextInput(attrs={'class': 'form-control', 'placeholder': 'Remarks'}),
        }

class StaffCreateForm(UserCreationForm):
    password1 = forms.CharField(widget=PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password', 'required': True,}))
    password2 = forms.CharField(widget=PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password', 'required': True,}))
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        widgets = {
            'username': TextInput(attrs={'class': 'form-control', 'placeholder': 'Username', 'required': True}),
            'email': TextInput(attrs={'class': 'form-control', 'placeholder': 'Email Address', 'required': True,}),
        }

class StaffUpdateForm(ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email')
        widgets = {
            'username': TextInput(attrs={'class': 'form-control', 'placeholder': 'Username', 'required': True}),
            'email': TextInput(attrs={'class': 'form-control', 'placeholder': 'Email Address', 'required': True,}),
        }

class DoctorForm(ModelForm):
    CAN_REG = (
        ('Yes', 'Yes'),
        ('No', 'No'),
    )
    date_start = forms.DateField(
        widget=DateInput(
            attrs={'class': 'form-control datetimepicker-input', 'placeholder': 'mm/dd/yyyy',
                     'data-target': '#datetimepicker1'},
                     format='%m/%d/%y'
        ),
        required=False,
    )
    date_end = forms.DateField(
        widget=DateInput(
            attrs={'class': 'form-control datetimepicker-input', 'placeholder': 'mm/dd/yyyy',
                     'data-target': '#datetimepicker1'},
                     format='%m/%d/%y'
        ),
        required=False,
    )
    cell_no = PhoneNumberField(
        widget=PhoneNumberInternationalFallbackWidget, required=False
    )
    cell_no.widget.attrs = {'class': 'form-control', 'id': 'cell_no', 'placeholder': 'Contact (+63)'}
    can_reg = forms.ChoiceField(choices=CAN_REG, widget=forms.Select(attrs={'class': 'form-control', 'placeholder': 'Can Register?'}))
    class Meta:
        model = Physician
        exclude = ('user', )
        widgets = {
            'prefix': TextInput(attrs={'class': 'form-control', 'placeholder': 'Prefix',}),
            'last_name': TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'first_name': TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'title': TextInput(attrs={'class': 'form-control', 'placeholder': 'Title'}),
            'doc_type': TextInput(attrs={'class': 'form-control', 'placeholder': 'Type'}), 
        }

class UnconfirmedApptsForm(ModelForm):
    date_start = forms.DateField(
        widget=DateInput(
            attrs={'class': 'form-control', 'placeholder': 'DD/MM/YYY'}
            ,format=['%m/%d/%y']
        ),
        required=True,
        input_formats=settings.DATE_INPUT_FORMAT
    )

    date_end = forms.DateField(
        widget=DateInput(
            attrs={'class': 'form-control', 'placeholder': 'DD/MM/YYY'},
            format='%m/%d/%y'
        ),
        required=True,
        input_formats=settings.DATE_INPUT_FORMAT
    )

    class Meta:
        model = Appointment
        fields = ('date_start', 'date_end')

class dueVaxForm(ModelForm):
    date_start = forms.DateField(
        widget=DateInput(
            attrs={'class': 'form-control', 'placeholder': 'DD/MM/YYY'}
            ,format=['%m/%d/%y']
        ),
        required=True,
        input_formats=settings.DATE_INPUT_FORMAT
    )

    date_end = forms.DateField(
        widget=DateInput(
            attrs={'class': 'form-control', 'placeholder': 'DD/MM/YYY'},
            format='%m/%d/%y'
        ),
        required=True,
        input_formats=settings.DATE_INPUT_FORMAT
    )

    class Meta:
        model = Vaccine
        fields = ('date_start', 'date_end')


class EmailForm(forms.Form):
    to_email = forms.CharField(max_length=30, required=True,widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Email'}))