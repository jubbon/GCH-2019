#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
from pathlib import Path

import simpy

from agents import Clock, Dispatcher, Vehicle, House
from resources import Dumpster
from data import save_to_csv, load_from_json


class City(simpy.Environment):
    '''
    '''
    debug = False

    def __init__(self, **kwargs):
        super(City, self).__init__(**kwargs)

        self._clock = Clock(self, timeout=600)

        self.dispatchers = list()
        self._dispatcher_states = list()

        self.vehicles = list()
        self._vehicle_states = list()

        self._houses = dict()
        self._house_states = list()

        self._dumpsters = dict()
        self._dumpster_states = list()

    @property
    def status(self):
        '''
        '''
        # Текущая загрузка всех мусорных контейнеров
        total_dumpster_load = 0
        for _, dumpster in self._dumpsters.items():
            total_dumpster_load += dumpster.state["value"]

        return {"total_dumpster_load": round(total_dumpster_load, 1)}

    def add_dispatcher(self, **kwargs):
        '''
        '''
        self.dispatchers.append(Dispatcher(self, **kwargs))

    def add_vehicle(self, **kwargs):
        '''
        '''
        # assert isinstance(vehicle, Vehicle)
        self.vehicles.append(Vehicle(self, **kwargs))

    def add_house(self, **kwargs):
        '''
        '''
        # assert isinstance(vehicle, Vehicle)
        uid = kwargs["uid"]
        self._houses[uid] = House(self, **kwargs)

    def add_dumpster(self, uid, latitude, longitude, capacity, count=1):
        ''' Добавляет контейнерную площадку
        '''
        self._dumpsters[uid] = Dumpster(self, uid, latitude, longitude, capacity=capacity, count=count)

    def get_dumpster(self, uid):
        '''
        '''
        return self._dumpsters[uid]

    def set_house_state(self, state):
        ''' Сохраняет состояние дома
        '''
        self._house_states.append(state)

    def house_states(self, uid=None, timestamp_after=None, timestamp_before=None):
        '''
        '''
        for state in self._house_states:
            yield state

    def set_dumpster_state(self, state):
        ''' Сохраняет состояние мусорного контейнера
        '''
        self._dumpster_states.append(state)

    def dumpster_states(self, uid=None, timestamp_after=None, timestamp_before=None):
        '''
        '''
        for state in self._dumpster_states:
            yield state

    def set_dispatcher_state(self, state):
        ''' Сохраняет состояние диспетчера
        '''
        self._vehicle_states.append(state)

    def dispatcher_states(self, uid=None, timestamp_after=None, timestamp_before=None):
        '''
        '''
        for state in self._dispatcher_states:
            yield state

    def set_vehicle_state(self, state):
        ''' Сохраняет состояние мусорного автомобиля
        '''
        self._vehicle_states.append(state)

    def vehicle_states(self, uid=None, timestamp_after=None, timestamp_before=None):
        '''
        '''
        for state in self._vehicle_states:
            yield state


def simulate(dispatchers, dumpsters, houses, vehicles, start_time=0, finish_time=None):
    '''
    '''
    city = City(initial_time=start_time)

    for dispatcher in dispatchers:
        assert isinstance(dispatcher, dict)
        city.add_dispatcher(**dispatcher)
    for dumpster in dumpsters:
        assert isinstance(dumpster, dict)
        city.add_dumpster(**dumpster)
    for house in houses:
        assert isinstance(house, dict)
        city.add_house(**house)
    for vehicle in vehicles:
        assert isinstance(vehicle, dict)
        city.add_vehicle(**vehicle)

    city.run(until=finish_time)
    return city


def main():
    '''
    '''
    start_time = 1555534800
    finish_time = 1555621200

    # Виртуальные диспетчеры
    dispatchers = list()
    dispatchers.append(dict(uid="1", name="Нижэкология-НН", timeout=600))
    dispatchers.append(dict(uid="2", name="Управление отходами-НН", timeout=600))

    # Мусорные контейнеры
    dumpsters = list()
    dumpsters_uids = list()
    dumpsters_info = load_from_json("/data/Реестр контейнерных площадок.json")
    for dumpster_uid, dumpster in dumpsters_info.items():
        try:
            location = dumpster["Расположение"][0]["location"]
            longitude, latitude = location
        except:
            print(f"Нет данных о расположении контейнерной площадки '{dumpster_uid}'", flush=True)
            continue

        area = dumpster.get("Округ", "")
        if area is None:
            area = ""
        # if "Советский" not in area:
        #     continue
        if "Нижегородский" not in area:
            continue

        capacity = dumpster["Вместимомть"]
        try:
            if capacity:
                capacity = float(capacity)
                capacity = round(float(capacity) * 1000)
            else:
                print(f"Нет данных о вместимости контейнерной площадки '{dumpster_uid}': {capacity}", flush=True)
                continue
        except ValueError:
            print(f"Нет данных о вместимости контейнерной площадки '{dumpster_uid}': {capacity}", flush=True)
            continue
            
        count = dumpster["Количество"]
        if count:
            count = int(count)
        else:
            print(f"Нет данных о количестве контейнеров на площадке'{dumpster_uid}': {count}", flush=True)
            continue
        dumpsters.append(dict(
            uid=dumpster_uid,
            latitude=latitude,
            longitude=longitude,
            capacity=capacity,
            count=count
        ))
        dumpsters_uids.append(dumpster_uid)

    # Жилые дома
    houses_info = load_from_json("/data/Реестр жилых домов.json")
    houses_coords = load_from_json("/data/Координаты жилых домов.json")
    houses_dumpsters = load_from_json("/data/Ближайшие контейнерные площадки.json")
    houses = list()
    for house in houses_info:
        address = house["address"]["fullname"]
        
        total_area = house.get("Общая площадь здания", "0")
        try:
            total_area = float(total_area.replace("м2", "").strip())
        except ValueError:
            if not total_area:
                total_area = None
            else:
                print(f"Неверный формат {total_area}", flush=True)

        living_area = house.get("Общая площадь жилых помещений", "0")
        try:
            living_area = float(living_area.replace("м2", "").strip())
        except ValueError:
            if not living_area:
                living_area = None
            else:
                print(f"Неверный формат {living_area}", flush=True)

        daily_emission = 0
        if living_area:
            daily_emission = round(living_area * 0.1 * 1000 / 365.0)
        elif total_area:
            daily_emission = round(total_area * 0.6 * 0.1 * 1000 / 365.0)

        coords = houses_coords.get(address)
        dumpster = houses_dumpsters.get(address)
        if coords is None:
            continue
        if dumpster is None:
            continue
        dumpster_uid = dumpster["uid"]
        if dumpster_uid not in dumpsters_uids:
            continue
        latitude = coords["lat"]
        longitude = coords["lng"]
        houses.append(dict(
            uid=address,
            latitude=latitude,
            longitude=longitude,
            dumpster_uid=dumpster_uid,
            daily_emission=daily_emission
        ))

    # Мусороуборочные автомобили
    vehicles = list()
    vehicles.append(dict(
        uid="1",
        number="514",
        owner="Ситилюкс",
        capacity=20000,
        value=200
    ))
    vehicles.append(dict(
        uid="2",
        number="515",
        owner="Ситилюкс",
        capacity=20000,
        value=300
    ))
    vehicles.append(dict(
        uid="3",
        number="515",
        owner="Ситилюкс",
        capacity=20000,
        value=300
    ))
    # vehicles.append(dict(uid="2", number="515", owner="ДЭП", capacity=20, value=8.5))

    result = simulate(
        dispatchers,
        dumpsters,
        houses,
        vehicles,
        start_time=start_time,
        finish_time=finish_time
    )

    # Сохранение результатов симуляции
    dt = datetime.now()
    path = Path(f"/data/result/{dt:%Y-%m-%d-%H-%M-%S}")
    print(f"Saving simulation result to {path}", flush=True)
    save_to_csv(path / "vehicles.csv", list(result.vehicle_states()))
    save_to_csv(path / "houses.csv", list(result.house_states()))
    save_to_csv(path / "dumpster.csv", list(result.dumpster_states()))

    all_data = list()
    for vehicle in result.vehicle_states():
        all_data.append({
            "timestamp": vehicle["timestamp"],
            "uid": vehicle["uid"],
            "type":"vehicle",
            "latitude": vehicle["latitude"],
            "longitude": vehicle["longitude"],
            "radius": 2,
            "capacity": vehicle["capacity"],
            "value": vehicle["value"],
            "percent_level": vehicle["percent_level"]
        })
    for dumpster in result.dumpster_states():
        all_data.append({
            "timestamp": dumpster["timestamp"],
            "uid": dumpster["uid"],
            "type":"dumpster",
            "latitude": dumpster["latitude"],
            "longitude": dumpster["longitude"],
            "radius": 10,
            "capacity": dumpster["capacity"],
            "value": dumpster["value"],
            "percent_level": dumpster["percent_level"]
        })
    save_to_csv(path / "all.csv", all_data)
