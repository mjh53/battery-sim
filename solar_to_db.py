#!/bin/python
import sqlite3
import datetime
from dateutil import parser

db=sqlite3.connect('/home/snow/smadata/SBFspot.db')

mydb=sqlite3.connect('/home/snow/electricity.db')

sql='SELECT TimeStamp,EnergyUsed from Consumption ORDER BY Timestamp'
grid=db.execute(sql)

def solar_generated(db,time):
    time=parser.parse(time)

    solar_sql='SELECT strftime("%Y%m%d,%H:%M",TimeStamp),TotalYield FROM [vwDayData] WHERE TimeStamp=DATETIME("{}");'
    meter_out=db.execute(solar_sql.format(time))

    solar_start=solar_end=0
    for result in meter_out:
        (x,solar_start)=result
    meter_out=db.execute(solar_sql.format(time+datetime.timedelta(minutes=30)))
    for result in meter_out:
        (x,solar_end)=result
    if solar_start==0: solar_start=solar_end
    if solar_end==0: solar_end=solar_start
    return solar_end-solar_start

for row in grid:
    (time,usedenergy)=row

    energy=solar_generated(db,time)
    print time,usedenergy,energy

    sql="INSERT into Solar(TimeStamp,EnergyGenerated) values ('{}',{})".format(time,energy)

    if energy>0:
        print sql
        mydb.execute(sql)
