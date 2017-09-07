from datetime import datetime
import json
import csv
import requests
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
#from employee.models import UserProfile
from app.pybamboohrextension import PyBambooHRExt
from requests.exceptions import HTTPError
from django.utils.dateparse import parse_date
from django.urls import reverse
import os
from django.core.files.storage import default_storage
from django.http import StreamingHttpResponse, FileResponse
import zipfile
import shutil
from wsgiref.util import FileWrapper
from django.contrib import messages
import category.views as category_views

def all(request):
    #user_profile = UserProfile.objects.first()
    bamboo = PyBambooHRExt(subdomain=request.session['sub_domain'], api_key=request.session['api_key'])

    employees = bamboo.get_employee_directory()
    try:
        list = bamboo.employee_files_categories(employees[0]['id']);

        return HttpResponse(content_type="application/json; charset=utf-8", content=json.dumps(employees))
    except HTTPError as e:
        return HttpResponse(status=e.code)

def type(request):
    bamboo = PyBambooHRExt(subdomain=request.session['sub_domain'], api_key=request.session['api_key'])

    employees = bamboo.request_custom_report(report_format='json', field_list=['id', 'displayName', 'location', 'status'])
    try:
        return HttpResponse(content_type="application/json; charset=utf-8", content=json.dumps(employees))
    except HTTPError as e:
        return HttpResponse(status=e.code)

def upload_file(request):
    file_upload_response = {'model':{'success':False}}
    if request.method == 'POST' and request.FILES['myfile']:
        #user_profile = UserProfile.objects.first()
        bamboo = PyBambooHRExt(subdomain=request.session['sub_domain'], api_key=request.session['api_key'])
        employee_id = request.POST['employee_id']
        category_id = request.POST['category_id']
        file_type = request.POST['file_type']
        signed_date = parse_date(request.POST['signed_date'])
        myfile = request.FILES['myfile']
        file_path = default_storage.path('tmp/' + myfile.name)

        # check if file is already present
        employee_categories = bamboo.employee_files_categories(employee_id)
        for category in employee_categories['employee']['category']:
            if category['id'] == category_id:
                if category.get('file', None):
                    files = category['file']
                    if isinstance(files, list):
                        for file in files:
                            if len(file['name'].split('_')) > 2:
                                if file['name'].split('_')[1] == file_type and file['originalFileName'] == myfile.name:
                                    bamboo.delete_file(employee_id=employee_id, file_id=file['id'])
                    else:
                        if len(files['name'].split('_')) > 2:
                            if files['name'].split('_')[1] == file_type and files['originalFileName'] == myfile.name:
                                bamboo.delete_file(employee_id=employee_id, file_id=files['id'])
                break

        override_name = "{}_{}_{}".format(signed_date.strftime('%Y.%m.%d'), file_type, employee_id)

        try:
            bamboo.upload_employee_file(employee_id, file_path, category_id, True, override_file_name=override_name)
            file_upload_response['model']['success'] = True
        except Exception:
            return render(request, 'employee/single-profile.html', file_upload_response)

        return render(request, 'employee/single-profile.html', file_upload_response)

    return HttpResponse(status_code=400)

def info(request):
    employee_id = request.GET['employee_id']
    #user_profile = UserProfile.objects.first()
    bamboo = PyBambooHRExt(subdomain=request.session['sub_domain'], api_key=request.session['api_key'])
    try:
        employee = bamboo.get_employee(employee_id=employee_id, field_list=['employeeNumber'])
        return HttpResponse(content_type="application/json; charset=utf-8", content=json.dumps(employee))
    except HTTPError as e:
        return HttpResponse(status=404)


    return HttpResponse(status=400)

def home(request):
    host = request.get_host()
    all(request)

    category_response = category_views.all(request)
    employee_response = all(request)
    employee_type = type(request)

    response_model = {
        'file_types':{},
        'employees':{},
        'employees_all':{},
        'id': request.session.get('employee_id')
    }

    if category_response.status_code == 200:
        response_model['file_types'] = json.loads(category_response.content)
    # if employee_response.status_code == 200:
    #     response_model['employees'] = json.loads(employee_response.content)
    if employee_type.status_code == 200:
        response_model['employees'] = json.loads(employee_type.content)['employees']

    if request.method == 'POST' and request.FILES.get('myfile', None):
        myfile = request.FILES['myfile']
        with open(default_storage.path('tmp/' + myfile.name), 'wb+') as destination:
            for chunk in myfile.chunks():
                destination.write(chunk)
        #user_profile = UserProfile.objects.first()
        bamboo = PyBambooHRExt(subdomain=request.session['sub_domain'], api_key=request.session['api_key'])
        employee_id = request.POST['employee_id']
        request.session['employee_id'] = employee_id
        employee = bamboo.get_employee(employee_id=employee_id, field_list=['employeeNumber', 'firstName', 'lastName'])
        category_id_string = request.POST['category_id']
        category_id = category_id_string.split('#')[0]
        file_type = category_id_string.split('#')[1]
        signed_date = parse_date(request.POST['signed_date'])
        file_path = default_storage.path('tmp/' + myfile.name)

        override_name = "{}_{}_{}_{}_{}".format(signed_date.strftime('%Y.%m.%d'), file_type, employee['employeeNumber'], employee['lastName'], employee['firstName'])

        #check if file is already present
        employee_categories = bamboo.employee_files_categories(employee['id'])
        for category in employee_categories['employee']['category']:
            if category['id'] == category_id:
                if category.get('file', None):
                    files = category['file']
                    if isinstance(files, list):
                        for file in files:
                            if len(file['name'].split('_')) > 2:
                                if file['name'].split('_')[1] == file_type and file['originalFileName'] == myfile.name:
                                    bamboo.delete_file(employee_id=employee_id, file_id=file['id'])
                    else:
                        if len(files['name'].split('_')) > 2:
                            if files['name'].split('_')[1] == file_type and files['originalFileName'] == myfile.name:
                                bamboo.delete_file(employee_id=employee_id, file_id=files['id'])
                break


        try:
            bamboo.upload_employee_file(employee_id, file_path, category_id, True, override_file_name=override_name)
            response_model['upload_success'] = 'File successfully uploaded!'

            messages.success(request, 'File successfully uploaded!')
            os.remove(default_storage.path('tmp/' + myfile.name))
        except HTTPError as e:
            os.remove(default_storage.path('tmp/' + myfile.name))
            response_model['upload_success'] = 'File can not be uploaded!'

            messages.error(request, 'File can not be uploaded!')
            return HttpResponseRedirect('home')

        return HttpResponseRedirect('home')

    return render(request, 'employee/single-profile.html', response_model)

def document_download(request):
    if request.method == "GET":
        response_model = {
            'file_types': {},
            'employee_list': {}
        }

        category_url = request.build_absolute_uri(reverse('all_categories'))
        category_response = category_views.all(request)

        if category_response.status_code == 200:
            response_model['file_types'] = json.loads(category_response.content)

        return render(request, 'employee/document-download.html', response_model)

    category_id_string = request.POST['category_id']
    category_id = category_id_string.split('#')[0]
    file_type = category_id_string.split('#')[1]


    employee_url = request.build_absolute_uri(reverse('all_employee'))

    if request.POST['employee_type']=='Active':
        employee_response = all(request)
        if employee_response.status_code == 200:
            employee_list = json.loads(employee_response.content)
    else:
        employee_response = type(request)
        if employee_response.status_code == 200:
            employee_list = json.loads(employee_response.content)['employees']

    category_url = request.build_absolute_uri(reverse('all_categories'))
    category_response = category_views.all(request)

    response_model = {
        'file_types': {},
        'employee_list': {}
    }

    if category_response.status_code == 200:
        response_model['file_types'] = json.loads(category_response.content)

    bamboo = PyBambooHRExt(subdomain=request.session['sub_domain'], api_key=request.session['api_key'])

    for employee in employee_list:
        try:
            #print(employee['id'])
            employee_categories = bamboo.employee_files_categories(employee['id'])
            for category in employee_categories['employee']['category']:
                if category['id'] == category_id:
                    if category.get('file', None):
                        files = category['file']
                        if isinstance(files, list):
                            for file in files:
                                if len(file['name'].split('_')) > 2:
                                    if file['name'].split('_')[1] == file_type:
                                        file_content = bamboo.download_file(employee['id'], file['id'])
                                        with open(default_storage.path('tmp/' + file['name'] + os.path.splitext(file['originalFileName'])[1]), 'wb+') as destination:
                                            destination.write(file_content)
                            break
                        else:
                            if len(files['name'].split('_')) > 2:
                                if files['name'].split('_')[1] == file_type:
                                    file_content = bamboo.download_file(employee['id'], files['id'])
                                    with open(default_storage.path('tmp/' + files['name'] + os.path.splitext(files['originalFileName'])[1]), 'wb+') as destination:
                                        destination.write(file_content)




        except HTTPError as e:
            #os.remove(default_storage.path('tmp/' + myfile.name))
            response_model['upload_success'] = 'File can not be uploaded!'
            return render(request, 'employee/document-download.html', response_model)


    # if employee_response.status_code == 200:
    #     response_model['employees'] = json.loads(employee_response.content)

    shutil.make_archive("files", 'zip', root_dir=default_storage.path('tmp/'), )
    delete_files_folders(default_storage.path('tmp/'))

    # os.remove(default_storage.path('tmp/' + "2017.07.21_Pass_4"))

    response = HttpResponse(FixedFileWrapper(open(default_storage.path('files.zip'), 'rb')),
                            content_type="application/x-zip-compressed")
    # response['Content-Length'] = os.path.getsize(open(default_storage.path('files.zip')))
    response['Content-Disposition'] = "attachment; filename=%s" % "files.zip"
    # response = FileResponse(default_storage.path('files.zip'), 'rb')
    # response = StreamingHttpResponse(file_content, content_type="text/plain")
    # response['Content-Disposition'] = 'attachment; filename="somefilename.zip"'

    os.remove(default_storage.path('files.zip'))



    return response

def backup(request):
    response_model = {
        'file_types': {},
        'employees': {}
    }

    employee_url = request.build_absolute_uri(reverse('all_employee'))

    if (request.method == 'POST' and request.POST['employee_type']=='All'):
        employee_response = type(request)
        if employee_response.status_code == 200:
            response_model['employees'] = json.loads(employee_response.content)['employees']
    else:
        employee_response = all(request)
        if employee_response.status_code == 200:
            response_model['employees'] = json.loads(employee_response.content)

    category_url = request.build_absolute_uri(reverse('all_categories'))
    category_response = category_views.all(request)

    if category_response.status_code == 200:
        response_model['file_types'] = json.loads(category_response.content)

    if request.method == "GET":
        return render(request, 'employee/backup.html', response_model)

    bamboo = PyBambooHRExt(subdomain=request.session['sub_domain'], api_key=request.session['api_key'])

    for employee in response_model['employees']:
        employee_categories = bamboo.employee_files_categories(employee['id'])
        for category in employee_categories['employee']['category']:
            category_name = category['name']
            directory = default_storage.path('tmp/'+ employee["displayName"] + '/' + category_name)
            if not os.path.exists(directory):
                os.makedirs(directory)
            if category.get('file', None):
                files = category['file']
                if isinstance(files, list):
                    for file in files:
                        file_content = bamboo.download_file(employee['id'], file['id'])
                        with open(directory + "/" + file['name'] + os.path.splitext(file['originalFileName'])[1], 'wb+') as destination:
                            destination.write(file_content)

                else:
                    file_content = bamboo.download_file(employee['id'], files['id'])
                    with open(default_storage.path(directory + '/' + files['name'] + os.path.splitext(files['originalFileName'])[1]), 'wb+') as destination:
                        destination.write(file_content)

    shutil.make_archive("files", 'zip', root_dir=default_storage.path('tmp/'), )
    delete_files_folders(default_storage.path('tmp/'))

    response = HttpResponse(FixedFileWrapper(open(default_storage.path('files.zip'), 'rb')),
                            content_type="application/x-zip-compressed")
    response['Content-Disposition'] = "attachment; filename=%s" % "files.zip"

    os.remove(default_storage.path('files.zip'))

    return response

def report(request):
    response_model = {
        'file_types': {},
        'employees': {},
        'test': {}
    }

    employee_url = request.build_absolute_uri(reverse('all_employee'))

    category_url = request.build_absolute_uri(reverse('all_categories'))
    category_response = category_views.all(request)

    if category_response.status_code == 200:
        response_model['file_types'] = json.loads(category_response.content)


    employee_response = type(request)
    if employee_response.status_code == 200:
        response_model['employees'] = json.loads(employee_response.content)['employees']
    # else:
    #     employee_response = all(request)
    #     if employee_response.status_code == 200:
    #         response_model['employees'] = json.loads(employee_response.content)

    if employee_response.status_code == 200:

        #user_profile = UserProfile.objects.first()
        bamboo = PyBambooHRExt(subdomain=request.session['sub_domain'], api_key=request.session['api_key'])

        if request.method == "POST":
            with open(default_storage.path('tmp/report.csv'), "w+") as rfile:
                csv_file = csv.writer(rfile, quoting=csv.QUOTE_ALL)

                employee_header = ['Name', 'Employee #', 'Location', 'Status', 'Contract Status']
                index_map = 5
                index_dictionary = {}
                for cat in response_model['file_types']['file_types']:
                    employee_header.append(cat['name'].replace("-", "/", 1))
                    category_name = cat['name'].split('-')[0].strip()
                    file_type = cat['name'].split('-')[1].strip()
                    index_dictionary[category_name + "/" + file_type] = index_map
                    #print(category_name + "/" + file_type)
                    index_map = index_map + 1
                csv_file.writerow(employee_header)


                for employee in response_model['employees']:
                    employee_row = [''] * index_map
                    employee_row[0] = employee['displayName']

                    if (request.POST['employee_type'] == 'Active' and employee['status'] != 'Active'):
                        continue

                    employee_hashID = bamboo.get_employee(employee_id=employee['id'], field_list=['employeeNumber'])
                    if employee_hashID.get('employeeNumber', None):
                        employee_row[1] = employee_hashID['employeeNumber']
                    else:
                        employee_row[1] = ''

                    employee_row[2] = employee['location']
                    employee_row[3] = employee['status']
                    employee_row[4] = ''

                    employee_categories = bamboo.employee_files_categories(employee['id'])

                    for category in employee_categories['employee']['category']:
                        flist = ""
                        if category.get('file', None):
                            files = category['file']
                            category_name = category['name']

                            if isinstance(files, list):
                                for file in files:
                                    if len(file['name'].split('_')) > 2:
                                        file_type = file['name'].split('_')[1]
                                        key = category_name + "/" + file_type
                                        #print(">>>>>> " + key +  ' ' + category['name'] + ' ' + file_type)
                                        if index_dictionary.get(key, None):
                                            key_index = index_dictionary[key]
                                            new_file_name = file['name'] + '.' + file['originalFileName'].split('.')[-1]
                                            if employee_row[key_index]:
                                                employee_row[key_index]  = employee_row[key_index] + '\n' + new_file_name
                                            else:
                                                employee_row[key_index] = new_file_name

                            else:
                                if len(files['name'].split('_')) > 2:
                                    file_type = files['name'].split('_')[1]
                                    key = category_name + "/" + file_type
                                    if index_dictionary.get(key, None):
                                        key_index = index_dictionary[key]
                                        new_file_name = files['name'] + '.' + files['originalFileName'].split('.')[-1]
                                        if employee_row[key_index]:
                                            employee_row[key_index] = employee_row[key_index] + '\n' + new_file_name
                                        else:
                                            employee_row[key_index] = new_file_name
                    csv_file.writerow(employee_row)
                        # employee_row.append(flist)



            with open('tmp/report.csv', 'rb') as rfile:
                response = HttpResponse(rfile, content_type='text/csv')
                response['Content-Disposition'] = "attachment; filename=%s" % "report.csv"

                delete_files_folders(default_storage.path('tmp/'))

                return response

    return render(request, 'employee/report.html', response_model)

def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))

def delete_files_folders(folder):
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path): shutil.rmtree(file_path)
        except Exception as e:
            print(e)

class FixedFileWrapper(FileWrapper):
    def __iter__(self):
        self.filelike.seek(0)
        return self