#!/bin/python

import simv2
import datetime


grid=s=simv2.supply("grid",[0.15,0.5,0.15],[["00:00","00:30"],["00:30","04:30"],["04:30","23:59"]])

print grid.rate(datetime.datetime.now())
