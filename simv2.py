#!/bin/python

from dateutil import parser
import datetime
DEBUG=True

class battery:

    def __init__(self,name,capacity,charge_power,output_power):
        """ Arguments
        name - String
        capacity - Usable storage in Wh
        charge_power - maximum power draw to charge in Wh
        output_power - maximum output power supply
        """

        self.name=name
        self.capacity=capacity
        self.charge_power=charge_power
        self.output_power=output_power
        # self.energy in Wh is currently stored energy
        self.energy=0
        # self.supplies is a list of available supplies
        self.supplies=[]

    def reset(self):
        self.energy=0
        return True

    def connect_supply(self,supply):
        """
        Connect a supply object to the battery
        """

        if supply in self.supplies:
            return (False,"Already connected")

        self.supplies.append(supply)
        return (True,"%s connected. %d supplies" % (supply.name,
                                                    len(self.supplies)))
    def _discharge_energy(self,energy):
        """
        Internal call to remove energy from storage (Wh)
        Returns energy successfully discharged
        """

        if energy>self.energy:
            energy=self.energy
            self.energy=0
        else:
            self.energy-=energy
        return energy

    def draw_power(self,power,period):
        """
        Request from load for power.
        Returns the requested power from available supplies
        """

class bill:

    def __init__(self):
        self.charges=[]

    def charge(self,amount,time):
        self.charges.append([amount,time])
        return True

    def total_charge(self):
        total=0
        for (cost,time) in self.charges:
            total+=cost
        return cost

    def pay(self):
        self.charges=[]
        return True

    def itemize(self):
        """
        Return a list of all charges/times
        """

        return self.charges
    
class supply:

    def __init__(self,name,rates,times):
        """
        rate is an array of charges (in ukp/kWh)
        time is an array of time-of-day periods corresponding to rates
        eg:
        rate is in ukp/unit (kWh)

        rate=[0.15,0.5,0.15]
        time=[["00:00","00:30"],["00:30","04:30"],["04:30","23:59"]]
        """

        self.name=name
        self.bill=bill()
        self.times=[]
        index=0
        for period in times:
            start=parser.parse(period[0])
            end=parser.parse(period[1])

            # convert kWh into Wh internally
            self.times.append([start.time(),end.time(),rates[index]/1000.0])
            if DEBUG:
                print self.times[index]
            index+=1


    def rate(self,timedate):
        time=timedate.time()
        for period in self.times:
            if time>period[0] and time < period[1]:
                return period[2]
        return False

    def draw(self,energy,period):
        

    
