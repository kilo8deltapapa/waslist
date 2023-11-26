#!/usr/bin/env python3

# waslist.py

"""
Description: This program generates a list of USA states that have been
confirmed, a list of unconfirmed states,
and a mapchartSave.txt file for upload to
https://www.mapchart.net/japan.html to visualize the states.

The following ADIF tags in the file being analyzied are used:
<STATION_CALLSIGN>  Your callsign; Optional, Needed for -c option
<STATE> Prefecture of station worked; Required
<DXCC> DXCC entity of station worked; Required
<MODE> Mode used; Optional, Needed for -m option
<BAND> Band used; Optional, Needed for -b option
<SAT_NAME> Name of satellite used; Optional, needed for -s option
<PROP_MODE> Propagation mode; Optional, needed for --satonly and --nosat options

This can be obtained by using the ARRL Logbook of the World Query by
Rick Murphy K1MU found at URL: https://www.rickmurphy.net/lotwquery.htm

Author: Douglas C. Papay K8DP
Date Created: November 23, 2023
Date Modified: November 24, 2023
Version: 1.1
Python Version: 3.10.5
Dependencies: argparse,adif-io,pyhamtools
License: MIT License
"""

import sys
import datetime
import csv
import argparse
import adif_io
from pyhamtools.locator import calculate_distance

VERSION = 1.1

def make_mapfile(all_list,need_list,filename):
    with open(filename, "w", encoding="utf-8") as f:
        print('{"groups":{"#e0f3db":{"label":"Confirmed LoTW","paths":[', end="", file=f)

        for i,p in enumerate(all_list):
            if i < len(all_list) - 1:
                print('"' + p + '"',end=",", file=f)
            else:
                print('"' + p + '"',end="", file=f)

        print(']},"#ffff33":{"label":"Needed","paths":[',end="", file=f)

        for i,p in enumerate(need_list):
            if i < len(need_list) - 1:
                print('"' + p + '"',end=",", file=f)
            else:
                print('"' + p + '"', file=f)
   #     if callsign != "":
   #         callsign = callsign + ' - '
        print(']}},"title":"'+ ', '.join(callsign_list) +' ",\
        "hidden":[],"background":"#fff","borders":"#000",\
        "legendFont":"Helvetica","legendFontColor":"#000",\
        "legendBgColor":"#00000000","legendWidth":150,"areBordersShown":true,\
        "defaultColor":"#d1dbdd","labelsColor":"#000000",\
        "strokeWidth":"medium","areLabelsShown":true,\
        "legendPosition":"bottom_left","legendSize":"medium",\
        "legendStatus":"show","scalingPatterns":true,\
        "legendRowsSameColor":true,"legendColumnCount":2}', file=f)

def lookup_name(abbreviation_list):
    name_list = []
    #print(abbreviation_list)
    for a in abbreviation_list:
        name_list.append(prov_names[prov_defs.index(a)].replace(" ", "_"))
    return name_list

# Initialize parser
parser = argparse.ArgumentParser()

# Adding optional argument
parser.add_argument('filename', help = "LoTW ADIF")
parser.add_argument("-g", "--grid", help = "list only contacts made within 50 \
miles (80 kilometers) of this grid", required=True)
parser.add_argument("-c", "--call", nargs='+', help = "list of callsigns, if \
not specified all callsigns are considered")
parser.add_argument("-b", "--band", help = "band (eg. 20M, 2M, 70CM, etc...), \
if not specified all bands are considered")
parser.add_argument("-m", "--mode", help = "mode (eg. CW, SSB, FT8, etc...), \
f not specified all modes are considered")
parser.add_argument("-s", "--sat", help = "satellite name (eg. RS-44, IO-117, \
etc...), if not specified all satellites are included")
parser.add_argument("--satonly", action='store_true', help = "include only \
satellite QSOs")
parser.add_argument("--nosat", action='store_true', help = "exclude satellite \
QSOs")
parser.add_argument("--canada", action='store_true', help = "include Canadian \
provinces/territories")
parser.add_argument("--dc", action='store_true', help = "include District of \
Colombia")
print(f"WAS List by K8DP - Version {VERSION}")
# Read arguments from command line
args = parser.parse_args()
if args.filename:
    input_filename = args.filename
else:
    sys.exit()

if args.call:
    callsign_list = args.call
    callsign_list = [x.upper() for x in callsign_list]
else:
    callsign_list = []

if args.band:
    BAND = args.band.upper()
else:
    BAND = ""

if args.mode:
    MODE = args.mode.upper()
else:
    MODE = ""

if args.sat:
    SAT = args.sat.upper()
else:
    SAT = ""

if args.grid:
    GRID = args.grid.upper()
else:
    GRID = ""

#Read state list from file
state_defs = []
with open("usa_states.txt", "r", encoding="utf-8") as file:
    while True:
        line = file.readline().strip()
        if not line:
            break
        val = line.split("\t")
        state_defs.append(val[0])

#Read province/territory from file
prov_defs = []
prov_names = []
if args.canada:
    with open("ve_provinces.txt", "r", encoding="utf-8") as file:
        while True:
            line = file.readline().strip()
            if not line:
                break
            val = line.split("\t")
            prov_defs.append(val[0])
            prov_names.append(val[1])

#not part of WAS, but could be used for mapcharts
if args.dc:
    state_defs.append("DC")

states_list = []
provs_list = []
was_needed_list = []
rac_needed_list = []
qsocall_list = []
was_list = []
rac_list = []

print(f"Reading {input_filename}")

#read ADIF file into lists
qsos_raw, adif_header = adif_io.read_from_file(input_filename)

# The QSOs are probably sorted by QSO time already, but make sure:
for qso in qsos_raw:
    qso["t"] = adif_io.time_on(qso)
qsos_raw_sorted = sorted(qsos_raw, key = lambda qso: qso["t"])

#look through qsos for those that match criteria
for qso in qsos_raw_sorted:

    station_callsign = qso["STATION_CALLSIGN"].upper()
    if station_callsign not in qsocall_list:
        qsocall_list.append(station_callsign)

    #not all records have SAT_NAME
    try:
        SAT_NAME = qso["SAT_NAME"].upper()
    except KeyError as e:
        #key does not exist
        SAT_NAME = ""
    try:
        PROP_MODE = qso["PROP_MODE"]
    except KeyError as e:
        #key does not exist
        PROP_MODE = ""

    try:
        if args.grid:
            GRID_DIST = calculate_distance(GRID,qso["MY_GRIDSQUARE"])
        else:
            GRID_DIST = 0
    except KeyError as e:
        #key does not exist
        GRID_DIST = 0

    try:
        #read only records that are with USA DXCC = 291, 110, or 6 
        #and conform to the specified band/mode/etc..
        if (qso["DXCC"] == '291' or qso["DXCC"] == '110' \
            or qso["DXCC"] == '6'):
            if ((station_callsign in callsign_list) or len(callsign_list) == 0):
                if (SAT in (SAT_NAME, '') or not SAT):
                    if ((PROP_MODE == "SAT" and args.satonly) \
                    or (not args.satonly and not args.nosat) \
                    or (not PROP_MODE and args.nosat)):
                        if (MODE in (qso['MODE'], '') or not MODE):
                            if (BAND in (qso['BAND'], '') or not BAND):
                                if qso["STATE"] not in states_list \
                                and qso["STATE"] in state_defs:
                                    if GRID_DIST <= 80.0: 
                                        d = adif_io.time_on(qso)
                                        #d = datetime.datetime.strptime(qso['QSO_DATE'], '%Y%m%d')
                                        qso_band = qso['BAND']
                                        if PROP_MODE == "SAT":
                                            #qso_band = qso['SAT_NAME']+"("+qso_band+")"
                                            qso_band = qso['SAT_NAME']
                                        states_list.append(qso["STATE"])

                                        was_list.append([qso['STATE'],
                                        qso['CALL'],\
                                        d.strftime("%m-%d-%Y"),
                                        d.strftime("%H:%M:%S"),\
                                        qso_band,qso['MODE']])
        elif qso["DXCC"] == '1':
            if ((station_callsign in callsign_list) or len(callsign_list) == 0):
                if (SAT in (SAT_NAME, '') or not SAT):
                    if ((PROP_MODE == "SAT" and args.satonly) \
                    or (not args.satonly and not args.nosat) \
                    or (not PROP_MODE and args.nosat)):
                        if (MODE in (qso['MODE'], '') or not MODE):
                            if (BAND in (qso['BAND'], '') or not BAND):
                                if qso["STATE"] not in provs_list \
                                and qso["STATE"] in prov_defs:
                                    d = adif_io.time_on(qso)
                                    qso_band = qso['BAND']
                                    if PROP_MODE == "SAT":
                                        #qso_band = qso['SAT_NAME']+"("+qso_band+")"
                                        qso_band = qso['SAT_NAME']
#                                    states_list.append(qso["STATE"])
                                    provs_list.append(qso["STATE"])

                                    rac_list.append([qso['STATE'],qso['CALL'],\
                                    d.strftime("%Y-%m-%d"),
                                    d.strftime("%H:%M:%S"),\
                                    qso_band,qso['MODE'],"LoTW"])

    except KeyError as e:
        #key does not exist
        pass

print("   Done.\n")

print(f"Callsigns found in ADIF: {len(qsocall_list)}")
for c in qsocall_list:
    print("   ",c)
print()

print("Records in ADIF:", len(qsos_raw))
print()

#sort the state list
states_list.sort()

for state in state_defs:
    if state not in states_list:
        was_needed_list.append(state)
print("States Confirmed:", len(was_list))
print("States Needed:",len(state_defs)-len(was_list))
for p in was_needed_list:
    print("   ",p,end="\n")
print()

if args.canada:
    for prov in prov_defs:
        if prov not in provs_list:
            rac_needed_list.append(prov)
    print("Provinces/Territories Confirmed:", len(provs_list))
    print("Provinces/Territories Needed:",len(prov_defs)-len(rac_list))
    for p in rac_needed_list:
        print("   ",p,end="\n")
    print()

if len(states_list) > 0:

    print("Generating waslist.csv...")
    was_list.sort(key=lambda x: x[0])

    with open('waslist.csv', 'w', encoding="utf-8") as f:
        # using csv.writer method from CSV package
        write = csv.writer(f)
        for was in was_list:                  
            write.writerow(was)                
                                                
    print("   Done.\n")      

    print("Generating raclist.csv...")
    #rac_list.sort(key=lambda x: x[2])
    rac_list.sort(key=lambda i: prov_defs.index(i[0]))

    with open('raclist.csv', 'w', encoding="utf-8") as f:
        # using csv.writer method from CSV package
        write = csv.writer(f)
        for rac in rac_list:                  
            write.writerow(rac)                
                                                
    print("   Done.\n")      

    print("Generating mapchart.net file(s)...")

    MAP_FILENAME = "mapchartSave-usa.txt"
    make_mapfile(states_list,was_needed_list,MAP_FILENAME)

    if args.canada:
        MAP_FILENAME = "mapchartSave-canada.txt"
        make_mapfile(lookup_name(provs_list),lookup_name(rac_needed_list),MAP_FILENAME)
        MAP_FILENAME = "mapchartSave-usa_canada.txt"
        make_mapfile(states_list+provs_list,was_needed_list+rac_needed_list,MAP_FILENAME)


    print("   Done.\n")
    print("File", MAP_FILENAME, "can be uploaded \
to https://www.mapchart.net/ for map display.\n")
else:
    print("No states confirmed, mapchart.net file was not created!")
