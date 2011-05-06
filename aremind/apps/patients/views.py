import logging

from django import http
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import mail_admins
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

from aremind.decorators import has_perm_or_basicauth
from aremind.apps.patients import models as patients
from aremind.apps.patients.forms import PatientRemindersForm
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
    context = {'patients': patients.Patient.objects.all()}
    return render(request, 'patients/patient_list.html', context)



@login_required
def view_patient(request, patient_id):
    patient = get_object_or_404(patients.Patient, pk=patient_id)
    if request.method == 'POST':
        form = PatientRemindersForm(request.POST, instance=patient)
        if form.is_valid():
            messages.info(request, "Patient info saved.")
            return redirect('patient-list')
    else:
        form = PatientRemindersForm(instance=patient)
    context = {'patient': patient, 'form': form}
    return render(request, 'patients/patient_detail.html', context)

