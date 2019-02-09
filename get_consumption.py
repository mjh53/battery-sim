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

x=db.execute('SELECT * from Config')
for row in x:
    print row

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
    current_day='fish'
    total_grid=0.0
    total_charge=0.0
    total_solar=0.0

    for reading in results:
        start=reading['interval_start']
        end=reading['interval_end']
        (day,tstart)=start.split('T')
        (day,tend)=end.split('T')
        consumption=int((reading['consumption']) * 1000)

        start_t=parser.parse(tstart)
        end_t=parser.parse(tend)
        if (start_t.time() > cheap_start_t.time() and end_t.time() < cheap_end_t.time()):
            rate=cheap_rate
        else:
            rate=high_rate

        units=consumption/1000.0
        cost=units*rate
        if DEBUG: print "%f units at ukp%f/unit = %f" % (units,rate,cost)
        
        if DEBUG: print "from {} to {}".format(start,end)
        solar_read=db.execute('SELECT strftime("\%Y\%m\%d,\%H:\%M",TimeStamp),TotalYield FROM [vwDayData] WHERE TimeStamp>=DATETIME("{}") AND TimeStamp<=DATETIME("{}") ORDER BY TimeStamp;'.format(start,end) )
        generated=0
        first_read=last_read=0
        for row in solar_read:
            (a,b)=row
            if first_read==0:
                first_read=b
                if DEBUG: print "Interval start: %d" % first_read
            last_read=b
            if DEBUG: print a,b-first_read
        generated=(last_read-first_read)
        if DEBUG: print "Interval end: %d" % last_read
        
        # sum is power generated over that timeframe
        if DEBUG: print "Grid: {} Solar: {}".format(consumption,generated)
        total_grid+=consumption
        total_solar+=generated

        if day != current_day:
            if current_day != 'fish':
                print "Summary for %s:" % current_day
                print total_grid
                print "Grid sourced:  %f kWh" % (total_grid/1000.0)
                print "Solar sourced: %f kWh" % (total_solar/1000.0)
            current_day=day
            total_grid=0.0
            total_solar=0.0
