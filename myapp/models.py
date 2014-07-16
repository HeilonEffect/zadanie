import xml.etree.ElementTree as ET

from django.db import models
from django.db.models.base import ModelBase
from django.contrib import admin

import yaml

types = {'char': models.CharField(max_length=255),
         'date': models.DateField(),
         'int': models.IntegerField()}

tables = {}
sources = {}

data = None

try:
    with open('myapp/primer.xml') as f:
        tree = ET.parse(f)
        root = tree.getroot()
        data = {}
        for child in root:
            data[child.tag] = {}
            data[child.tag]['title'] = child[0].text
            data[child.tag]['fields'] = []
            one, *fields = child
            for field in fields:
                tmp = {}
                for item in field:
                    tmp[item.tag] = item.text
                data[child.tag]['fields'].append(tmp)
except IOError as e:
    with open('myapp/primer.yaml') as f:
        data = yaml.load(f)

sources = data
if data:
    for item in data:
        db_name = item

        # Устанавливаем нужные атрибуты
        attrs = {'__module__': 'myapp.models'}
        for field in data[item]['fields']:
            # А так криво сделано потому, что иначе столбцы как-то
            # накладывались друг на друга
            if field['type'] == 'int':
                attrs[field['id']] = models.IntegerField()
            elif field['type'] == 'date':
                attrs[field['id']] = models.DateField()
            elif field['type'] == 'char':
                attrs[field['id']] = models.CharField(max_length=255)

        tmp = ModelBase.__new__(ModelBase, db_name, (models.Model, ), attrs)
        tables[db_name] = tmp
