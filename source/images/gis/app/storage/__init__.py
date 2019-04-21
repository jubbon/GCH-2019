#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from .file.json import save as save_to_json
from .file.json import load as load_from_json

def update_meta(region, address, params):
    ''' Обновляет метаинформацию о записях
    '''
    directory = os.path.join(*[part.strip() for part in address.split(",")])
    filename = f"/var/local/citylix.dom/data/{region}/houses/{directory}/meta.json"
    meta = None
    try:
        meta = load_from_json(filename)
    except FileNotFoundError:
        pass
    if meta is None:
        meta = dict()
    meta.update(address=address)
    if params:
        assert isinstance(params, dict), "params must be dict"
        meta.update(params)
    save_to_json(filename=filename, data=meta)


def handle_brief(ws, meta, data):
    ''' Сохраняет краткую информацию о доме
    '''
    assert isinstance(data, dict)
    # region = meta["region"]
    # address = data["address"]["fullname"]
    # directory = os.path.join(*[part.strip() for part in address.split(",")])
    # filename = f"/var/local/citylix.dom/data/{region}/houses/{directory}/brief.json"
    # print(f"Save data to file '{filename}'", flush=True)
    # await save_to_json(filename=filename, data=data["brief"])
    # await update_meta(region, address,
    #                 {"brief_updated": int(meta["timestamp"])})


def handle_company(meta, data):
    ''' Сохраняет информацию об управляющей компании
    '''
    assert isinstance(data, dict)
    region = meta["region"]
    address = data["address"]["fullname"]
    directory = os.path.join(*[part.strip() for part in address.split(",")])
    filename = f"/var/local/citylix.dom/data/{region}/houses/{directory}/company.json"
    print(f"Save data to file '{filename}'", flush=True)
    save_to_json(filename=filename, data=data["company"])
    update_meta(region, address,
                      {"company_updated": int(meta["timestamp"])})


def handle_passport(meta, data):
    ''' Сохраняет данные из паспорта дома
    '''
    assert isinstance(data, dict)
    region = meta["region"]
    address = data["address"]["fullname"]
    directory = os.path.join(*[part.strip() for part in address.split(",")])
    filename = f"/var/local/citylix.dom/data/{region}/houses/{directory}/passport.json"
    print(f"Save data to file '{filename}'", flush=True)
    save_to_json(filename=filename, data=data["passport"])
    update_meta(region, address,
                      {"passport_updated": int(meta["timestamp"])})
