from django.db.models import query
from django.db.models.query import QuerySet, RawQuerySet
from django.db.models.query_utils import PathInfo
from django.http import request
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from .models import *
from .forms import *
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.mail import message, send_mail
from vaccine_tracker.settings import DATABASES, EMAIL_HOST_USER
from .decorators import unauthenticated_user, allowed_users, admin_only
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import login_required
from django.db.models import F
from .filters import *
import datetime
from xhtml2pdf import pisa
from easy_pdf.views import PDFTemplateResponseMixin, PDFTemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.shortcuts import render, redirect
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User, Group
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.decorators import method_decorator
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django import template
from django.template.loader import get_template 
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from dateutil.relativedelta import relativedelta



# Create your views here.
# @login_required(login_url='login')
# @user_passes_test(lambda u: u.is_superuser)
def password_reset(request):
    password_reset_form = PasswordResetForm()

    if(request.method == 'POST'):
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            email = password_reset_form.cleaned_data['email']
            users = User.objects.filter(Q(email=email))
            if users.exists():
                for user in users:
                    # subject = 'Password Reset Requested'
                    # email_template_name = 'tracker/password/password_reset_email.txt'
                    # context = {
                    #     'email': user.email,
                    #     'domain': '127.0.0.1:8000',
                    #     'site_name': 'Website',
                    #     'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    #     'user': user,
                    #     'token': default_token_generator.make_token(user),
                    #     'protocol': 'http',
                    # }
                    # mail = render_to_string(email_template_name, context)
                    # try:
                    #     send_mail(subject, mail, EMAIL_HOST_USER, [user.email], fail_silently=False)
                    # except BadHeaderError:
                    #     return HttpResponse('Invalid header found!')
                    # return redirect('password_reset/done')
                    htmly = get_template('tracker/password/password_reset_email.html')
                    d = {
                        'username': user,
                        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                        'token': default_token_generator.make_token(user),
                        'domain': '127.0.0.1:8000',
                        'protocol': 'http',
                        }
                    subject, from_email, to = 'BAQNA - Password Reset Form', 'your_email@gmail.com', email
                    html_content = htmly.render(d)
                    msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
                    msg.attach_alternative(html_content, "text/html")
                    msg.send()
                    return redirect('password_reset/done')
    data = {
        'password_reset_form': password_reset_form
    }
    return render(request, 'tracker/password/password_reset.html', data)

@login_required(login_url='login')
def notifsPage(request):
    flag = True if request.user.groups.filter(name='Doctor') else False
    if flag:
        appointments = Appointment.objects.filter(doctor=request.user.physician.id, status='Confirmed').order_by('-id')
    else:
        appointments = Appointment.objects.all().order_by('-id')

    data = {
        'appointments': appointments,
    }
    return render(request,'tracker/notifs.html', data)

def logoutUser(request):
	logout(request)
	return redirect('login')

@unauthenticated_user
def loginPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == 'POST':
                username = request.POST.get('username')
                password = request.POST.get('password')
                
                user = authenticate(request, username=username, password=password)
                
                if user is not None:
                    if user.groups.filter(name='Patient User').exists():
                        login(request, user)
                        return redirect('homePatient')
                    else:
                        login(request, user)
                        return redirect('home')
                else:
                    messages.info(request, 'Username or password is incorrect. Please try again.')
        context = {}
        return render(request, 'tracker/login.html', context)




@login_required(login_url='login')
def homePage(request):
    patients = Patient.objects.all()
    patientFilter = PatientFilter(request.GET, queryset=patients)
    patients = patientFilter.qs

    physicians = Physician.objects.all()
    data = {
        'patients': patients, 'physicians': physicians , 'patientFilter': patientFilter,
    }

    return render(request, "tracker/home.html", data)

@login_required(login_url='login')
@allowed_users(allowed_roles=['Patient User'])
def homePagePatient(request):
    patientUser = request.user.patientuser

    # -- Age (X Years Y Months) --
    curr_date = datetime.date.today()
    months = curr_date.month - patientUser.patient.birthdate.month
    years = curr_date.year - patientUser.patient.birthdate.year
    age = "{} year {} month".format(years, months)
    
    data = {
        'patientUser': patientUser, 'age': age,
    }
    return render(request, 'tracker/homePatient.html', data)


#--CREATE RECORD VIEW--
@login_required(login_url='login')
def createRecord(request):
    patient_form = CreateRecordFormPatient()
    latest = Patient.objects.latest('id')
    latest_id = getattr(latest, 'id')
    
    if(request.method == "POST"):
        patient_form = CreateRecordFormPatient(request.POST)
        if patient_form.is_valid():
            pfname = patient_form.cleaned_data.get('first_name')
            plname = patient_form.cleaned_data.get('last_name')

            new_patient = patient_form.save()

            Vaccine.objects.bulk_create([
                Vaccine(age='Birth', name='BCG', dose='1 of 1', patient=new_patient, due_date=new_patient.birthdate),
                Vaccine(age='Birth', name='Hepatitis B #1', dose='1 of 3', patient=new_patient, due_date=new_patient.birthdate),

                Vaccine(age='2 to 3 months', name='Hepatitis B #2', dose='2 of 3', patient=new_patient, due_date=new_patient.birthdate + relativedelta(months=2)),
                Vaccine(age='2 to 3 months', name='DTaP/DTwP #1', dose='1 of 5', patient=new_patient, due_date=new_patient.birthdate + relativedelta(weeks=6)),
                Vaccine(age='2 to 3 months', name='IPV/OPV #1', dose='1 of 5', patient=new_patient, due_date=new_patient.birthdate + relativedelta(weeks=6)),
                Vaccine(age='2 to 3 months', name='HiB #1', dose='1 of 4', patient=new_patient, due_date=new_patient.birthdate + relativedelta(weeks=6)),
                Vaccine(age='2 to 3 months', name='PCV #1', dose='1 of 4', patient=new_patient, due_date=new_patient.birthdate + relativedelta(weeks=6)),
                Vaccine(age='2 to 3 months', name='Rotavirus #1', dose='1 of 2', patient=new_patient, due_date=new_patient.birthdate + relativedelta(weeks=6)),

                Vaccine(age='4 to 5 months', name='DTaP/DTwP #2', dose='2 of 5', patient=new_patient),
                Vaccine(age='4 to 5 months', name='IPV/OPV #2', dose='2 of 5', patient=new_patient),
                Vaccine(age='4 to 5 months', name='HiB #2', dose='2 of 4', patient=new_patient),
                Vaccine(age='4 to 5 months', name='PCV #2', dose='2 of 4', patient=new_patient),
                Vaccine(age='4 to 5 months', name='Rotavirus #2', dose='2 of 2', patient=new_patient),
                
                Vaccine(age='6 to 7 months', name='Hepatitis B #3', dose='3 of 3', patient=new_patient, due_date=new_patient.birthdate + relativedelta(months=6)),
                Vaccine(age='6 to 7 months', name='DTaP/DTwP #3', dose='3 of 5', patient=new_patient),
                Vaccine(age='6 to 7 months', name='IPV/OPV #3', dose='3 of 5', patient=new_patient),
                Vaccine(age='6 to 7 months', name='HiB #3', dose='3 of 4', patient=new_patient),
                Vaccine(age='6 to 7 months', name='PCV #3', dose='3 of 4', patient=new_patient),
                Vaccine(age='6 to 7 months', name='Rotavirus #3', dose='3 of 3', patient=new_patient),
                Vaccine(age='6 to 7 months', name='Influenza #1', dose='1 of 2', patient=new_patient, due_date=new_patient.birthdate + relativedelta(months=6)),
                
                Vaccine(age='9 months', name='Measles', dose='1 of 1', patient=new_patient, due_date=new_patient.birthdate + relativedelta(months=9)),
                Vaccine(age='9 months', name='Japanese Encephalitis B #1', dose='1 of 2', patient=new_patient, due_date=new_patient.birthdate + relativedelta(months=9)),
                Vaccine(age='9 months', name='Influenza #2', dose='2 of 2', patient=new_patient),

                Vaccine(age='12 to 15 months', name='MMR #1', dose='1 of 2', patient=new_patient, due_date=new_patient.birthdate + relativedelta(months=12)),
                Vaccine(age='12 to 15 months', name='Varicella #1', dose='1 of 2', patient=new_patient, due_date=new_patient.birthdate + relativedelta(months=12)),
                Vaccine(age='12 to 15 months', name='DTaP/DTwP Booster #1', dose='4 of 5', patient=new_patient, due_date=new_patient.birthdate + relativedelta(months=12)),
                Vaccine(age='12 to 15 months', name='IPV/OPV Booster #1', dose='4 of 5', patient=new_patient, due_date=new_patient.birthdate + relativedelta(months=12)),
                Vaccine(age='12 to 15 months', name='HiB Booster #1', dose='4 of 4', patient=new_patient),
                Vaccine(age='12 to 15 months', name='PCV Booster #1', dose='4 of 4', patient=new_patient),
                Vaccine(age='12 to 15 months', name='Inactivated Hepatitis A #1', dose='1 of 2', patient=new_patient, due_date=new_patient.birthdate + relativedelta(months=12)),

                Vaccine(age='18 to 21 months', name='Inactivated Hepatitis A #2', dose='2 of 2', patient=new_patient),

                Vaccine(age='24 months', name='Meninggococcal vaccine', dose='1 of 1', patient=new_patient),
                Vaccine(age='24 months', name='Typhoid', dose='1 of 1', patient=new_patient, due_date=new_patient.birthdate + relativedelta(years=2)),
                Vaccine(age='24 months', name='Japanese Encephalitis B #2', dose='2 of 2', patient=new_patient, due_date=new_patient.birthdate + relativedelta(months=9)),    

                Vaccine(age='4 to 6 yrs ', name='DTaP/DTwP Booster #2', dose='5 of 5', patient=new_patient, due_date=new_patient.birthdate + relativedelta(years=4)),

                Vaccine(age='10 yrs', name='IPV/OPV Booster #2', dose='5 of 5', patient=new_patient, due_date=new_patient.birthdate + relativedelta(years=4)),   
                Vaccine(age='10 yrs', name='MMR #2', dose='2 of 2', patient=new_patient), 
                Vaccine(age='10 yrs', name='Varicella #2', dose='2 of 2', patient=new_patient), 
                Vaccine(age='10 yrs', name='Td/Tdap Booster #3', dose='every 10 years', patient=new_patient, due_date=new_patient.birthdate + relativedelta(years=15)),    
                
                Vaccine(age='9-14 yrs', name='HPV #1', dose='1 of 2', patient=new_patient),
                Vaccine(age='9-14 yrs', name='HPV #2', dose='2 of 2', patient=new_patient),   

                Vaccine(age='15 and up', name='HPV #1', dose='1 of 3', patient=new_patient),
                Vaccine(age='15 and up', name='HPV #2', dose='2 of 3', patient=new_patient),
                Vaccine(age='15 and up', name='HPV #3', dose='3 of 3', patient=new_patient), 

                Vaccine(age='Annual', name='Influenza', patient=new_patient),
            ])

            messages.success(request, 'Account has been created for {} {}.'.format(pfname, plname))
        else:
            messages.error(request, patient_form.errors)
        return redirect('/home')

    context = {'patient_form':patient_form,
                'latest_id': latest_id,
    }
    return render(request, "tracker/createRecord.html", context)

@login_required(login_url='login')
def patient(request, pk):
    patient = Patient.objects.get(id=pk)

    # -- Age (X Years Y Months) --
    curr_date = datetime.date.today()
    months = curr_date.month - patient.birthdate.month
    years = curr_date.year - patient.birthdate.year
    age = "{} year {} month".format(years, months)

    data = {
        'patient': patient, 'age': age,
    }
    return render(request, 'tracker/patient.html', data)

@login_required(login_url='login')
def editPatient(request, pk):
    patient = Patient.objects.get(id=pk)
    patient_form = CreateRecordFormPatient(instance=patient)

    # -- Age (X Years Y Months) --
    curr_date = datetime.date.today()
    months = curr_date.month - patient.birthdate.month
    years = curr_date.year - patient.birthdate.year
    age = "{} year {} month".format(years, months)

    if(request.method == "POST"):
        patient_form = CreateRecordFormPatient(request.POST, instance=patient)
        if patient_form.is_valid():
            pfname = patient_form.cleaned_data.get('first_name')
            plname = patient_form.cleaned_data.get('last_name')
            patient_form.save()
            messages.success(request, 'Patient details have been saved.')
        else:
            messages.error(request, patient_form.errors)
        return redirect('/patient/' + pk)

    data = {
        'patient': patient, 'patient_form': patient_form,
        'age': age,
    }

    return render(request, 'tracker/editPatient.html', data)

@login_required(login_url='login')
def appointment(request, pk):
    patient = Patient.objects.get(id=pk)
    appointment_form = AppointmentForm(initial={'patient': patient, 'doctor': patient.attending_doctor})
    appointment_form_patient = AppointmentFormPatient(initial={'patient': patient, 'status': 'Requested', 'doctor': patient.attending_doctor})

    appointments = Appointment.objects.filter(patient=patient).order_by('date')

    # -- Age (X Years Y Months) --
    curr_date = datetime.date.today()
    months = curr_date.month - patient.birthdate.month
    years = curr_date.year - patient.birthdate.year
    age = "{} year {} month".format(years, months)

    if(request.method == "POST"):
        appointment_form = AppointmentForm(request.POST)
        if appointment_form.is_valid():
            appointment_form.save()
            messages.success(request, 'Appointment scheduled!')
        else:
            messages.error(request, appointment_form.errors)
        return redirect('/appointment/' + pk)

    data = {
        'patient': patient,
        'appointment_form': appointment_form,
        'appointment_form_patient': appointment_form_patient,
        'appointments': appointments,
        'age': age,
    }

    return render(request, 'tracker/appointment.html', data)

@login_required(login_url='login')
def editAppointment(request, pk):
    patient = Patient.objects.get(id=pk)
    appointments = Appointment.objects.filter(patient=patient).order_by('date')

    appointment_formset = forms.modelformset_factory(Appointment, AppointmentForm, extra=0)
    formset = appointment_formset(queryset=appointments)
    # -- Age (X Years Y Months) --
    curr_date = datetime.date.today()
    months = curr_date.month - patient.birthdate.month
    years = curr_date.year - patient.birthdate.year
    age = "{} year {} month".format(years, months)

    if(request.method == "POST"):
        formset = appointment_formset(request.POST, queryset=appointments)
        if formset.is_valid():
            for form in formset:
                form.save()
            messages.success(request, 'Appointment saved!')
        else:
            messages.error(request, formset.errors)
        return redirect('/appointment/' + pk)

    data = {
        'patient': patient,
        'formset': formset,
        'appointments': appointments,
        'age': age,
    }

    return render(request, 'tracker/editAppointment.html', data)

def hasPatientUser(request, pk):
    patient = Patient.objects.get(id=pk)
    if PatientUser.objects.get(patient=patient) is None:
        return False
    
    return True


@login_required(login_url='login')
def portal(request, pk):
    patient = Patient.objects.get(id=pk)
    try:
        patient_user = PatientUser.objects.get(patient=patient)
    except PatientUser.DoesNotExist:
        patient_user = None
    patient_user_grp = Group.objects.get(name='Patient User')

    portal_form = PortalForm()
    patient_form = PatientUserForm()
    portal_form_edit = PortalFormEdit()
    
    # -- Age (X Years Y Months) --
    curr_date = datetime.date.today()
    months = curr_date.month - patient.birthdate.month
    years = curr_date.year - patient.birthdate.year
    age = "{} year {} month".format(years, months)

    if request.method == 'POST':
        portal_form = PortalForm(request.POST)
        patient_form = PatientUserForm(request.POST)
        if User.objects.filter(username = request.POST['username']).exists():
            messages.error(request, 'Username exists.')
        else:
            if portal_form.is_valid() and patient_form.is_valid():
                user = portal_form.save()
                profile = patient_form.save(commit=False)
                profile.user = user
                profile.patient = patient
                profile.save()
                patient_user_grp.user_set.add(user)
                messages.success(request, 'Account Created!')
        return redirect('/portal/' + pk)
    data = {
        'patient': patient,
        'patient_user': patient_user, 
        'age': age,
        'portal_form': portal_form,
        'patient_form': patient_form,
        'portal_form_edit': portal_form_edit,
    }
    return render(request, 'tracker/portal.html', data)

@login_required(login_url='login')
def portalEdit(request, pk):
    patient = Patient.objects.get(id=pk)

    try:
        patient_user = PatientUser.objects.get(patient=patient)
    except PatientUser.DoesNotExist:
        patient_user = None

    patient_form = PatientUserForm(instance=patient_user)
    portal_form_edit = PortalFormEdit(instance=patient_user.user)

    # -- Age (X Years Y Months) --
    curr_date = datetime.date.today()
    months = curr_date.month - patient.birthdate.month
    years = curr_date.year - patient.birthdate.year
    age = "{} year {} month".format(years, months)

    if(request.method == "POST"):
        patient_form = PatientUserForm(request.POST, instance=patient_user)
        portal_form_edit = PortalFormEdit(request.POST, instance=patient_user.user)

        if patient_form.is_valid() and portal_form_edit.is_valid():
            patient_form.save()
            portal_form_edit.save()
            messages.success(request, 'Patient Account details have been saved.')
        else:
            messages.error(request, patient_form.errors)

        return redirect('/portal/' + pk)
    
    data = {
        'patient': patient,
        'patient_user': patient_user,
        'patient_form': patient_form,
        'portal_form_edit': portal_form_edit,
        'age': age,
    }

    return render(request, 'tracker/portalEdit.html', data)

@login_required(login_url='login')
def portalEditPass(request, pk):
    patient = Patient.objects.get(id=pk)

    try:
        patient_user = PatientUser.objects.get(patient=patient)
    except PatientUser.DoesNotExist:
        patient_user = None

    password_form = PasswordChangeForm(patient_user.user)

    # -- Age (X Years Y Months) --
    curr_date = datetime.date.today()
    months = curr_date.month - patient.birthdate.month
    years = curr_date.year - patient.birthdate.year
    age = "{} year {} month".format(years, months)

    if(request.method == "POST"):
        password_form = PasswordChangeForm(patient_user.user, request.POST)

        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password Changed!')
        else:
            messages.error(request, password_form.errors)
        
        return redirect('/portal/' + pk)

    data = {
        'patient': patient,
        'patient_user': patient_user,
        'password_form': password_form,
        'age': age,
    }

    return render(request, 'tracker/portalEditPass.html', data)

@login_required(login_url='login')
def certificate(request, pk):
    patient = Patient.objects.get(id=pk)
    cert_date_form = CertDateForm(instance=patient)

    # -- Age (x Years y Months) -- 
    curr_date = datetime.date.today()
    months = curr_date.month - patient.birthdate.month
    years = curr_date.year - patient.birthdate.year
    age = "{} year {} month".format(years, months)

    patient.cert_date = curr_date
    patient.age = age

    data = {
        'patient': patient, 
        'age': age,
        'curr_date': curr_date,
        'cert_date_form': cert_date_form,
    }
    return render(request, 'tracker/certificate.html', data)
    
class PdfDetail(PDFTemplateResponseMixin, DetailView):
    model = Patient
    template_name = 'tracker/pdf_cert.html'
    download_filename = 'Vaccine Certificate of {}-{}'.format(model.last_name, model.first_name)
    context_object_name = 'patient'

    def get_context_data(self, *args, **kwargs):
        context = super(PdfDetail, self).get_context_data(*args, **kwargs)

        curr_date = datetime.date.today()
        months = curr_date.month - self.object.birthdate.month
        years = curr_date.year - self.object.birthdate.year

        context['curr_date'] = datetime.date.today()
        context['age'] = "{} year {} month".format(years, months)

        return context

class PdfDetailPatient(PDFTemplateResponseMixin, DetailView):
    model = Patient
    template_name = 'tracker/pdf_cert_patient.html'
    download_filename = 'Vaccine Certificate of {}-{}'.format(model.last_name, model.first_name)
    context_object_name = 'patient'

    def get_context_data(self, *args, **kwargs):
        context = super(PdfDetailPatient, self).get_context_data(*args, **kwargs)

        curr_date = datetime.date.today()
        months = curr_date.month - self.object.birthdate.month
        years = curr_date.year - self.object.birthdate.year

        context['curr_date'] = datetime.date.today()
        context['age'] = "{} year {} month".format(years, months)

        return context

@login_required(login_url='login')
def vaccine(request, pk):
    patient = Patient.objects.get(id=pk)
    vaccines = Vaccine.objects.filter(patient=patient).order_by('id')

    vaccine_form = VaccineForm(request.POST or None, initial={'patient': patient})
    if request.method == 'POST':
        if vaccine_form.is_valid():
            if not vaccines.filter(name=request.POST['name']).exists():
                vaccine_form.save()
                messages.success(request, 'Vaccine has been added to {}'.format(patient))
            else:
                messages.error(request, 'Vaccine already exists.')
                return redirect('/vaccine/' + pk)
        else:
            messages.error(request, vaccine_form.errors)
        return redirect('/vaccine/' + pk)

    # -- Age (X Years Y Months) --
    curr_date = datetime.date.today()
    months = curr_date.month - patient.birthdate.month
    years = curr_date.year - patient.birthdate.year
    age = "{} year {} month".format(years, months)
    
    data = {
        'patient': patient,
        'vaccines': vaccines,
        'vaccine_form': vaccine_form,
        'age': age,
    }
    return render(request, 'tracker/vaccine.html', data)

@login_required(login_url='login')
def editVaccine(request, pk):
    patient = Patient.objects.get(id=pk)
    vaccines = Vaccine.objects.filter(patient=patient)

    vaccine_formset = forms.modelformset_factory(Vaccine, VaccineForm, 
    extra=0)
    formset = vaccine_formset(request.POST or None, queryset=vaccines)
    if request.method == 'POST':
        if formset.is_valid():
            for form in formset:
                form.save()
            #DTaP/DTwP
            if vaccines.get(name='DTaP/DTwP #1').date is not None:
                vaccines.filter(name='DTaP/DTwP #2').update(due_date=vaccines.get(name='DTaP/DTwP #1').date + relativedelta(weeks=4))
            if vaccines.get(name='DTaP/DTwP #2').date is not None:
                vaccines.filter(name='DTaP/DTwP #3').update(due_date=vaccines.get(name='DTaP/DTwP #2').date + relativedelta(weeks=4))
            #HiB
            if vaccines.get(name='HiB #1').date is not None:
                vaccines.filter(name='HiB #2').update(due_date=vaccines.get(name='HiB #1').date + relativedelta(weeks=4))
            if vaccines.get(name='HiB #2').date is not None:
                vaccines.filter(name='HiB #3').update(due_date=vaccines.get(name='HiB #2').date + relativedelta(weeks=4))
            if vaccines.get(name='HiB #3').date is not None:
                vaccines.filter(name='HiB Booster #1').update(due_date=vaccines.get(name='HiB #3').date + relativedelta(months=6))
            #HPV 9-14yrs
            if vaccines.get(name='HPV #1', age__contains='9-14').date is not None:
                vaccines.filter(name='HPV #2').update(due_date=vaccines.get(name='HPV #1', age__contains='9-14').date + relativedelta(months=6))
            #HPV 15 up
            if vaccines.get(name='HPV #1', age__contains='15').date is not None:
                vaccines.filter(name='HPV #2').update(due_date=vaccines.get(name='HPV #1', age__contains='15').date + relativedelta(months=2))
            if vaccines.get(name='HPV #2', age__contains='15').date is not None:
                vaccines.filter(name='HPV #3').update(due_date=vaccines.get(name='HPV #2', age__contains='15').date + relativedelta(months=6))  
            #Inactivated Hepatitis A
            if vaccines.get(name='Inactivated Hepatitis A #1').date is not None:
                vaccines.filter(name='Inactivated Hepatitis A #2').update(due_date=vaccines.get(name='Inactivated Hepatitis A #1').date + relativedelta(months=6)) 
            #Influenza
            if vaccines.get(name='Influenza #1').date is not None:
                vaccines.filter(name='Influenza #2').update(due_date=vaccines.get(name='Influenza #1').date + relativedelta(weeks=4))
            #IPV/OPV
            if vaccines.get(name='IPV/OPV #1').date is not None:
                vaccines.filter(name='IPV/OPV #2').update(due_date=vaccines.get(name='IPV/OPV #1').date + relativedelta(weeks=4))
            if vaccines.get(name='IPV/OPV #2').date is not None:
                vaccines.filter(name='IPV/OPV #3').update(due_date=vaccines.get(name='IPV/OPV #2').date + relativedelta(weeks=4))
            #Japanese Encephalitis B
            if vaccines.get(name='Japanese Encephalitis B #1').date is not None:
                vaccines.filter(name='Japanese Encephalitis B #2').update(due_date=vaccines.get(name='Japanese Encephalitis B #2').date + relativedelta(months=24))
            #MMR
            if vaccines.get(name='MMR #1').date is not None:
                vaccines.filter(name='MMR #2').update(due_date=vaccines.get(name='MMR #1').date + relativedelta(weeks=4))
            #PCV
            if vaccines.get(name='PCV #1').date is not None:
                vaccines.filter(name='PCV #2').update(due_date=vaccines.get(name='PCV #1').date + relativedelta(weeks=4))
            if vaccines.get(name='PCV #2').date is not None:
                vaccines.filter(name='PCV #3').update(due_date=vaccines.get(name='PCV #2').date + relativedelta(weeks=4))
            if vaccines.get(name='PCV #3').date is not None:
                vaccines.filter(name='PCV Booster #1').update(due_date=vaccines.get(name='PCV #3').date + relativedelta(months=6))
            #Rotavirus
            if vaccines.get(name='Rotavirus #1').date is not None:
                vaccines.filter(name='Rotavirus #2').update(due_date=vaccines.get(name='Rotavirus #1').date + relativedelta(weeks=4))
            if vaccines.get(name='Rotavirus #2').date is not None:
                vaccines.filter(name='Rotavirus #3').update(due_date=vaccines.get(name='Rotavirus #2').date + relativedelta(weeks=4))
            #Typhoid
            if vaccines.get(name='Typhoid').date is not None:
                vaccines.filter(name='Typhoid').update(due_date=vaccines.get(name='Typhoid').date + relativedelta(years=3))
            #Varicella
            if vaccines.get(name='Varicella #1').date is not None:
                vaccines.filter(name='Varicella #2').update(due_date=vaccines.get(name='Varicella #1').date + relativedelta(months=3))

            messages.success(request, 'Vaccine saved!')
        else:
            messages.error(request, formset.errors)
        return redirect('/vaccine/' + pk)
        

    # -- Age (X Years Y Months) --
    curr_date = datetime.date.today()
    months = curr_date.month - patient.birthdate.month
    years = curr_date.year - patient.birthdate.year
    age = "{} year {} month".format(years, months)
    
    data = {
        'patient': patient, 
        'formset': formset,
        'vaccines': vaccines,
        'age': age,
    }
    return render(request, 'tracker/editVaccine.html', data)

@login_required(login_url='login')
def report(request):
    appt = Appointment.objects.all()

    #BCG
    bcg = Vaccine.objects.filter(name__contains='BCG')
    confirmed_bcg = appt.filter(patient__in=bcg.values('patient'), date__in=bcg.values('due_date'), status='Confirmed').count()
    unconfirmed_bcg = appt.filter(patient__in=bcg.values('patient'), date__in=bcg.values('due_date'), 
                                                status__in=['Blank', 'Cancelled', 'Rescheduled', 'Requested']).count()
    total_bcg = bcg.count()
    bcg_no_appt = total_bcg - (confirmed_bcg + unconfirmed_bcg)

    #Hepatitis B
    hb = Vaccine.objects.filter(name__contains='Hepatitis B')
    confirmed_hb = appt.filter(patient__in=hb.values('patient'), date__in=hb.values('due_date'), status='Confirmed').count()
    unconfirmed_hb = appt.filter(patient__in=hb.values('patient'), date__in=hb.values('due_date'), 
                                                status__in=['Blank', 'Cancelled', 'Rescheduled', 'Requested']).count()
    total_hb = hb.count()
    hb_no_appt = total_hb - (confirmed_hb + unconfirmed_hb)

    #DTaP/DTwP
    dtap = Vaccine.objects.filter(name__contains='DTaP/DTwP')
    confirmed_dtap = appt.filter(patient__in=dtap.values('patient'), date__in=dtap.values('due_date'), status='Confirmed').count()
    unconfirmed_dtap = appt.filter(patient__in=dtap.values('patient'), date__in=dtap.values('due_date'), 
                                                status__in=['Blank', 'Cancelled', 'Rescheduled', 'Requested']).count()
    total_dtap = dtap.count()
    dtap_no_appt = total_dtap - (confirmed_dtap + unconfirmed_dtap)

    #IPV/OPV
    ipv = Vaccine.objects.filter(name__contains='IPV/OPV')
    confirmed_ipv = appt.filter(patient__in=ipv.values('patient'), date__in=ipv.values('due_date'), status='Confirmed').count()
    unconfirmed_ipv = appt.filter(patient__in=ipv.values('patient'), date__in=ipv.values('due_date'), 
                                                status__in=['Blank', 'Cancelled', 'Rescheduled', 'Requested']).count()
    total_ipv = ipv.count()
    ipv_no_appt = total_ipv - (confirmed_ipv + unconfirmed_ipv)

    #HiB
    hib = Vaccine.objects.filter(name__contains='HiB')
    confirmed_hib = appt.filter(patient__in=hib.values('patient'), date__in=hib.values('due_date'), status='Confirmed').count()
    unconfirmed_hib = appt.filter(patient__in=hib.values('patient'), date__in=hib.values('due_date'), 
                                                status__in=['Blank', 'Cancelled', 'Rescheduled', 'Requested']).count()
    total_hib = hib.count()
    hib_no_appt = total_hib - (confirmed_hib + unconfirmed_hib)

    #PCV
    pcv = Vaccine.objects.filter(name__contains='PCV')
    confirmed_pcv = appt.filter(patient__in=pcv.values('patient'), date__in=pcv.values('due_date'), status='Confirmed').count()
    unconfirmed_pcv = appt.filter(patient__in=pcv.values('patient'), date__in=pcv.values('due_date'), 
                                                status__in=['Blank', 'Cancelled', 'Rescheduled', 'Requested']).count()
    total_pcv = pcv.count()
    pcv_no_appt = total_pcv - (confirmed_pcv + unconfirmed_pcv)

    #Rotavirus
    rv = Vaccine.objects.filter(name__contains='Rotavirus')
    confirmed_rv = appt.filter(patient__in=rv.values('patient'), date__in=rv.values('due_date'), status='Confirmed').count()
    unconfirmed_rv = appt.filter(patient__in=rv.values('patient'), date__in=rv.values('due_date'), 
                                                status__in=['Blank', 'Cancelled', 'Rescheduled', 'Requested']).count()
    total_rv = rv.count()
    rv_no_appt = total_rv - (confirmed_rv + unconfirmed_rv)

    #Measles
    msls = Vaccine.objects.filter(name__contains='Measles')
    confirmed_msls = appt.filter(patient__in=msls.values('patient'), date__in=msls.values('due_date'), status='Confirmed').count()
    unconfirmed_msls = appt.filter(patient__in=msls.values('patient'), date__in=msls.values('due_date'), 
                                                status__in=['Blank', 'Cancelled', 'Rescheduled', 'Requested']).count()
    total_msls = msls.count()
    msls_no_appt = total_msls - (confirmed_msls + unconfirmed_msls)

    #MMR
    mmr = Vaccine.objects.filter(name__contains='MMR')
    confirmed_mmr = appt.filter(patient__in=mmr.values('patient'), date__in=mmr.values('due_date'), status='Confirmed').count()
    unconfirmed_mmr = appt.filter(patient__in=mmr.values('patient'), date__in=mmr.values('due_date'), 
                                                status__in=['Blank', 'Cancelled', 'Rescheduled', 'Requested']).count()
    total_mmr = mmr.count()
    mmr_no_appt = total_mmr - (confirmed_mmr + unconfirmed_mmr)

    #Varicella
    vrcl = Vaccine.objects.filter(name__contains='Varicella')
    confirmed_vrcl = appt.filter(patient__in=vrcl.values('patient'), date__in=vrcl.values('due_date'), status='Confirmed').count()
    unconfirmed_vrcl = appt.filter(patient__in=vrcl.values('patient'), date__in=vrcl.values('due_date'), 
                                                status__in=['Blank', 'Cancelled', 'Rescheduled', 'Requested']).count()
    total_vrcl = vrcl.count()
    vrcl_no_appt = total_vrcl - (confirmed_vrcl + unconfirmed_vrcl)

    #Influenza
    flu = Vaccine.objects.filter(name__contains='Influenza')
    confirmed_flu = appt.filter(patient__in=flu.values('patient'), date__in=flu.values('due_date'), status='Confirmed').count()
    unconfirmed_flu = appt.filter(patient__in=flu.values('patient'), date__in=flu.values('due_date'), 
                                                status__in=['Blank', 'Cancelled', 'Rescheduled', 'Requested']).count()
    total_flu = flu.count()
    flu_no_appt = total_flu - (confirmed_flu + unconfirmed_flu)

    #Jap Encephalitis B
    jeb = Vaccine.objects.filter(name__contains='Japanese Encephalitis B')
    confirmed_jeb = appt.filter(patient__in=jeb.values('patient'), date__in=jeb.values('due_date'), status='Confirmed').count()
    unconfirmed_jeb = appt.filter(patient__in=jeb.values('patient'), date__in=jeb.values('due_date'), 
                                                status__in=['Blank', 'Cancelled', 'Rescheduled', 'Requested']).count()
    total_jeb = jeb.count()
    jeb_no_appt = total_jeb - (confirmed_jeb + unconfirmed_jeb)

    #Hepatitis A
    ha = Vaccine.objects.filter(name__contains='Hepatitis A')
    confirmed_ha = appt.filter(patient__in=ha.values('patient'), date__in=ha.values('due_date'), status='Confirmed').count()
    unconfirmed_ha = appt.filter(patient__in=ha.values('patient'), date__in=ha.values('due_date'), 
                                                status__in=['Blank', 'Cancelled', 'Rescheduled', 'Requested']).count()
    total_ha = ha.count()
    ha_no_appt = total_ha - (confirmed_ha + unconfirmed_ha)

    #Meningococcal
    mng = Vaccine.objects.filter(name__contains='Meninggococcal')
    confirmed_mng = appt.filter(patient__in=mng.values('patient'), date__in=mng.values('due_date'), status='Confirmed').count()
    unconfirmed_mng = appt.filter(patient__in=mng.values('patient'), date__in=mng.values('due_date'), 
                                                status__in=['Blank', 'Cancelled', 'Rescheduled', 'Requested']).count()
    total_mng = mng.count()
    mng_no_appt = total_mng - (confirmed_mng + unconfirmed_mng)

    #Typhoid
    typ = Vaccine.objects.filter(name__contains='Typhoid')
    confirmed_typ = appt.filter(patient__in=typ.values('patient'), date__in=typ.values('due_date'), status='Confirmed').count()
    unconfirmed_typ = appt.filter(patient__in=typ.values('patient'), date__in=typ.values('due_date'), 
                                                status__in=['Blank', 'Cancelled', 'Rescheduled', 'Requested']).count()
    total_typ = typ.count()
    typ_no_appt = total_typ - (confirmed_typ + unconfirmed_typ)

    #Td/Tdap
    td = Vaccine.objects.filter(name__contains='Td/Tdap')
    confirmed_td = appt.filter(patient__in=td.values('patient'), date__in=td.values('due_date'), status='Confirmed').count()
    unconfirmed_td = appt.filter(patient__in=td.values('patient'), date__in=td.values('due_date'), 
                                                status__in=['Blank', 'Cancelled', 'Rescheduled', 'Requested']).count()
    total_td = td.count()
    td_no_appt = total_td - (confirmed_td + unconfirmed_td)

    #HPV
    hpv = Vaccine.objects.filter(name__contains='HPV')
    confirmed_hpv = appt.filter(patient__in=hpv.values('patient'), date__in=hpv.values('due_date'), status='Confirmed').count()
    unconfirmed_hpv = appt.filter(patient__in=hpv.values('patient'), date__in=hpv.values('due_date'), 
                                                status__in=['Blank', 'Cancelled', 'Rescheduled', 'Requested']).count()
    total_hpv = hpv.count()
    hpv_no_appt = total_hpv - (confirmed_hpv + unconfirmed_hpv)


    data = {
        'confirmed_bcg': confirmed_bcg, 'unconfirmed_bcg': unconfirmed_bcg,
        'total_bcg': total_bcg, 'bcg_no_appt': bcg_no_appt,

        'confirmed_hb': confirmed_hb, 'unconfirmed_hb': unconfirmed_hb,
        'total_hb': total_hb, 'hb_no_appt': hb_no_appt,

        'confirmed_dtap': confirmed_dtap, 'unconfirmed_dtap': unconfirmed_dtap,
        'total_dtap': total_dtap, 'dtap_no_appt': dtap_no_appt,

        'confirmed_ipv': confirmed_ipv, 'unconfirmed_ipv': unconfirmed_ipv,
        'total_ipv': total_ipv, 'ipv_no_appt': ipv_no_appt,

        'confirmed_hib': confirmed_hib, 'unconfirmed_hib': unconfirmed_hib,
        'total_hib': total_hib, 'hib_no_appt': hib_no_appt,

        'confirmed_pcv': confirmed_pcv, 'unconfirmed_pcv': unconfirmed_pcv,
        'total_pcv': total_pcv, 'pcv_no_appt': pcv_no_appt,

        'confirmed_rv': confirmed_rv, 'unconfirmed_rv': unconfirmed_rv,
        'total_rv': total_rv, 'rv_no_appt': rv_no_appt,

        'confirmed_msls': confirmed_msls, 'unconfirmed_msls': unconfirmed_msls,
        'total_msls': total_msls, 'msls_no_appt': msls_no_appt,

        'confirmed_mmr': confirmed_mmr, 'unconfirmed_mmr': unconfirmed_mmr,
        'total_mmr': total_mmr, 'mmr_no_appt': mmr_no_appt,

        'confirmed_vrcl': confirmed_vrcl, 'unconfirmed_vrcl': unconfirmed_vrcl,
        'total_vrcl': total_vrcl, 'vrcl_no_appt': vrcl_no_appt,

        'confirmed_flu': confirmed_flu, 'unconfirmed_flu': unconfirmed_flu,
        'total_flu': total_flu, 'flu_no_appt': flu_no_appt,

        'confirmed_jeb': confirmed_jeb, 'unconfirmed_jeb': unconfirmed_jeb,
        'total_jeb': total_jeb, 'jeb_no_appt': jeb_no_appt,

        'confirmed_ha': confirmed_ha, 'unconfirmed_ha': unconfirmed_ha,
        'total_ha': total_ha, 'ha_no_appt': ha_no_appt,

        'confirmed_mng': confirmed_mng, 'unconfirmed_mng': unconfirmed_mng,
        'total_mng': total_mng, 'mng_no_appt': mng_no_appt,

        'confirmed_typ': confirmed_typ, 'unconfirmed_typ': unconfirmed_typ,
        'total_typ': total_typ, 'typ_no_appt': typ_no_appt,

        'confirmed_td': confirmed_td, 'unconfirmed_td': unconfirmed_td,
        'total_td': total_td, 'td_no_appt': td_no_appt,

        'confirmed_hpv': confirmed_hpv, 'unconfirmed_hpv': unconfirmed_hpv,
        'total_hpv': total_hpv, 'hpv_no_appt': hpv_no_appt,
    }
    return render(request, 'tracker/report.html', data)

@login_required(login_url='login')
def dueVax(request):
    patients = Patient.objects.filter(Q(vaccine__in=Vaccine.objects.all()))
    appointments = Appointment.objects.filter(patient__in=patients)
    vaccines = Vaccine.objects.filter(patient__in=patients)
    due_vaccine_patients = vaccines.exclude(date__in=appointments.values('date'))

    vax_filter = dueVaxForm(request.POST or None)
    if request.method == 'POST':
        due_vaccine_patients = due_vaccine_patients.filter(
            due_date__range = [
                vax_filter['date_start'].value(),
                vax_filter['date_end'].value()
            ]
        )

    data = {
        'vaccines': due_vaccine_patients,
        'vax_filter': vax_filter
    }
    
    return render(request, 'tracker/dueVax.html', data)

@login_required(login_url='login')
def dueVaxEmail(request, pk):
    vaccine = Vaccine.objects.get(id=pk)
    email = vaccine.patient.email

    if(request.method == "POST"):
        htmly = get_template('tracker/dueVaxEmailTemplate.html')
        d = {
            'vaccine': vaccine,
        }
        subject, from_email, to = 'BAQNA - Reminder for Due Vaccination w/o Appointment', 'your_email@gmail.com', email
        html_content = htmly.render(d)
        msg = EmailMultiAlternatives(
            subject, html_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        messages.success(request, 'Email Reminder Sent!')
        return redirect('/dueVax/')

    data = {
        'vaccine': vaccine
    }
    return render(request, 'tracker/dueVaxEmail.html', data)


@login_required(login_url='login')
def unconfirmedAppts(request):
    patient = Patient.objects.all()
    physician = Physician.objects.all()
    appointments = Appointment.objects.all()
    unconfirmed_form = UnconfirmedApptsForm(request.POST or None)

    if(request.method == "POST"):

        appointments = Appointment.objects.filter(
            date__range = [
                unconfirmed_form['date_start'].value(),
                unconfirmed_form['date_end'].value()
            ]
        )

    data = {
        'patient': patient, 
        'physician': physician,
        'appointments': appointments,
        'unconfirmed_form': unconfirmed_form,
    }
    
    return render(request, 'tracker/unconfirmedAppts.html', data)

@login_required(login_url='login')
def unconfirmedApptsEmail(request, pk):
    appointment = Appointment.objects.get(id=pk)
    email = appointment.patient.email

    if(request.method == "POST"):
        htmly = get_template('tracker/unconfirmedApptEmailTemplate.html')
        d = {
            'appointment': appointment,
        }
        subject, from_email, to = 'BAQNA - Reminder for Unconfirmed Booked Appointment', 'your_email@gmail.com', email
        html_content = htmly.render(d)
        msg = EmailMultiAlternatives(
            subject, html_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        messages.success(request, 'Email Reminder Sent!')
        return redirect('/unconfirmedAppts/')
        

    data = {
        'appointment': appointment, 
    }

    return render(request, 'tracker/unconfirmedApptsEmail.html', data)

@login_required(login_url='login')
def staffUpdate(request):
    physicians = Physician.objects.all()
    doc_grp = Group.objects.get(name='Doctor')
    physicianFilter = PhysicianFilter(request.GET, queryset=physicians)
    physicians = physicianFilter.qs

    data = {
        'physicians': physicians, 'physicianFilter': physicianFilter,
    }

    return render(request, 'tracker/staffUpdate.html', data)


@login_required(login_url='login')
def staffUpdateEdit(request, pk):
    physician = Physician.objects.get(id=pk)
    staff_create_form = StaffUpdateForm(instance=physician.user)
    doc_user_form = DoctorForm(instance=physician)

    if(request.method == "POST"):
        staff_create_form = StaffUpdateForm(request.POST, instance=physician.user)
        doc_user_form = DoctorForm(request.POST, instance=physician)

        if staff_create_form.is_valid() and doc_user_form.is_valid():
            staff_create_form.save()
            doc_user_form.save()
            messages.success(request, 'Staff details have been saved.')
        else:
            messages.error(request, staff_create_form.errors)

        return redirect('/staffUpdate/')
    
    data = {
        'physician': physician,
        'staff_create_form': staff_create_form,
        'doc_user_form': doc_user_form,
    }

    return render(request, 'tracker/staffUpdateEdit.html', data)

@login_required(login_url='login')
def staffUpdateEditPass(request, pk):
    physician = Physician.objects.get(id=pk)
    password_form = PasswordChangeForm(physician.user)

    if(request.method == "POST"):
        password_form = PasswordChangeForm(physician.user, request.POST)

        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password Changed!')
        else:
            messages.error(request, password_form.errors)
        
        return redirect('/staffUpdate/')

    data = {
        'physician': physician,
        'password_form': password_form,
    }

    return render(request, 'tracker/staffUpdateEditPass.html', data)


@login_required(login_url='login')
def staffCreate(request):
    doc_grp = Group.objects.get(name='Doctor')
    staff_create_form = StaffCreateForm()
    doc_user_form = DoctorForm()
    if request.method == 'POST':
        staff_create_form = StaffCreateForm(request.POST)
        doc_user_form = DoctorForm(request.POST)
        if User.objects.filter(username = request.POST['username']).exists():
            messages.error(request, 'Username exists.')
        else:
            if staff_create_form.is_valid() and doc_user_form.is_valid():
                #staff_create_form.save()
                user = staff_create_form.save()
                profile = doc_user_form.save(commit=False)
                profile.user = user
                profile.save()
                doc_grp.user_set.add(user)
                messages.success(request, 'Account Created!')
        return redirect('/staffCreate/')
    
    data = {
        'staff_create_form': staff_create_form,
        'doc_user_form': doc_user_form,
    }

    return render(request, 'tracker/staffCreate.html', data)
