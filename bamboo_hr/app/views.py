from django.shortcuts import render, redirect
from django.http import HttpResponse
#from employee.models import UserProfile


def login(request):
    if(request.method == "POST"):
        return HttpResponse(request.POST.get("api_key", "pai nai"))

    return render(request, 'app/login.html')

def setup(request):
    if(request.method == "POST"):
        api_key = request.POST.get('api_key')
        sub_domain = request.POST.get('sub_domain')
        if api_key and sub_domain:
            request.session['api_key'] = api_key
            request.session['sub_domain'] = sub_domain
            request.session.set_expiry(0)
            #UserProfile.objects.create(api_key=api_key, sub_domain=sub_domain)
            return redirect('/employee/home')

    return render(request, 'app/setup.html')