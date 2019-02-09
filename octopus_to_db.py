#!/bin/python

import requests
import datetime
import time
from dateutil import parser
import sqlite3

DEBUG=False

cheap_rate=0.05
high_rate=0.15
cheap_start="00:30"
cheap_end="04:30"
cheap_start_t=parser.parse(cheap_start)
cheap_end_t=parser.parse(cheap_end)

class APIError(Exception):
    """An API Error Exception"""

    def __init__(self, status):
        self.status = status

    def __str__(self):
        return "APIError: status={}".format(self.status)


keyf=open('/home/snow/keys/octopus_api.key')
key=keyf.readline().strip()
keyf.close()
db=sqlite3.connect('/home/snow/smadata/SBFspot.db')
cursor=db.cursor()

api_url='https://api.octopus.energy/v1/electricity-meter-points/2100040571536/meters/18P5044807/consumption/'


while api_url:
    resp = requests.get(api_url, auth=(key,''))
    if resp.status_code != 200:
        # failed
        raise APIError('GET consumption {}'.format(resp.status_code))
    #print resp.json()

    r=resp.json()
    count=r['count']
    api_url=r['next']
    results=r['results']

    for reading in results:
        start=reading['interval_start']
        end=reading['interval_end']
        consumption=int(reading['consumption']*1000)

        sql= "INSERT INTO Consumption(TimeStamp,EnergyUsed) VALUES(DATETIME('{}'),{})".format(start,consumption)
        try:
            cursor.execute(sql)
            db.commit()
            print sql
        except Exception as e:
            db.rollback()
            print "duplicated",sql

    print api_url
