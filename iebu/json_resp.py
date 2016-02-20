# -*- coding: utf-8 -*-
from django.http import HttpResponse
import json


def get_json(data, *args, **kwargs):
    '''Возвращает json ответ на запрос
    '''
    return HttpResponse(json.dumps(data),
        content_type='application/json', *args, **kwargs)


def get_error(msg):
    '''Возвращает ответ-ошибку
    '''
    return get_json({'status': 'error', 'msg': msg})


def get_ok(data=None):
    '''Возвращает успешный ответ
    '''
    resp = {'status': 'ok'}
    if data is not None:
        resp.update({'data': data})
    return get_json(resp)
