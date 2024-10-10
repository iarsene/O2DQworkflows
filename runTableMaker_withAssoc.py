#!/usr/bin/env python3

from ast import parse
import sys
import json
import os
import argparse

parser = argparse.ArgumentParser(description='Arguments to pass')
parser.add_argument('cfgFileName', metavar='text', default='config.json', help='config file name')
parser.add_argument('-runData', help="Run over data", action="store_true")
parser.add_argument('-runMC', help="Run over MC", action="store_true")
parser.add_argument('--arg', help='Configuration argument')
parser.add_argument('--add_mc_conv', help="Add the converter from mcparticle to mcparticle+001", action="store_true")
parser.add_argument('--add_fdd_conv', help="Add the fdd converter", action="store_true")
parser.add_argument('--add_zdc_conv', help="Add the zdc converter", action="store_true")
parser.add_argument('--add_bc_conv', help="Add the BC converter", action="store_true")
parser.add_argument('--add_track_prop', help="Add track propagation to the innermost layer (TPC or ITS)", action="store_true")
parser.add_argument("--add_weakdecay_ind", help = "Add Converts V0 and cascade version 000 to 001", action = "store_true")
parser.add_argument("--add_col_conv", help = "Add the converter from collision to collision+001", action = "store_true")
parser.add_argument("--add_track_extra_conv", help = "Add the converter from track_extra to track_extra+001", action = "store_true")
parser.add_argument("--add_mft_conv", help = "Add the converter from mfttrack_001 to mfttrack", action = "store_true")
extrargs = parser.parse_args()

commonDeps = ["o2-analysis-timestamp", "o2-analysis-event-selection", "o2-analysis-multiplicity-table"]
#commonDeps = ["o2-analysis-timestamp", "o2-analysis-event-selection"]
barrelDeps = ["o2-analysis-trackselection", "o2-analysis-trackextension","o2-analysis-pid-tof-base", "o2-analysis-pid-tof", "o2-analysis-pid-tof-full", "o2-analysis-pid-tof-beta", "o2-analysis-pid-tpc-base", "o2-analysis-pid-tpc-full", "o2-analysis-track-to-collision-associator"]
#barrelDeps = ["o2-analysis-trackselection","o2-analysis-pid-tof-base", "o2-analysis-pid-tof", "o2-analysis-pid-tof-full", "o2-analysis-pid-tof-beta", "o2-analysis-pid-tpc-full"]
muonDeps = ["o2-analysis-fwdtrackextension", "o2-analysis-fwdtrack-to-collision-associator"]
#muonDeps = ["o2-analysis-fwdtrackextension"]
specificDeps = {
  "processPP": [],
  "processPPBarrelOnly": [],
  "processPPMuonOnly": [],
  "processPPMuonMFT": [],
  "processPPWithFilter": ["o2-analysis-dq-filter-pp-with-association"],
  "processPPWithFilterBarrelOnly": ["o2-analysis-dq-filter-pp-with-association"],
  "processPPWithFilterMuonOnly": ["o2-analysis-dq-filter-pp-with-association"],
  "processPPWithFilterMuonMFT": ["o2-analysis-dq-filter-pp-with-association"],
  "processPbPb": [],
  "processPbPbBarrelOnly": [],
  "processPbPbMuonOnly": [],
  "processPbPbMuonMFT": []
}

# Definition of all the tables we may write
tables = {
  "ReducedEvents" : {"table": "AOD/REDUCEDEVENT/0"},
  "ReducedEventsExtended" : {"table": "AOD/REEXTENDED/0"},
  "ReducedEventsVtxCov" : {"table": "AOD/REVTXCOV/0"},
  "ReducedEventsQvector" : {"table": "AOD/REQVECTOR/0"},
  "ReducedEventsMultPV" : {"table": "AOD/REMULTPV/0"},
  "ReducedEventsMultAll" : {"table": "AOD/REMULTALL/0"},
  "ReducedTracks" : {"table": "AOD/REDUCEDTRACK/0"},
  "ReducedTracksBarrel" : {"table": "AOD/RTBARREL/0"},
  "ReducedTracksBarrelCov" : {"table": "AOD/RTBARRELCOV/0"},
  "ReducedTracksBarrelPID" : {"table": "AOD/RTBARRELPID/0"},
  "ReducedTracksBarrelLabels" : {"table": "AOD/RTBARRELLABELS/0"},
  "ReducedMuons" : {"table": "AOD/REDUCEDMUON/0"},
  "ReducedMuonsExtra" : {"table": "AOD/RTMUONEXTRA/0"},
  "ReducedMuonsCov" : {"table": "AOD/RTMUONCOV/0"},
  "ReducedMuonsLabels" : {"table": "AOD/RTMUONSLABELS/0"},
  "DalitzBits" : {"table": "AOD/DALITZBITS/0"},
  "ReducedMFTTracks" : {"table": "AOD/REDUCEDMFT/0"},
  "ReducedMFTTracksExtra" : {"table": "AOD/RMFTEXTRA/0"},
  "ReducedTracksAssoc" : {"table": "AOD/RTASSOC/0"},
  "ReducedMuonsAssoc" : {"table": "AOD/RMASSOC/0"},
  "ReducedMFTAssoc" : {"table": "AOD/RMFTASSOC/0"},
  "ReducedMCEvents" : {"table": "AOD/REDUCEDMCEVENT/0"},
  "ReducedMCEventLabels" : {"table": "AOD/REMCCOLLBL/0"},
  "ReducedMCTracks" : {"table": "AOD/REDUCEDMCTRACK/0"},
  "ReducedTracksBarrelLabels" : {"table": "AOD/RTBARRELLABELS/0"},
  "ReducedMuonsLabels" : {"table": "AOD/RTMUONSLABELS/0"}
}
# Tables to be written, per process function
commonTables = ["ReducedEvents", "ReducedEventsExtended", "ReducedEventsVtxCov", "ReducedEventsMultPV", "ReducedEventsMultAll"]
barrelCommonTables = ["ReducedTracks","ReducedTracksBarrel","ReducedTracksBarrelPID", "ReducedTracksBarrelCov", "ReducedTracksAssoc"]
muonCommonTables = ["ReducedMuons", "ReducedMuonsExtra", "ReducedMuonsAssoc", "ReducedMuonsCov"]
#muonCommonTables = ["ReducedMuons", "ReducedMuonsExtra", "ReducedMFTTracks", "ReducedMFTTracksExtra", "ReducedMuonsAssoc", "ReducedMFTAssoc"]
specificTables = {
  "processPP": ["ReducedMFTTracks", "ReducedMFTTracksExtra", "ReducedMFTAssoc"],
  "processPPBarrelOnly": [],
  "processPPMuonOnly": ["ReducedMFTTracks", "ReducedMFTTracksExtra", "ReducedMFTAssoc"],
  "processPPMuonMFT": ["ReducedMFTTracks", "ReducedMFTTracksExtra", "ReducedMFTAssoc"],
  "processPPWithFilter": ["ReducedMFTTracks", "ReducedMFTTracksExtra", "ReducedMFTAssoc"],
  "processPPWithFilterBarrelOnly": [],
  "processPPWithFilterMuonOnly": [],
  "processPPWithFilterMuonMFT": ["ReducedMFTTracks", "ReducedMFTTracksExtra", "ReducedMFTAssoc"],
  "processPbPb": ["ReducedMFTTracks", "ReducedMFTTracksExtra", "ReducedMFTAssoc"],
  "processPbPbBarrelOnly": [],
  "processPbPbMuonOnly": [],
  "processPbPbMuonMFT": ["ReducedMFTTracks", "ReducedMFTTracksExtra", "ReducedMFTAssoc"]
}

# Make some checks on provided arguments
if len(sys.argv) < 3:
  print("ERROR: Invalid syntax! The command line should look like this:")
  print("  ./runTableMaker.py <yourConfig.json> <runData|runMC> [task:param:value] ...")
  sys.exit()

# Load the configuration file provided as the first parameter
config = {}
with open(extrargs.cfgFileName) as configFile:
  config = json.load(configFile)

# Check whether we run over data or MC
if not (extrargs.runMC or extrargs.runData):
  print("ERROR: You have to specify either runMC or runData !")
  sys.exit()

runOverMC = False
if (extrargs.runMC):
  runOverMC = True

print("runOverMC ",runOverMC)

# Delete trackextension dependency if track-propagation dependency provided (for compatibility)
if extrargs.add_track_prop:
  barrelDeps.remove("o2-analysis-trackextension")

if extrargs.arg != "" and extrargs.arg is not None:
  args = [line.split(':') for line in extrargs.arg.split(',') if line]
  for threeIndex in args:
    if len(threeIndex) != 3:
      print("ERROR: Wrong parameter syntax for --arg: ", threeIndex, " in ", extrargs.arg)
      print("Correct syntax: task:param:value,task:param:value ... ")
      print("Example: --arg table-maker:processBarrelOnly:true")
      sys.exit()
  for arg in args:
    config[arg[0]][arg[1]] = arg[2]

taskNameInConfig = "table-maker"
taskNameInCommandLine = "o2-analysis-dq-table-maker-with-assoc"
if runOverMC == True:
  taskNameInConfig = "table-maker-m-c"
  taskNameInCommandLine = "o2-analysis-dq-table-maker-mc-with-assoc"


if not taskNameInConfig in config:
  print("ERROR: Task to be run not found in the configuration file!")
  sys.exit()

# Write the updated configuration file into a temporary file
updatedConfigFileName = "tempConfig.json"
with open(updatedConfigFileName,'w') as outputFile:
  json.dump(config, outputFile, indent = 2)

# Check which dependencies need to be run
depsToRun = {}
for dep in commonDeps:
  depsToRun[dep] = 1

for processFunc in specificDeps.keys():
  if not processFunc in config[taskNameInConfig].keys():
    continue
  if config[taskNameInConfig][processFunc] == "true":
    if "processPP" in processFunc or "processPbPb" in processFunc:
      for dep in barrelDeps:
        depsToRun[dep] = 1
      for dep in muonDeps:
        depsToRun[dep] = 1  
    if "BarrelOnly" in processFunc:
      for dep in muonDeps:
        depsToRun[dep] = 0
    if "Muon" in processFunc:
      for dep in barrelDeps:
        depsToRun[dep] = 0    
    for dep in specificDeps[processFunc]:
      depsToRun[dep] = 1

# Check which tables are required in the output
tablesToProduce = {}
for table in commonTables:
  tablesToProduce[table] = 1

if runOverMC == True:
  tablesToProduce["ReducedMCEvents"] = 1
  tablesToProduce["ReducedMCEventLabels"] = 1

for processFunc in specificDeps.keys():
  if not processFunc in config[taskNameInConfig].keys():
    continue
  if config[taskNameInConfig][processFunc] == "true":
    print("processFunc ========")
    print(processFunc)
    if "processPP" in processFunc or "processPbPb" in processFunc:
      print("common barrel tables==========")
      for table in barrelCommonTables:
        print(table)
        tablesToProduce[table] = 1
      for table in muonCommonTables:
        print(table)
        tablesToProduce[table] = 1  
      if runOverMC == True:
        tablesToProduce["ReducedTracksBarrelLabels"] = 1
        tablesToProduce["ReducedMuonsLabels"] = 1
    if "BarrelOnly" in processFunc:
      print("common muon tables==========")
      for table in muonCommonTables:
        print(table)
        tablesToProduce[table] = 0
      if runOverMC == True:
        tablesToProduce["ReducedMuonsLabels"] = 0
    if "Muon" in processFunc:
      print("common muon tables==========")
      for table in barrelCommonTables:
        print(table)
        tablesToProduce[table] = 0
      if runOverMC == True:
        tablesToProduce["ReducedTracksBarrelLabels"] = 0    
    if runOverMC == True:
      tablesToProduce["ReducedMCTracks"] = 1
    print("specific tables==========")
    for table in specificTables[processFunc]:
      print(table)
      tablesToProduce[table] = 1

# Generate the aod-writer output descriptor json file
writerConfig = {}
writerConfig["OutputDirector"] = {
  "debugmode": True,
  "resfile": "reducedAod",
  "resfilemode": "RECREATE",
  "ntfmerge": 1,
  "OutputDescriptors": []
}
iTable = 0
for table in tablesToProduce.keys():
  writerConfig["OutputDirector"]["OutputDescriptors"].insert(iTable, tables[table])
  iTable += 1

writerConfigFileName = "aodWriterTempConfig.json"
with open(writerConfigFileName,'w') as writerConfigFile:
  json.dump(writerConfig, writerConfigFile, indent = 2)

print(writerConfig)
#sys.exit()

commandToRun = taskNameInCommandLine + " --configuration json://" + updatedConfigFileName + " --severity error --shm-segment-size 12000000000 --aod-writer-json " + writerConfigFileName + " -b"
for dep in depsToRun.keys():
  if depsToRun[dep]:
      commandToRun += " | " + dep + " --configuration json://" + updatedConfigFileName + " -b"

if extrargs.add_mc_conv:
    commandToRun += " | o2-analysis-mc-converter --configuration json://" + updatedConfigFileName + " -b"

if extrargs.add_fdd_conv:
    commandToRun += " | o2-analysis-fdd-converter --configuration json://" + updatedConfigFileName + " -b"
    
if extrargs.add_zdc_conv:
    commandToRun += " | o2-analysis-zdc-converter --configuration json://" + updatedConfigFileName + " -b"

if extrargs.add_bc_conv:
    commandToRun += " | o2-analysis-bc-converter --configuration json://" + updatedConfigFileName + " -b"

if extrargs.add_track_prop:
    commandToRun += " | o2-analysis-track-propagation --configuration json://" + updatedConfigFileName + " -b"

if extrargs.add_weakdecay_ind:
    commandToRun += " | o2-analysis-weak-decay-indices --configuration json://" + updatedConfigFileName + " -b"

if extrargs.add_col_conv:
    commandToRun += " | o2-analysis-collision-converter --configuration json://" + updatedConfigFileName + " -b"

if extrargs.add_track_extra_conv:
    commandToRun += " | o2-analysis-tracks-extra-converter --configuration json://" + updatedConfigFileName + " -b"

if extrargs.add_mft_conv:
    commandToRun += " | o2-analysis-mft-tracks-converter --configuration json://" + updatedConfigFileName + " -b"

print("====================================================================================================================")
print("Command to run:")
print(commandToRun)
print("====================================================================================================================")
print("Tables to produce:")
print(tablesToProduce.keys())
print("====================================================================================================================")
#sys.exit()

os.system(commandToRun)
