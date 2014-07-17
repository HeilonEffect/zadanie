import json
import random
import re

from django.test import TestCase
from django.test.client import Client

from .models import tables, sources


class MainPageTest(TestCase):
    fixtures = ['users.json', 'rooms.json']

    def setUp(self):
        self.client = Client()

    def test_main_page_available(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_tablenames(self):
        response = self.client.get('/tablenames')
        self.assertEqual(response.status_code, 200)
        names = json.dumps([sources[item]['title'] for item in sources],
                           ensure_ascii=False)
        self.assertEqual(str(response.content, 'utf-8'), names)

    def test_table_columns(self):
        for table in tables:
            response = self.client.get('/%s' % sources[table]['title'])

            self.assertEqual(response.status_code, 200)

            kwargs = [item['id'] for item in sources[table]['fields']]
            data = tables[table].objects.values(*kwargs)
            for i, item in enumerate(
                    json.loads(str(response.content, 'utf-8'))['data']):
                for key in item:
                    self.assertEqual(sorted(item), sorted(
                                     [str(data[i][key]) for key in data[i]]))

        response = self.client.get('/sfsdfdsfsd')
        self.assertEqual(response.status_code, 404)

    def test_add_value(self):
        convert = {'int': 1, 'char': 'aaa', 'date': 'Jul 03 2014'}
        for table in tables:
            data = {}
            for item in sources[table]['fields']:
                data[item['id']] = convert[item['type']]

            response = self.client.post(
                '/add/%s' % sources[table]['title'], data)
            self.assertEqual(response.status_code, 200)

            data = {}
            response = self.client.post(
                '/add/%s' % sources[table]['title'], {})
            self.assertEqual(response.status_code, 500)

    def test_edit_value(self):
        for table in tables:
            vals = tables[table].objects.values()
            old = vals[0]
            key = random.choice([key for key in old.keys()])
            new_val = random.choice(tables[table].objects.values(key))

            for key in old:
                old[key] = str(old[key])
            for key in new_val:
                new_val[key] = str(new_val[key])

            response = self.client.post('/put/%s' % sources[table]['title'],
                                        {'old': json.dumps(old),
                                         'new_val': json.dumps(new_val)})
            self.assertEqual(response.status_code, 200)

            for key in old:
                if isinstance(old[key], int):
                    for k in new_val:
                        new_val[k] = 'qwerty'

            response = self.client.post('/put/%s' % sources[table]['title'],
                                        {'old': json.dumps(old),
                                         'new_val': json.dumps(new_val)})
            self.assertEqual(response.status_code, 200)

            response = self.client.post('/put/%s' % sources[table]['title'], {})
            self.assertEqual(response.status_code, 500)

            # response = self.client.post
