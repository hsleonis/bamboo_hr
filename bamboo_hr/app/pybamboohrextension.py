import xml.etree.ElementTree
from xml.etree import ElementTree

import requests
from PyBambooHR import PyBambooHR
import json
from app import utils
import xmltodict

class PyBambooHRExt(PyBambooHR.PyBambooHR):

    def add_custom_field(self, field):
        self.employee_fields[field] = 'Custom field ' + field

        return True

    def get_company_files_categories(self):
        url = self.base_url + 'files/view/'
        print(url)

        response = requests.get(url, headers=self.headers, auth=(self.api_key, ''))
        response.raise_for_status()

        #print(xml.etree.ElementTree.fromstring(response.content))
        obj = json.loads(json.dumps(xmltodict.parse(response.content)))
        #print(obj)
        #return utils.make_dict_from_tree(xml.etree.ElementTree.fromstring(response.content))
        return obj

    def download_company_file(self, file_id):
        url = self.base_url + "files/{0}/".format(file_id)
        r = requests.get(url, headers=self.headers, auth=(self.api_key, ''))
        print(r.status_code)
        r.raise_for_status()

        # print r.text
        #file = r.content
        return r.content

    def employee_files_categories(self, employee_id):
        payload = {
        }
        url = self.base_url + "employees/{0}".format(employee_id) + '/files/view/'
        response = requests.get(url, headers=self.headers, params=payload, auth=(self.api_key, ''))
        #print(response.content)
        response.raise_for_status()

        return utils.make_dict_from_tree(xml.etree.ElementTree.fromstring(response.content))

    def download_file(self, employee_id, fileID):
        payload = {
        }
        url = self.base_url + "employees/{0}/files/{1}/".format(employee_id, fileID)
        r = requests.get(url, headers=self.headers, params=payload, auth=(self.api_key, ''))
        r.raise_for_status()

        # print r.text
        file = r.content
        return file

    def delete_file(self, employee_id, file_id):
        url = self.base_url + "employees/{}/files/{}/".format(employee_id, file_id)
        response = requests.delete(url, headers=self.headers, auth=(self.api_key, ''))
        response.raise_for_status()

        return True
