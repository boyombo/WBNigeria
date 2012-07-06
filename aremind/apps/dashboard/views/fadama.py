from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def dashboard(request):
    return render(request, 'dashboard/fadama/dashboard.html')


@login_required
def reports(request):
    return render(request, 'dashboard/fadama/reports.html')


@login_required
def site_detail(request, pk):
    return render(request, 'dashboard/fadama/site_detail.html')