from django.http import HttpResponse
from app import pybamboohrextension
#from employee.models import UserProfile
from requests.exceptions import HTTPError
from django.conf import settings
import json

def list_of_folders_from_file(file_content):
    return [folder.strip() for folder in file_content.split(',')]


def all(request):
    #user_profile = UserProfile.objects.first()

    bamboo = pybamboohrextension.PyBambooHRExt(subdomain=request.session['sub_domain'], api_key=request.session['api_key'])

    try:
        file_id = ''
        file_category_dictionary = bamboo.get_company_files_categories();
        file_date = None
        for category in file_category_dictionary['files']['category']:
            # print(json.dumps(category))
            files = category.get('file', None)
            if files:
                for file in category.get('file', None):
                    if file['name'] == 'file_folders_list_dont_delete.txt':
                        if file_date:
                            date_created = file['dateCreated']
                            if date_created > file_date:
                                file_id = file['id']
                                file_date = date_created
                        else:
                            file_date = file['dateCreated']
                            file_id = file['id']

        # print('########')
        # print(file_id)
        # print('@@@@@@@@@@')
        # print(file_category_dictionary)
        if file_id is None:
            return HttpResponse(status=404)

        employees = bamboo.get_employee_directory()
        try:
            employee_categories = bamboo.employee_files_categories(employees[0]['id']);
            category_id_dic = {}
            for category in employee_categories['employee']['category']:
                category_id_dic[category['name']] = category['id']
                # print('here ' + category['name'])

            file_content = bamboo.download_company_file(file_id).decode('utf-8')
            file_types = [file_type.strip() for file_type in file_content.split(',')]

            categor_mapper = {

            }

            for file_type in file_types:
                file_type_parts = file_type.split('-')
                if len(file_type_parts) == 2:
                    category_name = file_type_parts[0].strip()
                    # print(category_name)

                    file_type_name = file_type_parts[1].strip()
                    if category_id_dic.get(category_name, None):
                        categor_mapper[category_name] = {
                            'id': category_id_dic[category_name],
                            'file_types': [],
                        }
                else:
                    if len(file_type_parts) > 2:
                        category_name = file_type_parts[0].strip()

                        file_type_len = len(file_type_parts) - 1
                        for i in range(1, file_type_len):
                            category_name = category_name + ' - ' + file_type_parts[i].strip()

                        file_type_name = file_type_parts[file_type_len].strip()

                        if category_id_dic.get(category_name, None):
                            categor_mapper[category_name] = {
                                'id': category_id_dic[category_name],
                                'file_types': [],
                            }

            response_dic = {
                'file_types': []
            }

            for file_type in file_types:
                file_type_parts = file_type.split('-')
                if len(file_type_parts) == 2:
                    category_name = file_type_parts[0].strip()
                    file_type_name = file_type_parts[1].strip()
                    # print(category_name)
                    # print(file_type_name)
                    #if category_name != 'Core' and category_name != 'ID':
                        #continue
                    if categor_mapper.get(category_name, None) is None:
                        continue
                    file_type_dic = {}
                    file_type_dic['id'] = categor_mapper[category_name]['id'] + "#" + file_type_name
                    file_type_dic['name'] = file_type
                    response_dic['file_types'].append(file_type_dic)
                else:
                    if len(file_type_parts) > 2:
                        category_name = file_type_parts[0].strip()

                        file_type_len = len(file_type_parts) - 1
                        for i in range(1, file_type_len):
                            category_name = category_name + ' - ' + file_type_parts[i].strip()

                        file_type_name = file_type_parts[file_type_len].strip()
                        # print(category_name)
                        # print(file_type_name)
                        # if category_name != 'Core' and category_name != 'ID':
                        # continue
                        if categor_mapper.get(category_name, None) is None:
                            continue
                        file_type_dic = {}
                        file_type_dic['id'] = categor_mapper[category_name]['id'] + "#" + file_type_name
                        file_type_dic['name'] = file_type
                        response_dic['file_types'].append(file_type_dic)


        except HTTPError as e:
            return HttpResponse(status=e.code)
        #print(json.dumps(file_category_dictionary))
        # return HttpResponse(json.dumps(file_category_dictionary, sort_keys=True, indent=4))


        return HttpResponse(content_type="application/json; charset=utf-8", content=json.dumps(response_dic))
    except HTTPError as e:
        return HttpResponse(status=404)

    return HttpResponse('file_category_dictionary');

def add(request):
    pass

