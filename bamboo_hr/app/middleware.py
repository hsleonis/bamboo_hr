from django.shortcuts import HttpResponseRedirect
#from employee.models import UserProfile

class InitialSetupRequiredMiddleWare(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)


        if request.path.startswith('/setup'):
            return response

        #if UserProfile.objects.count() == 0:

        if 'api_key' not in request.session:
            return HttpResponseRedirect('/setup/')

        return response