#!/bin/python

import simulator
from dateutil import parser
import datetime
import sqlite3

battery1=simulator.battery("Powerwall",13.5,6)
battery2=simulator.battery("Powervault",6,6)
grid=simulator.supply(0.1335,0.0476,"00:30","04:30") # 0.0476
solar_supply=simulator.supply(0,0,"00:00","00:00")

#midday=parser.parse('12:00')
#night=parser.parse('01:30')
#
#grid.draw(midday,10)
#grid.draw(night,10)
#print grid.get_bill()


def consistency_check(date):
    print "Checking for %s" % date
    db=sqlite3.connect('/home/snow/smadata/SBFspot.db')
    sql="SELECT TimeStamp,EnergyUsed FROM Consumption WHERE TimeStamp >= DATETIME('{}') AND TimeStamp< DATETIME('{}','+1 days')".format(date,date)
    ret=db.execute(sql)
    for row in ret:
        (time,amount)=row
        time=parser.parse(time)
        
        grid.drawWh(time,amount)
    print_bill(grid)

def print_bill(grid,detailed=False):    
    (header,bill,energy,detail,by_day)=grid.get_bill()
    print header, "Charged:",bill,"for",energy,"kWh"
    if detailed:
        for line in detail:
            (time,tariff,energy,cost)=line
            print time,tariff,energy,cost
    #for date in sorted(by_day.iterkeys()):
    #print date,round(by_day[date],2)




#consistency_check('2019-01-10')

def solar_generated(db,time):


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
    

def run_history(controller,start,end,base_load,detail=False):
    """
    Runs controller simultation from beginning of <start> to end of <end>
    """
    
    print "Checking for %s to %s" % (start,end)
    db=sqlite3.connect('/home/snow/smadata/SBFspot.db')
    sql="SELECT TimeStamp,EnergyUsed FROM Consumption WHERE TimeStamp >= DATETIME('{}') AND TimeStamp< DATETIME('{}','+1 days')".format(start,end)
    ret=db.execute(sql)
    for row in ret:
        (time,amount)=row
        time=parser.parse(time)
        """ 30 minute interval. Get and summarise solar power """
        solar_gen=solar_generated(db,time)
        solar=solar_gen
        demand=amount
        if solar>base_load:
            if demand < 50:
                solar-=base_load
                demand=0
            else:
                solar=0
        """ This is the historic grid draw at that 30-minute time interval """
        action=controller.decision(time,30,demand,solar)
        if detail: print time,"Historic draw:",amount, "Solar gen:",solar_gen,"Battery action:",action, "Battery state:",controller.battery.get_charge_percentage(),"%"
        grid.drawWh(time,amount)
    print "Grid ",
    print_bill(grid,detail)
    print "Solar ",
    print_bill(solar_supply,detail)
        
controller_solar=simulator.battery_control(
    simulator.battery("Powerwall",13.5,6),grid,solar_supply,"Econ7Solar")
controller_econ=simulator.battery_control(
    simulator.battery("Powerwall",13.5,6),grid,solar_supply,"Econ7")
controller_none=simulator.battery_control(
    simulator.battery("Powerwall",13.5,6),grid,solar_supply)
start="2019-01-09"
end="2019-02-09"
print "Solar end Econ7 charging"
run_history(controller_solar,start,end,300,False)
grid.do_reset()
solar_supply.do_reset()
print "Just Econ7 to battery"
run_history(controller_econ,start,end,300)
grid.do_reset()
solar_supply.do_reset()
print "No battery"
run_history(controller_none,start,end,300)
