from django.contrib.auth.models import User
from django import forms
# from django.forms import Form, ModelForm
from django.forms.models import ModelFormMetaclass

from .models import tables, sources

myforms = {}
for item in sources:
    attrs = {}
    attrs = {'id': forms.IntegerField(required=False)}
    for field in sources[item]['fields']:
        if field['type'] == 'int':
            attrs[field['id']] = forms.IntegerField()
        elif field['type'] == 'date':
            attrs[field['id']] = forms.DateField(
                input_formats=['%m/%d/%Y', '%b %d %Y', '%Y-%m-%d'])
        elif field['type'] == 'char':
            attrs[field['id']] = forms.CharField()

    tmp = type('%sForm' % item, (forms.Form, ), attrs)
    myforms['%sForm' % item] = tmp
