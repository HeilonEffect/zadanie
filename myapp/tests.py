import json

from django.test import TestCase
from django.test.client import Client

# Create your tests here.
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
