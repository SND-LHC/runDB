###
#
# This is an example file to demonstrate how the conditionsDatabase API works
# It reads the geometry file and adds subdetectors with their positions to the condDB
# Takes about 5 mins to fill the condDB
###
from __future__ import print_function, division
from factory import APIFactory
import datetime, sys


from builtins import range
import operator
from argparse import ArgumentParser
from array import array
import os,ROOT


def local2Global(n):
    Info={}
    nav = ROOT.gGeoManager.GetCurrentNavigator()
    nav.cd(n)
    Info['node'] = nav.GetCurrentNode()
    Info['path'] = n
    tmp = Info['node'].GetVolume().GetShape()
    Info['material'] = Info['node'].GetVolume().GetMaterial().GetName()
    o = [tmp.GetOrigin()[0],tmp.GetOrigin()[1],tmp.GetOrigin()[2]]
    Info['locorign'] = o
    local = array('d',o)
    globOrigin  = array('d',[0,0,0])
    nav.LocalToMaster(local,globOrigin)
    Info['origin'] = globOrigin
    shifts = [ [-tmp.GetDX()+o[0],o[1],o[2]],
               [tmp.GetDX()+o[0],o[1],o[2]],
               [o[0],-tmp.GetDY()+o[1],o[2]],
               [o[0],tmp.GetDY()+o[1],o[2]],
               [o[0],o[1],-tmp.GetDZ()+o[2]],[o[0],o[1],tmp.GetDZ()+o[2]]
             ]
    shifted = []
    for s in shifts:
     local = array('d',s)
     glob  = array('d',[0,0,0])
     nav.LocalToMaster(local,glob)
     shifted.append([glob[0],glob[1],glob[2]])
    Info['boundingbox']={}
    for j in range(3):
     jmin = 1E30
     jmax = -1E30
     for s in shifted:
       if s[j]<jmin: jmin = s[j]
       if s[j]>jmax: jmax = s[j]
     Info['boundingbox'][j]=[jmin,jmax]
    return Info

def add_info(path, node, level, currentlevel, print_sub_det_info=False):
  sub_nodes = {}
  fullInfo = {}
  conditions_0={}
  conditions_1={}
  conditions_2={}
  conditions={}
  conditions_e0={}
  conditions_p0={}
  conditions_mu0={}
  conditions_Scifi={}
  name="Wall_"
  row="/Row_"
  brick="/Brick_"
  for i in range(5):
    wallname=name+str(i)
    for j in range(2):
       rowname=wallname+row+str(j)
       for k in range(2):
         brickname=rowname+brick+str(k)
         print("brickname=",brickname)
    #    conditionsDB.add_detector(brickname)
  name="ScifiVolume"
  horplane="/ScifiHorPlaneVol"
  hormatvol="/HorMatVolume_"
  fibrevol="/FiberVolume_"
  for i in range(1,6):
    scifiname=name+str(i)+"_"+str(i)+"000000"
    print("scifiname=",scifiname)
    #conditionsDB.add_detector(scifiname)
    #for j in range(1,6):
      #horplanename=scifiname+horplane+str(j)+"_"+str(j)+"000000"
      #for k in range(1,4):
        #hormatname=horplanename+hormatvol+str(i)+"0"+str(k)+"0000"
        #for l in range(1,4):
          #fibrevolname=hormatname+fibrevol+str

  name="volVeto_1"
  #conditionsDB.add_detector(volVeto_1)

  for subnode in node.GetNodes():
    name = subnode.GetName()
    fullInfo[name] = local2Global(path + '/' + name)
    sd = path[path.rfind('/')+1:] # want to know if we're inside a subdetector
    subdet=""
    if (name[:8]=="Emulsion"):
      #print("path.find Wall_ =",path.find("Wall_")," path.find Wall_ +20=",path.find("Wall_")+20)
      subdet=path[path.find("Wall_"):path.find("Wall_")+20]
      #print("subdet",subdet)
      conditions_0[name]={'x':fullInfo[name]['boundingbox'][0],'y':fullInfo[name]['boundingbox'][1],'z':fullInfo[name]['boundingbox'][2]}
      if (name=="Emulsion_59"):
          #print ("conditions_0=",conditions_0)
          print ("*********")
          #conditionsDB.add_condition(subdet, "emulsion positions", "Geo", conditions_0,None,datetime.datetime.now(), datetime.datetime.max)

    if (name[:10]=="volPassive"):
      #print("path.find Wall_ =",path.find("Wall_")," path.find Wall_ +20=",path.find("Wall_")+20)
      subdet=path[path.find("Wall_"):path.find("Wall_")+20]
      conditions_1[name]={'x':fullInfo[name]['boundingbox'][0],'y':fullInfo[name]['boundingbox'][1],'z':fullInfo[name]['boundingbox'][2]}
      if (name=="volPassive_58"):
          #print ("conditions_1=",conditions_1)
          print ("*********")
          #conditionsDB.add_condition(subdet, "passive material positions", "Geo", conditions_0,None,datetime.datetime.now(), datetime.datetime.max)

    if (name[:12]=="ScintCoreVol"):
      #print("path.find Wall_ =",path.find("Wall_")," path.find Wall_ +6=",path.find("Wall_")+6)
      subdet=path[path.find("ScifiVolume"):path.find("ScifiVolume")+20]
      print("subdet=",subdet," name=",name)
      conditions_2[name]={'x':fullInfo[name]['boundingbox'][0],'y':fullInfo[name]['boundingbox'][1],'z':fullInfo[name]['boundingbox'][2]}
      #conditionsDB.add_condition(subdet, "fibre positions", "Geo", conditions_0,None,datetime.datetime.now(), datetime.datetime.max)


    if (name[:10]=="volVetoBar"):
      subdet=name[:10]


    if (name[:16]=="volMuUpstreamBar"):
      subdet=name[:16]

    if (name[:18]=="volMuDownstreamBar"):
      subdet=name[:18]

    #print ("path=",path," name=",name," sd=",sd," subdet=",subdet)

    #conditionsDB.add_detector(name)
    #conditions_0[name]={'x':fullInfo[name]['boundingbox'][0],'y':fullInfo[name]['boundingbox'][1],'z':fullInfo[name]['boundingbox'][2]}
    #conditionsDB.add_condition(path[1:], "positions", "Geo", conditions_0,None,datetime.datetime.now(), datetime.datetime.max)

    if (1==0):
     if sd == path[1:]:
      # it was the first
      firstsd = True
     else:
      firstsd = False
     if sd=="":
       print("path=",name,"sd=",sd)
       #conditionsDB.add_detector(name)
       conditions= {'x':fullInfo[name]['boundingbox'][0],'y':fullInfo[name]['boundingbox'][1],'z':fullInfo[name]['boundingbox'][2]}
       #conditionsDB.add_condition(name, "xyz", "Geo", conditions,None,datetime.datetime.now(), datetime.datetime.max)
     else:
      if firstsd == False:
         conditionsDB.add_detector(name , path[1:] ) 
         if sd=="volVetoPlane_0_0" and name[:10]=="volVetoBar":
            conditions_0[name]={'x':fullInfo[name]['boundingbox'][0],'y':fullInfo[name]['boundingbox'][1],'z':fullInfo[name]['boundingbox'][2]}
            if name=="volVetoBar_10006" :
              #print ("adding conditions to",path[1:],"conditions_0",conditions_0)
              conditionsDB.add_condition(path[1:], "barpositions", "Geo", conditions_0,None,datetime.datetime.now(), datetime.datetime.max)
         if sd=="volVetoPlane_1_1" and name[:10]=="volVetoBar":
            conditions_1[name]={'x':fullInfo[name]['boundingbox'][0],'y':fullInfo[name]['boundingbox'][1],'z':fullInfo[name]['boundingbox'][2]}
            if name=="volVetoBar_11006" :
              #print ("adding conditions to",path[1:],"conditions_1",conditions_1)
              conditionsDB.add_condition(path[1:], "barpositions", "Geo", conditions_1,None,datetime.datetime.now(), datetime.datetime.max)

         if sd[:5]=="Brick" and name[:8]=="Emulsion":
            conditions_e0[name]={'x':fullInfo[name]['boundingbox'][0],'y':fullInfo[name]['boundingbox'][1],'z':fullInfo[name]['boundingbox'][2]}
            if name=="Emulsion_59" :
               #print ("emulsion path",path[1:])
               conditionsDB.add_condition(path[1:], "emulsionpositions", "Geo", conditions_e0,None,datetime.datetime.now(), datetime.datetime.max)

         if sd[:5]=="Brick" and name[:10]=="volPassive":
            conditions_p0[name]={'x':fullInfo[name]['boundingbox'][0],'y':fullInfo[name]['boundingbox'][1],'z':fullInfo[name]['boundingbox'][2]}
            if name=="volPassive_58" :
               #print ("tungsten path",path[1:])
               conditionsDB.add_condition(path[1:], "tungsten positions", "Geo", conditions_p0,None,datetime.datetime.now(), datetime.datetime.max)

         if sd[:15]=="volMuUpstreamDet" and name[:16]=="volMuUpstreamBar":
            conditions_mu0[name]={'x':fullInfo[name]['boundingbox'][0],'y':fullInfo[name]['boundingbox'][1],'z':fullInfo[name]['boundingbox'][2]}
            if name=="volMuUpstreamBar_24009" :
               #print ("emulsion path",path[1:])
               conditionsDB.add_condition(path[1:], "mu upstream", "Geo", conditions_mu0,None,datetime.datetime.now(), datetime.datetime.max)

         if sd[:17]=="volMuDownstreamDet" and name[:22]=="volMuDownstreamBar_hor":
            conditions_mu0[name]={'x':fullInfo[name]['boundingbox'][0],'y':fullInfo[name]['boundingbox'][1],'z':fullInfo[name]['boundingbox'][2]}
            if name=="volMuDownstreamBar_hor_32059" :
               #print ("emulsion path",path[1:])
               conditionsDB.add_condition(path[1:], "mu downstream horizontal", "Geo", conditions_mu0,None,datetime.datetime.now(), datetime.datetime.max)

         if sd[:17]=="volMuDownstreamDet" and name[:22]=="volMuDownstreamBar_ver":
            conditions_mu0[name]={'x':fullInfo[name]['boundingbox'][0],'y':fullInfo[name]['boundingbox'][1],'z':fullInfo[name]['boundingbox'][2]}
            if name=="volMuDownstreamBar_ver_33060" :
               #print ("emulsion path",path[1:])
               conditionsDB.add_condition(path[1:], "mu downstream vertical", "Geo", conditions_mu0,None,datetime.datetime.now(), datetime.datetime.max)

         if sd[:11]=="FibreVolume" and name[:13]=="VertMatVolume":
            conditions_e0[name]={'x':fullInfo[name]['boundingbox'][0],'y':fullInfo[name]['boundingbox'][1],'z':fullInfo[name]['boundingbox'][2]}
            if name=="VertMatVolume_5136472" :
               #print ("emulsion path",path[1:])
               conditionsDB.add_condition(path[1:], "emulsionpositions", "Geo", conditions_e0,None,datetime.datetime.now(), datetime.datetime.max)

         if sd[:11]=="FibreVolume" and name[:12]=="HorMatVolume":
            conditions_e0[name]={'x':fullInfo[name]['boundingbox'][0],'y':fullInfo[name]['boundingbox'][1],'z':fullInfo[name]['boundingbox'][2]}
            if name=="VertMatVolume_5036472" :
               #print ("emulsion path",path[1:])
               conditionsDB.add_condition(path[1:], "emulsionpositions", "Geo", conditions_e0,None,datetime.datetime.now(), datetime.datetime.max)

      else:
         #scifi structure not yet in geofile, add it by hand:
         #print ("adding name",name,"sd",sd," to condb")
         conditionsDB.add_detector(name , sd)
         #if name[:5]=="Scifi":
         if 1==0:
            conditions_Scifi[name]={'id':name[6:]}
            for l in range(2):
               planesd="plane_"+str(l)
               #print ("planesd",planesd,"name",name)
               conditionsDB.add_detector( planesd,sd+"/"+name )
               for m in range(3):
                  boardsd="board_"+str(m)
                  conditionsDB.add_detector(boardsd, sd+"/"+name+"/"+planesd)
                  for n in range(8):
                     tofpetsd="tofpet_"+str(n)
                     conditionsDB.add_detector(tofpetsd, sd+"/"+name+"/"+planesd+"/"+boardsd)
                     for o in range(64):
                       channelsd="channel_"+str(o)
                       conditionsDB.add_detector(channelsd, sd+"/"+name+"/"+planesd+"/"+boardsd+"/"+tofpetsd)

            if name=="Scifi_4":
               #print ("SciFi conditions=",conditions_Scifi)
               conditionsDB.add_condition(path[1:], "SciFi ", "Geo", conditions_Scifi,None,datetime.datetime.now(), datetime.datetime.max)
         else:
            conditions= {'x':fullInfo[name]['boundingbox'][0],'y':fullInfo[name]['boundingbox'][1],'z':fullInfo[name]['boundingbox'][2]}
            conditionsDB.add_condition(path[1:]+'/'+name, "xyz", "Geo", conditions,None,datetime.datetime.now(), datetime.datetime.max)


    sub_nodes[name] = fullInfo[name]['origin'][2]
    if currentlevel < level and fullInfo[name]['node'].GetNodes():
      add_info(fullInfo[name]['path'], fullInfo[name]['node'], level, currentlevel + 1,
                 print_sub_det_info)

    if currentlevel == 0:
      print_sub_det_info = False
    
# debug=0: data added to conddb
# debug=1: data removed from conddb
debug=0


#fname="~/snd-10jan2021/geofile_full.Ntuple-TGeant4.root"
#fgeom = ROOT.TFile.Open(fname)
#fGeo = fgeom.FAIRGeom
#top = fGeo.GetTopVolume()

currentlevel = 0
#level=5 to get emulsion
level = 2



# Instantiate an API factory
api_factory = APIFactory()
# Call construct_DB_API to get an CDB API instance, the path must lead to a valid config.yml file containing the database configuration

conditionsDB = api_factory.construct_DB_API("/home/eric/snd-10jan2021/sndsw/conditionsDatabase/config.yml")

#value_array = {"x": [5, 2, 6, 3, 7]}

#if debug == 0:
  #add_info("", top, int(level), currentlevel)

# How to add a main detector to the database:
conditionsDB.add_detector("SciFi")
conditions = {"z":0.0,"xdim": 39.0,"ydim": 39.0,"zdim": 3.0,"DZ": 7.790000000000001,"nmats": 3,"nscifi": 5,"channel_width": 0.025,"sipm_edge": 0.017,"charr_gap": 0.020000000000000004,"charr_width": 1.6,"sipm_diegap": 0.006,"SiPMarray_width": 3.254,\
"nsipm_channels": 128,"nsipm_mat": 4,"nsipms": 12,"sipmarr_width": 3.22,"firstChannelX": -19.528,"nfibers_shortrow": 471,"nfibers_longrow": 472,"nfibers_z": 6,"scifimat_width": 12.989999999999998,"scifimat_length": 39.0,"scifimat_z": 0.135,"epoxymat_z": 0.17,\
"scifimat_gap": 0.05,"fiber_length": 39.0,"scintcore_rmax": 0.011,"clad1_rmax": 0.01175,"clad2_rmax": 0.0125,"horizontal_pitch": 0.0275,"vertical_pitch": 0.021,"rowlong_offset": 0.035,"rowshort_offset": 0.0215,"carbonfiber_z": 0.02,"honeycomb_z": 0.5,\
"plastbar_x": 1.5,"plastbar_y": 39.0,"plastbar_z": 0.195,"scifi_separation": 10.790000000000001,"offset_z": -24.71,"timeResol": 0.15,"Xpos0": 4.34,"Ypos0": 298.94,"Zpos0": 15.22,"Xpos1": 4.34,"Ypos1": 311.94,"Zpos1": 15.22,"Xpos2": 4.34,"Ypos2": 324.94,\
"Zpos2": 15.22,"Xpos3": 4.34,"Ypos3": 337.94,"Zpos3": 15.22,"Xpos4": 4.34,"Ypos4": 350.94,"Zpos4": 15.22,"EdgeAX": 22.5,"EdgeAY": 22.5,"EdgeAZ": 0.0,"FirstChannelVX": -19.528000000000002,"FirstChannelVY": -20.0,"FirstChannelVZ": -1.292,"FirstChannelHX": -20.0,\
"FirstChannelHY": -19.528000000000002,"FirstChannelHZ": -0.7070000000000001,"LfirstChannelVX": -19.5135,"LfirstChannelVY": 19.5,"LfirstChannelVZ": 1.185,"LfirstChannelHX": -19.5,"LfirstChannelHY": 19.5178,"LfirstChannelHZ": 0.625,"LocM100": 0.0,"LocM101": 0.0,\
"LocM102": 0.0,"LocM110": 0.0,"LocM111": 0.0,"LocM112": 0.0,"LocM200": 0.0,"LocM201": 0.0,"LocM202": 0.0,"LocM210": 0.0,"LocM211": 0.0,"LocM212": 0.0,"LocM300": 0.0,"LocM301": 0.0,"LocM302": 0.0,"LocM310": 0.0,"LocM311": 0.0,"LocM312": 0.0,"LocM400": 0.0,\
"LocM401": 0.0,"LocM402": 0.0,"LocM410": 0.0,"LocM411": 0.0,"LocM412": 0.0,"LocM500": 0.0,"LocM501": 0.0,"LocM502": 0.0,"LocM510": 0.0,"LocM511": 0.0,"LocM512": 0.0}
conditionsDB.add_condition("SciFi", "Alignment Constants", "Scifi_1", conditions,None,datetime.datetime.now(), datetime.datetime.max)

# How to add a subdetector to a parent detector in the database:
# Params: (subdetector name, parent detector ID)
#conditionsDB.add_detector("Veto" , "Tunnel")
#conditionsDB.add_detector("Target" , "Tunnel")
#conditionsDB.add_detector("Mufilter" , "Tunnel")



# Show all main detector names in the database:
result = conditionsDB.list_detectors()
j=0
#print("Level ",j," :",result)
j+=1


if 1==1:
 results=[]
 for sd in result:
  conditions = conditionsDB.get_conditions_by_tag(sd,'Geo')
  print("conditions of Geo detector",sd," :",conditions)
  results.append(conditionsDB.list_detectors(sd))
  
 #print("Level ",j," :",results)
 j+=1

 for sd in results:
  resultss=[]
  for ssd in sd:
     if conditionsDB.list_detectors(ssd) != [] :
        resultss.append(conditionsDB.list_detectors(ssd))
        conditions = conditionsDB.get_conditions_by_tag(ssd,'Geo')
        print("conditions of Geo sub detector",ssd," :",conditions)

 
        
 print('Brick_0 conditions',result)
 result = conditionsDB.get_conditions('volTarget_1/Wall_0/Row_0/Brick_1')
 print('Brick_1 conditions',result)
 result = conditionsDB.get_conditions('volTarget_1/Wall_0/Row_1/Brick_0')
 print('Row 1 Brick_0 conditions',result) 
 result = conditionsDB.get_conditions('volTarget_1/Wall_0/Row_1/Brick_1')
 print('Row_1 Brick 1 conditions',result)  
 result = conditionsDB.get_conditions('volTarget_1/Wall_1/Row_1/Brick_1')
 print('Wall 1 Row_1 Brick 1 conditions',result)  
       
# Adding a condition to the database
# Name-Tag and Name-CollectedAt combinations should be unique in the database
# Dates can be parsed as a string: year-month-day hour:minutes:second    OR    as a datetime object
#conditionsDB.add_condition("detector3/subdetector1", "conditionName1", "SampleTag", "2020-03-21 18:14", value_array, "testType", "2020-03-21 18:12", "2020-05-20")
#conditionsDB.add_condition("detector3/subdetector1", "conditionsName1", "SampleTag2", datetime.datetime(2020,3,22,20,20), value_array, "testType", datetime.datetime(2020,3,23,18,12), datetime.datetime(2020,3,23,18,12))
# A condition can also be added to the database without specifying the type, valid_since and/or valid_until, they will take the default values: None, datetime.datetime.now(), datetime.datetime.MAX respectively
#conditionsDB.add_condition("detector3/subdetector1", "conditionsName1", "SampleTag3", datetime.datetime(2020,3,25,20,20), value_array)

# Get detector dictionary by specifying the detectorID: "Detector/subdetector/subdetector ..."
# This function gets subdetector: "subdetector1" of detector: "detector3"
#result = conditionsDB.get_detector("detector3/subdetector1")
#print(result)

# Get a list of all conditions of a detector
# This function gets a list of conditions in subdetector: "subdetector1" of detector: "detector3"
#result = conditionsDB.get_conditions("detector3/subdetector1")
#print(result)

# Get a list of all conditions with a specific tag for the specified detector
# This function gets a list of conditions in subdetector: "subdetector1" of detector: "detector3" WITH the tag "SampleTag"
#result = conditionsDB.get_conditions_by_tag("detector3/subdetector1", "SampleTag")
#print(result)

# Get a condition dictionary by specifying the detectorID, condition name, condition tag
# This function gets a condition in subdetector: "subdetector1" of detector: "detector3" WITH the name "conditionName1" AND the tag "SampleTag2"
#result = conditionsDB.get_condition_by_name_and_tag("detector3/subdetector1", "conditionsName1", "SampleTag2")
#print(result)

# Get a condition dictionary by specifying the detectorID and condition collected_at
# This function gets a condition in subdetector: "subdetector1" of detector: "detector3" WITH the name "conditionName1" AND the collected_at: 2020-03-21 18:14:00
# If a certain time accuracy is omitted then defaults are assumed. See API documentation for details
#conditionsDB.get_condition_by_name_and_collection_date("detector3/subdetector1", "conditionName1",  "2020-03-21 18:14")

# Get a list of conditions by specifying the detectorID, condition name, and date where it should be valid
# This function gets a condition in subdetector: "subdetector1" of detector: "detector3" WITH the name "conditionName1" AND the valid_since <= 2020-03-22 00:00:00 AND the valid_until >= 2020-03-22 00:00:00
#conditionsDB.get_conditions_by_name_and_validity("detector3/subdetector1", "conditionName1", "2020-03-22")

# Update a condition type, valid_since and valid_until by specifying the detectorID, condition name and condition tag
# This function sets the following values to the subdetector: "subdetector1" of detector: "detector3" WITH the name "conditionName1" AND the tag "SampleTag"
# Values updated: Type:  "testType2"   valid_since: "2020-03-20 18:12:00"    valid_until: stays the same
#conditionsDB.update_condition_by_name_and_tag("detector3/subdetector1", "conditionName1", "SampleTag", "testType2", "2020-03-20 18:12")

# EXECUTE WITH CARE: Removes a subdetector including all of it's values from the database
# This function removes subdetector: "subdetector1" of detector: "detector3" and all of it's values from the database

if 1==1:
 if debug==1:
   conditionsDB.remove_detector("Tunnel_1")
   conditionsDB.remove_detector("volTarget_1")
   conditionsDB.remove_detector("volVeto_1")
   conditionsDB.remove_detector("volMuFilter_1")
   conditionsDB.remove_detector("daq")
   conditionsDB.remove_detector("Detector_0")
