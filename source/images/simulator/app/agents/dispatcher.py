#!/usr/bin/env python
# -*- coding: utf-8 -*-

import uuid
import random
from datetime import datetime

from resources import Order


class Dispatcher():
    ''' Диспетчер
         - формирует наряд на вывоз мусора
    '''

    def __init__(self, env, uid, name, timeout):
        self.env = env
        # Уникальный идентификатор дома
        self.uid = uid
        # Название регионального оператора
        self.name = name
        # Пороговый уровень заполненности контейнера
        self.dumpster_threshold = 0.7
        # Таймаут
        self.timeout = timeout
        # Наряды
        self.orders = dict()

        self.action = env.process(self.run())

    @property
    def state(self):
        '''
        '''
        return dict(
            timestamp=self.env.now,
            uid=self.uid
        )

    def run(self):
        '''
        '''
        while True:
            # Начинаем работу с 06-00 и завершаем работу в 16-00
            # Формирование нарядов
            yield self.env.timeout(self.timeout)
            dumpsters = dict()
            for dumpster_uid, dumpster in self.env._dumpsters.items():
                if dumpster.percent_level > self.dumpster_threshold and dumpster.order_uid is None:
                    dumpsters[dumpster_uid] = dumpster

            if len(dumpsters) >= 16:
                order_uid = uuid.uuid4()
                self.orders[order_uid] = Order(
                    self.env,
                    order_uid,
                    dumpsters,
                    target=dict(
                        latitude=56.322486,
                        longitude=43.560934
                    )
                )
                for _, dumpster in dumpsters.items():
                    dumpster.set_order(order_uid)
                print(f"Generating order '{order_uid}'", flush=True)

    def get_order(self, vehicle_uid, latitude, longitude):
        ''' Возвращает свободный наряд
        '''
        for order_uid, order in self.orders.items():
            if order.vehicle_uid is None:
                order.set_vehicle(vehicle_uid)
                return order