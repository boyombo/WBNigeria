import datetime
import logging

from django import http
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import mail_admins
from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

from rapidsms.messages import OutgoingMessage
from threadless_router.router import Router

from aremind.decorators import has_perm_or_basicauth
from aremind.apps.adherence.app import make_tree_for_day, start_tree_for_patient
from aremind.apps.adherence.models import get_contact_message
from aremind.apps.patients import models as patients
from aremind.apps.patients.forms import PatientRemindersForm, PatientOnetimeMessageForm, PillHistoryForm
from aremind.apps.patients.importer import parse_payload


logger = logging.getLogger('aremind.apps.patients')


@csrf_exempt
@require_http_methods(['POST'])
@has_perm_or_basicauth('patients.add_patientdatapayload', 'Patients')
def receive_patient_record(request):
    ''' Accept data submissions from the the site via POST. '''
    if request.META['CONTENT_TYPE'] != 'text/xml':
        logger.warn('incoming post does not have text/xml content type')
        logger.debug(request)
    content = request.raw_post_data
    if not content:
        logger.error("No XML data appears to be attached.")
        return http.HttpResponseServerError("No XML data appears to be attached.")
    payload = patients.PatientDataPayload.objects.create(raw_data=content)
    try:
        parse_payload(payload)
    except Exception as e:
        mail_admins(subject="Patient Import Failed", message=unicode(e))
        return http.HttpResponseServerError(unicode(e))
    return http.HttpResponse("Data submitted succesfully.")


@login_required
def list_patients(request):
    patients_list = patients.Patient.objects.all().annotate(
        reminder_count=Count('contact__reminders', distinct=True),
        feed_count=Count('contact__feeds', distinct=True)
    )
    context = {'patients': patients_list}
    return render(request, 'patients/patient_list.html', context)



@login_required
def create_edit_patient(request, patient_id=None):
    if patient_id:
        patient = get_object_or_404(patients.Patient, pk=patient_id)
    else:
        patient = patients.Patient()
    if request.method == 'POST':
        form = PatientRemindersForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            messages.info(request, "Patient info saved.")
            return redirect('patient-list')
    else:
        form = PatientRemindersForm(instance=patient)
    context = {'patient': patient, 'form': form}
    return render(request, 'patients/create_edit_patient.html', context)


@login_required
def patient_onetime_message(request, patient_id):
    """Send a onetime message to a patient.
    Default to getting it from their feeds but allow editing that."""

    patient = get_object_or_404(patients.Patient, pk=patient_id)
    if request.method == 'POST':
        form = PatientOnetimeMessageForm(request.POST)
        if form.is_valid():
            message = form.cleaned_data['message']
            connection = patient.contact.default_connection
            msg = OutgoingMessage(connection, message)
            router = Router()
            success = True
            try:
                router.outgoing(msg)
            except Exception, e:
                logger.exception(e)
                success = False
            if success:
                messages.success(request, "Message sent to patient %s" % patient.subject_number)
            else:
                messages.error(request, "An error occurred while trying to send the message to patient %s" % patient.subject_number)

            return redirect('patient-list')
    else:
        # Set default message
        message = get_contact_message(patient.contact)
        form = PatientOnetimeMessageForm(initial={'message': message})
    context = { 'patient': patient, 'form': form }
    return render(request, 'patients/patient_onetime_message.html', context)


# FIXME: This might just be for testing - take out later?
@login_required
def patient_start_adherence_tree(request, patient_id):
    """Start adherence tree interaction with patient."""
    patient = get_object_or_404(patients.Patient, pk=patient_id)
    tree = make_tree_for_day(datetime.date.today())
    start_tree_for_patient(tree, patient)
    return redirect('/httptester/httptester/%s/' % patient.contact.default_connection.identity)


@login_required
def patient_pill_report(request, patient_id):
    patient = get_object_or_404(patients.Patient, pk=patient_id)
    pills = patients.PatientPillsTaken.objects.filter(patient=patient).order_by('-date')
    context = {'patient': patient, 'pills': pills}
    return render(request, 'patients/patient_pill_report.html', context)


@login_required
def create_edit_pill_history(request, patient_id, pill_id=None):
    if pill_id:
        pill = get_object_or_404(patients.PatientPillsTaken, pk=pill_id, patient=patient_id)
        patient = pill.patient
    else:
        patient = get_object_or_404(patients.Patient, pk=patient_id)
        pill = patients.PatientPillsTaken(patient=patient)
    if request.method == 'POST':
        form = PillHistoryForm(request.POST, instance=pill)
        if form.is_valid():
            pill = form.save()
            messages.success(request, "Pill history saved.")
            return redirect('patient-report', patient_id)
    else:
        form = PillHistoryForm(instance=pill)
    context = {'patient': patient, 'pill': pill, 'form': form}
    return render(request, 'patients/create_edit_pill_history.html', context)


@login_required
def pill_history_data(request, patient_id):
    pass
