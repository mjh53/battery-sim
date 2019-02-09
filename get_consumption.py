#!/bin/python

import requests
import datetime
import time
from dateutil import parser

class APIError(Exception):
    """An API Error Exception"""

    def __init__(self, status):
        self.status = status

    def __str__(self):
        return "APIError: status={}".format(self.status)


keyf=open('/home/snow/keys/octopus_api.key')
key=keyf.readline().strip()
    
resp = requests.get('https://api.octopus.energy/v1/electricity-meter-points/2100040571536/meters/18P5044807/consumption/', auth=(key,''))
if resp.status_code != 200:
  # failed
  raise APIError('GET consumption {}'.format(resp.status_code))

#print resp.json()
sum=0
r=resp.json()
count=r['count']
next_url=r['next']
results=r['results']
for reading in results:
    start=reading['interval_start']
    begin=parser.parse(start)

    print begin
    end=reading['interval_end']
    amount=reading['consumption']

    sum+=amount

print sum
