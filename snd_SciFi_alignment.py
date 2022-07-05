###
#
# This is an example file to demonstrate how the conditionsDatabase API works
###
from __future__ import print_function, division
from factory import APIFactory
import datetime, sys


from builtins import range
import operator
from argparse import ArgumentParser
from array import array
import os,ROOT

# Instantiate an API factory
api_factory = APIFactory()
conditionsDB = api_factory.construct_DB_API("/home/eric/snd-10jan2021/sndsw/conditionsDatabase/config.yml")

conditionsDB.add_detector("SciFi")

conditions = {"z":0.0,"xdim": 39.0,"ydim": 39.0,"zdim": 3.0,"DZ": 7.790000000000001,"nmats": 3,"nscifi": 5,"channel_width": 0.025,"sipm_edge": 0.017,"charr_gap": 0.020000000000000004,"charr_width": 1.6,"sipm_diegap": 0.006,"SiPMarray_width": 3.254,\
"nsipm_channels": 128,"nsipm_mat": 4,"nsipms": 12,"sipmarr_width": 3.22,"firstChannelX": -19.528,"nfibers_shortrow": 471,"nfibers_longrow": 472,"nfibers_z": 6,"scifimat_width": 12.989999999999998,"scifimat_length": 39.0,"scifimat_z": 0.135,"epoxymat_z": 0.17,\
"scifimat_gap": 0.05,"fiber_length": 39.0,"scintcore_rmax": 0.011,"clad1_rmax": 0.01175,"clad2_rmax": 0.0125,"horizontal_pitch": 0.0275,"vertical_pitch": 0.021,"rowlong_offset": 0.035,"rowshort_offset": 0.0215,"carbonfiber_z": 0.02,"honeycomb_z": 0.5,\
"plastbar_x": 1.5,"plastbar_y": 39.0,"plastbar_z": 0.195,"scifi_separation": 10.790000000000001,"offset_z": -24.71,"timeResol": 0.15,"Xpos0": 4.34,"Ypos0": 298.94,"Zpos0": 15.22,"Xpos1": 4.34,"Ypos1": 311.94,"Zpos1": 15.22,"Xpos2": 4.34,"Ypos2": 324.94,\
"Zpos2": 15.22,"Xpos3": 4.34,"Ypos3": 337.94,"Zpos3": 15.22,"Xpos4": 4.34,"Ypos4": 350.94,"Zpos4": 15.22,"EdgeAX": 22.5,"EdgeAY": 22.5,"EdgeAZ": 0.0,"FirstChannelVX": -19.528000000000002,"FirstChannelVY": -20.0,"FirstChannelVZ": -1.292,"FirstChannelHX": -20.0,\
"FirstChannelHY": -19.528000000000002,"FirstChannelHZ": -0.7070000000000001,"LfirstChannelVX": -19.5135,"LfirstChannelVY": 19.5,"LfirstChannelVZ": 1.185,"LfirstChannelHX": -19.5,"LfirstChannelHY": 19.5178,"LfirstChannelHZ": 0.625,"LocM100": 0.0,"LocM101": 0.0,\
"LocM102": 0.0,"LocM110": 0.0,"LocM111": 0.0,"LocM112": 0.0,"LocM200": 0.0,"LocM201": 0.0,"LocM202": 0.0,"LocM210": 0.0,"LocM211": 0.0,"LocM212": 0.0,"LocM300": 0.0,"LocM301": 0.0,"LocM302": 0.0,"LocM310": 0.0,"LocM311": 0.0,"LocM312": 0.0,"LocM400": 0.0,\
"LocM401": 0.0,"LocM402": 0.0,"LocM410": 0.0,"LocM411": 0.0,"LocM412": 0.0,"LocM500": 0.0,"LocM501": 0.0,"LocM502": 0.0,"LocM510": 0.0,"LocM511": 0.0,"LocM512": 0.0}

#the tag is Scifi_1
#time validity infinite
conditionsDB.add_condition("SciFi", "Alignment Constants", "Scifi_1", conditions,None,datetime.datetime.now(), datetime.datetime.max)
