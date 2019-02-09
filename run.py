#!/bin/python

import simulator
from dateutil import parser
import sqlite3

battery1=simulator.battery("Powerwall",13.5,6)
battery2=simulator.battery("Powervault",6,6)
grid=simulator.supply(0.1335,0.0476,"00:30","04:30")

#midday=parser.parse('12:00')
#night=parser.parse('01:30')
#
#grid.draw(midday,10)
#grid.draw(night,10)
#print grid.get_bill()


def consistency_check(date):
    print "Checking for %s" % date
    db=sqlite3.connect('/home/snow/smadata/SBFspot.db')
    cursor=db.cursor()
    sql="SELECT TimeStamp,EnergyUsed FROM Consumption WHERE TimeStamp >= DATETIME('{}') AND TimeStamp< DATETIME('{}','+1 days')".format(date,date)
    ret=cursor.execute(sql)
    for row in ret:
        (time,amount)=row
        time=parser.parse(time)
        
        grid.drawWh(time,amount)
    print_bill(grid)

def print_bill(grid,detail=False):    
    (header,bill,detail,by_day)=grid.get_bill()
    print header, "Charged:",bill
    #for line in detail:
    #    (time,tariff,energy,cost)=line
    #    print time,tariff,energy,cost
    #for date in sorted(by_day.iterkeys()):
    #print date,round(by_day[date],2)




#consistency_check('2019-01-10')

def run_history(controller,start,end):
    """
    Runs controller simultation from beginning of <start> to end of <end>
    """
    
    print "Checking for %s to %s" % (start,end)
    db=sqlite3.connect('/home/snow/smadata/SBFspot.db')
    cursor=db.cursor()
    sql="SELECT TimeStamp,EnergyUsed FROM Consumption WHERE TimeStamp >= DATETIME('{}') AND TimeStamp< DATETIME('{}','+1 days')".format(start,end)
    ret=cursor.execute(sql)
    for row in ret:
        (time,amount)=row
        time=parser.parse(time)
        """ This is the historic grid draw at that 30-minute time interval """
        action=controller.decision(time,30,amount)
#        print "Historic draw:",amount, "Battery action:",action, "Battery state:",battery.get_charge_percentage(),"%"
        grid.drawWh(time,amount)

    print_bill(grid)
        
controller_econ=simulator.battery_control(
    simulator.battery("Powerwall",13.5,6),grid,"Econ7")
controller_none=simulator.battery_control(
    simulator.battery("Powerwall",13.5,6),grid)
print "No battery"
run_history(controller_none,"2017-01-01","2019-05-30")
print "Just Econ7 to battery"
grid.do_reset()
run_history(controller_econ,"2017-01-01","2019-05-30")
