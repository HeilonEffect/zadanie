import datetime
import json
import re

from django.http import HttpResponse, HttpResponseNotFound
from django.http import HttpResponseServerError
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from myapp.models import tables, sources
from myapp.forms import myforms


@require_http_methods(['GET'])
def index(request):
    return render_to_response('base.html')


@require_http_methods(['GET'])
def tablenames(request):
    names = json.dumps([sources[item]['title'] for item in sources],
                       ensure_ascii=False)
    return HttpResponse(names, content_type='application/json')


def get_table(fields, table):
    convert = {'int': 'number', 'char': 'text', 'date': 'date',
               'number': 'number', 'text': 'text'}
    result = {}
    result['columns'] = fields
    for column in result['columns']:
        column['type'] = convert[column['type']]
        column['result'] = ''
    kwargs = [field['id'] for field in fields]
    result['data'] = list(table.objects.values(*kwargs)) or list()

    tmp = []
    for item in result['data']:
        for key in item:
            if str(item[key]).find('datetime'):
                item[key] = str(item[key])
        columns = [item['id'] for item in result['columns']]
        tmp.append([item[column] for column in columns])
    result['data'] = tmp

    return json.dumps(result, ensure_ascii=False)


@require_http_methods(['GET'])
def table_columns(request, table):
    for key in sources:
        if sources[key]['title'] == table:
            return HttpResponse(get_table(
                sources[key]['fields'], tables[key]
            ), content_type='application/json')
    return HttpResponseNotFound()


@csrf_exempt
@require_http_methods(['POST'])
def add_value(request, table):
    for key in sources:
        if sources[key]['title'] == table:
            form = myforms['%sForm' % key](request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                tables[key].objects.create(**cd)
                for key in cd:
                    # если строка начинается с datetime
                    if (str(cd[key])).find('datetime'):
                        cd[key] = str(cd[key])
                return HttpResponse(json.dumps(cd))
            else:
                tmp = []
                for error in form.errors:
                    tmp.append(error)
                return HttpResponseServerError(json.dumps(tmp))


@csrf_exempt
@require_http_methods(['POST'])
def edit_value(request, table):
    '''
    Обновляет отредактированную ячейку
    Здесь идея заключается в следующем - мы получаем данные,
    сериализованные в JSON - по ключу old - все данные старой
    ячейки, по ключу new_val - то, что изменилось.
    Дополняем новые данные теми старыми значениями, которые не изменились
    После валидации, если '''
    try:
        old_val = json.loads(request.POST['old'])
        new_val = json.loads(request.POST['new_val'])

        for key in new_val:
            try:
                new_val[key] = re.search(
                    r'(\d+-\d+-\d+)', new_val[key]).group(1)
            except Exception as e:
                pass
        for key in old_val:
            if not key in new_val:
                new_val[key] = old_val[key]

        for key in sources:
            if sources[key]['title'] == table:
                form = myforms['%sForm' % key](old_val)
                form1 = myforms['%sForm' % key](new_val)
                if form.is_valid() and form1.is_valid():
                    cd = form.cleaned_data
                    cd1 = form1.cleaned_data

                    tables[key].objects.filter(**cd).update(**cd1)
                    return HttpResponse(get_table(
                        sources[key]['fields'], tables[key]
                    ), content_type='application/json')
                else:
                    return HttpResponse()
                    # print('invalid')
        return HttpResponse()
    except Exception as e:
        print(e)
        return HttpResponseServerError()
