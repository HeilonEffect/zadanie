import json

from django.http import HttpResponse, HttpResponseNotFound
from django.http import HttpResponseServerError
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from myapp.models import tables, sources
from myapp.forms import myforms


def index(request):
    return render(request, 'base.html')


def tablenames(request):
    names = json.dumps([sources[item]['title'] for item in sources],
                       ensure_ascii=False)
    return HttpResponse(names, content_type='application/json')


def table_columns(request, table):
    convert = {'int': 'number', 'char': 'text', 'date': 'date',
               'number': 'number', 'text': 'text'}
    try:
        for key in sources:
            if sources[key]['title'] == table:
                src = sources[key]['fields']

                result = {}
                result['columns'] = src
                for column in result['columns']:
                    column['type'] = convert[column['type']]
                    column['result'] = ''
                kwargs = [item['id'] for item in sources[key]['fields']]
                result['data'] = list(tables[key].objects.values(*kwargs)) or list()
                print(result['data'])
                for item in result['data']:
                    for key in item:
                        if str(item[key]).find('datetime'):
                            item[key] = str(item[key])
                js = json.dumps(result, ensure_ascii=False)
                return HttpResponse(js, content_type='application/json')
        return HttpResponseNotFound()
    except Exception as e:
        print(e)
        return HttpResponse()


@csrf_exempt
def add_value(request, table):
    try:
        for key in sources:
            if sources[key]['title'] == table:
                form = myforms['%sForm' % key](request.POST)
                if form.is_valid():
                    cd = form.cleaned_data
                    tables[key].objects.create(**cd)
                else:
                    print(request.POST)
                    print('invalid')
                    print(form.errors)
        return HttpResponse()
    except Exception as e:
        print(e)
        return HttpResponse()
