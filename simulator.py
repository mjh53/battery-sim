#!/bin/python

from dateutil import parser
import datetime

class battery:

    def __init__(self,name,capacity,power):
        """Arguments:
        name (duh)
        capacity in kWh is storage capacity
        Power in kW is input/output power capacity
        """
        
        self.name=name
        self.capacity=capacity
        self.charge=0
        self.power=power

    def do_reset(self):
        self.charge=0
        return
        
    def do_charge(self,supply,time,energy,interval):
        """Charge battery with <energy> kWh over <interval> minutes
        Draws from supply to charge up
        Returns amount of energy consumed"""
        if self.charge+energy < self.capacity:
            increase=energy
        else:
            increase=self.capacity-self.charge
        power=increase*(60/interval)
        if power > self.power:
            increase=self.power/(60/interval)
        supply.drawkWh(time,increase)
        self.charge+=increase
        return increase

    def do_discharge(self,supply_obj,time,requested):
        """Discharge <energy> W from the battery
        Returns energy delivered"""
        if self.charge > requested:
            energy=requested
        else:
            energy=self.charge
        if energy > self.power:
            energy=self.power    
        self.charge-=energy
        supply_obj.injectkWh(time,energy)
        return energy

    def get_charge_state(self):
        """Returns energy stored in battery"""
        return self.charge
    def get_charge_percentage(self):
        """Returns charge state as a percentage"""
        return round((self.charge/self.capacity)*100,2)

class supply:
    def __init__(self,rate,cheap_rate,cheap_start,cheap_end):
        self.rate=rate
        self.cheap_rate=cheap_rate
        self.cheap_start=parser.parse(cheap_start).time()
        self.cheap_end=parser.parse(cheap_end).time()
        self.cost=0
        self.statement=[]

    def do_reset(self):
        self.cost=0
        self.statement=[]
        return
        
    def drawkWh(self,time,energy):
        tariff=self.tariff(time)
        cost=round(energy * tariff,5)
        self.statement.append([time,tariff,energy,cost])
        return True

    def injectkWh(self,time,energy):
        return self.drawkWh(time,-energy)
    
    def drawWh(self,time,energy):
        return self.drawkWh(time,energy/1000.0)

    def tariff(self,time):
        if self.cheap_time(time):
            tariff=self.cheap_rate
        else:
            tariff=self.rate
        return tariff

    def cheap_time(self,time):
        return (time.time() >= self.cheap_start and time.time() < self.cheap_end)
    
    def get_bill_period(self,bill_start,bill_end):
        bill=0
        detail=[]
        days={}
        start=False
        end=False
        for line in self.statement:
            time,tariff,energy,cost=line
            if not (time > bill_start and time < bill_end):
                continue
            if not start:
                start=time
            else:
                if time<start: start=time
            if not end:
                end=time
            else:
                if time>end: end=time
            bill+=cost
            detail.append([time,tariff,energy,cost])
            date=time.date()
            if date in days:
                days[date]+=cost
            else:
                days[date]=cost
        header="From {} to {}".format(start,end)
        bill=round(bill,2)
        return [header,bill,detail,days]

    def get_bill(self):
        """returns:
        time period header
        cost      """
        return self.get_bill_period(datetime.datetime.fromtimestamp(0),datetime.datetime.now())

    def reset_billing(self):
        self.statement=[]
        return True
    
    
class battery_control:
    def decision(self,time,interval,demand):
        """
        Apply relevant control logic to the demand/time.

        Charge/Discharge battery appropriately
        
        """
        demand=demand/1000.0
        return self.logic(time,interval,demand)

    def no_action(self,time,interval,demand):
        return False

    def economy7_charger(self,time,interval,demand):
        if self.supply.cheap_time(time):
            amount=self.battery.do_charge(self.supply,time,99999,interval)
            return "Charge by %skWh" % amount
            
        if demand>0:
            amount=self.battery.do_discharge(self.supply,time,demand)
            return "Discharge %skWh" % amount
    
    def __init__(self,battery,supply,control_type="None"):
        self.battery=battery
        self.supply=supply
        self.logic=self.no_action
        if control_type == "Econ7":
            self.logic=self.economy7_charger
        
