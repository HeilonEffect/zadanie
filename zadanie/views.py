import json

from django.http import HttpResponse, HttpResponseNotFound
from django.http import HttpResponseServerError
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt

from myapp.models import tables, sources
from myapp.forms import myforms


def index(request):
    return render_to_response('base.html')


def tablenames(request):
    names = json.dumps([sources[item]['title'] for item in sources],
                       ensure_ascii=False)
    return HttpResponse(names, content_type='application/json')


def table_columns(request, table):
    convert = {'int': 'number', 'char': 'text', 'date': 'date',
               'number': 'number', 'text': 'text'}
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

            tmp = []
            for item in result['data']:
                for key in item:
                    if str(item[key]).find('datetime'):
                        item[key] = str(item[key])
                columns = [item['id'] for item in result['columns']]
                tmp.append([item[column] for column in columns]) #!!
            result['data'] = tmp

            js = json.dumps(result, ensure_ascii=False)
            return HttpResponse(js, content_type='application/json')
    return HttpResponseNotFound()


@csrf_exempt
def add_value(request, table):
    for key in sources:
        if sources[key]['title'] == table:
            form = myforms['%sForm' % key](request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                tables[key].objects.create(**cd)
                return HttpResponse()
            else:
                print('invalid')
                print(form.errors)
                return HttpResponseServerError()

@csrf_exempt
def edit_value(request, tables):
    try:
        return HttpResponse()
    except Exception as e:
        print(e)
        return HttpResponse()