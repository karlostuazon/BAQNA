from datetime import timezone
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.db.models.fields import CharField, DateField, TimeField
from django.forms import widgets
from django.forms.fields import ChoiceField
from django.urls import reverse
from django.core.validators import *
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone

# Create your models here.
class Physician(models.Model):
    CAN_REG = (
        ('Yes', 'Yes'),
        ('No', 'No'),
    )
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    prefix = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True)
    first_name = models.CharField(max_length=100, null=True)
    title = models.CharField(max_length=100, null=True, blank=True)
    date_start = models.DateField(null=True, blank=True)
    date_end = models.DateField(null=True, blank=True)
    cell_no = PhoneNumberField(null=True, blank=True)
    doc_type = models.CharField(max_length=100, null=True)
    can_reg = models.CharField(max_length=100, null=True, blank=True, choices=CAN_REG)

    def __str__(self):
        return self.doc_type + " " + self.last_name



class Patient(models.Model):
    SEX = (
        ('M', 'Male'),
        ('F', 'Female'),
    )
    last_name = models.CharField(max_length=100, null=True)
    first_name = models.CharField(max_length=100, null=True)
    middle_name = models.CharField(max_length=100, null=True, blank=True)
    suffix = models.CharField(max_length=2, null=True, blank=True)
    nick_name = models.CharField(max_length=100, null=True, blank=True)
    sex = models.CharField(max_length=1, null=True, choices=SEX)
    birthdate = models.DateField(null=True)
    age = models.CharField(max_length=100, null=True, blank=True)
    attending_doctor = models.ForeignKey(Physician, related_name="docpatient", on_delete=models.CASCADE, null=True)

    #Vaccine Certificate Date
    cert_date = models.DateField(null=True, blank=True)

    # Contact Deets
    cell_no = PhoneNumberField(null=True, blank=True, validators=[MaxLengthValidator(13)])
    landline = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(max_length=254, null=True, blank=True)
    
    # Address
    house_no = models.CharField(max_length=100, null=True, blank=True)
    barangay = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    region = models.CharField(max_length=100, null=True, blank=True)
    zip = models.IntegerField(null=True, blank=True)
    
    # Mother
    mfname = models.CharField(max_length=100, null=True, blank=True)
    mlname = models.CharField(max_length=100, null=True, blank=True)
    mcontact = PhoneNumberField(null=True, blank=True)
    memail = models.EmailField(max_length=254, null=True, blank=True)
    # Father
    ffname = models.CharField(max_length=100, null=True, blank=True)
    flname = models.CharField(max_length=100, null=True, blank=True)
    fcontact = PhoneNumberField(null=True, blank=True)
    femail = models.EmailField(max_length=254, null=True, blank=True)

    c1full_name = models.CharField(max_length=100, null=True, blank=True)
    relation1 = models.CharField(max_length=100, null=True, blank=True)
    c1contact = PhoneNumberField(null=True, blank=True)

    c2full_name = models.CharField(max_length=100, null=True, blank=True)
    relation2 = models.CharField(max_length=100, null=True, blank=True)
    c2contact = PhoneNumberField(null=True, blank=True)

    def __str__(self):
        return "{}, {}".format(self.last_name, self.first_name)

class PatientUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, null=True)
    relationship = models.CharField(max_length=50, null=True)

    def __str__(self):
        return '{} of {}'.format(self.relationship, self.patient)


class Appointment(models.Model):
    STATUS = (
        ('Blank','Blank'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
        ('Rescheduled', 'Rescheduled'),
        ('Requested', 'Requested'),
    )
    patient = models.ForeignKey(Patient, null=True, blank=True, on_delete=models.CASCADE)
    status = models.CharField(max_length=100, choices=STATUS, null=True)
    date = models.DateField(null=True)
    time = models.TimeField(null=True)
    doctor = models.ForeignKey(Physician, on_delete=models.CASCADE)
    visit = models.CharField(max_length=100, null=True)
    location = models.CharField(max_length=100, null=True)
    date_created = models.DateTimeField(null=True, auto_now_add=True)

    def __str__(self):
        return '{} on {}'.format(self.patient, self.date)

class Vaccine(models.Model):
    LOCATION = (
        ('R thigh', 'R thigh'), ('L thigh', 'L thigh'), ('R arm ', 'R arm'),
        ('L arm', 'L arm'), ('R buttocks', 'R buttocks'), ('L buttocks', 'L buttocks'),
    )
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
    patient = models.ForeignKey(Patient, null=True, blank=True, on_delete=models.CASCADE)
    age = models.CharField(max_length=50, null=True, choices=AGE)
    name = models.CharField(max_length=50, null=True, choices=VACCINES)
    dose = models.CharField(max_length=50, null=True, choices=DOSE)
    brand = models.CharField(max_length=50, null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=50, null=True, blank=True, choices=LOCATION)
    remarks = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return "{} for {}".format(self.name, self.patient)
        