from django.db import models
from django.db.models.base import ModelBase
from django.contrib import admin

import yaml

types = {'char': models.CharField(max_length=255),
         'date': models.DateField(),
         'int': models.IntegerField()}

tables = {}
sources = {}

with open('myapp/primer.yaml') as f:
    data = yaml.load(f)
    sources = data

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
