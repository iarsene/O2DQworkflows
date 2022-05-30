#!/usr/bin/env python3

import sys
import json
import os

commonDeps = ["o2-analysis-timestamp", "o2-analysis-event-selection", "o2-analysis-multiplicity-table"]
barrelDeps = ["o2-analysis-trackselection", "o2-analysis-track-propagation", "o2-analysis-pid-tof", "o2-analysis-pid-tof-full", "o2-analysis-pid-tof-beta", "o2-analysis-pid-tof-base", "o2-analysis-pid-tpc-full"]
specificDeps = {
  "processFull" : [],
  "processFullTiny" : [],
  "processFullWithCov" : [],
  "processFullWithCent" : ["o2-analysis-centrality-table"],
  "processBarrelOnly" : [],
  "processBarrelOnlyWithCov" : [],
  "processBarrelOnlyWithV0Bits" : ["o2-analysis-dq-v0-selector", "o2-analysis-weak-decay-indices"],
  "processBarrelOnlyWithEventFilter" : ["o2-analysis-dq-filter-pp"],
  "processBarrelOnlyWithCent" : ["o2-analysis-centrality-table"],
  "processMuonOnly" : [],
  "processMuonOnlyWithCov" : [],
  "processMuonOnlyWithCent" : ["o2-analysis-centrality-table"],
  "processMuonOnlyWithFilter" : ["o2-analysis-dq-filter-pp"]
  #"processFullWithCentWithV0Bits" : ["o2-analysis-centrality-table","o2-analysis-dq-v0-selector", "o2-analysis-weak-decay-indices"],
  #"processFullWithEventFilterWithV0Bits" : ["o2-analysis-dq-filter-pp","o2-analysis-dq-v0-selector", "o2-analysis-weak-decay-indices"],
} 

# Definition of all the tables we may write
tables = {
  "ReducedEvents" : {"table": "AOD/REDUCEDEVENT/0", "treename": "ReducedEvents"},
  "ReducedEventsExtended" : {"table": "AOD/REEXTENDED/0", "treename": "ReducedEventsExtended"},
  "ReducedEventsVtxCov" : {"table": "AOD/REVTXCOV/0", "treename": "ReducedEventsVtxCov"},
  "ReducedMCEventLabels" : {"table": "AOD/REMCCOLLBL/0", "treename": "ReducedMCEventLabels"},
  "ReducedMCEvents" : {"table": "AOD/REMC/0", "treename": "ReducedMCEvents"},
  "ReducedTracks" : {"table": "AOD/REDUCEDTRACK/0", "treename": "ReducedTracks"},
  "ReducedTracksBarrel" : {"table": "AOD/RTBARREL/0", "treename": "ReducedTracksBarrel"},
  "ReducedTracksBarrelCov" : {"table": "AOD/RTBARRELCOV/0", "treename": "ReducedTracksBarrelCov"},
  "ReducedTracksBarrelPID" : {"table": "AOD/RTBARRELPID/0", "treename": "ReducedTracksBarrelPID"},
  "ReducedTracksBarrelLabels" : {"table": "AOD/RTBARRELLABELS/0", "treename": "ReducedTracksBarrelLabels"},
  "ReducedMCTracks" : {"table": "AOD/RTMC/0", "treename": "ReducedMCTracks"},
  "ReducedMuons" : {"table": "AOD/RTMUON/0", "treename": "ReducedMuons"},
  "ReducedMuonsExtra" : {"table": "AOD/RTMUONEXTRA/0", "treename": "ReducedMuonsExtra"},
  "ReducedMuonsCov" : {"table": "AOD/RTMUONCOV/0", "treename": "ReducedMuonsCov"},
  "ReducedMuonsLabels" : {"table": "AOD/RTMUONSLABELS/0", "treename": "ReducedMuonsLabels"}
}
# Tables to be written, per process function
commonTables = ["ReducedEvents", "ReducedEventsExtended", "ReducedEventsVtxCov"]
barrelCommonTables = ["ReducedTracks","ReducedTracksBarrel","ReducedTracksBarrelPID"]
muonCommonTables = ["ReducedMuons", "ReducedMuonsExtra"]
specificTables = {
  "processFull" : [],
  "processFullTiny" : [],
  "processFullWithCov" : ["ReducedTracksBarrelCov", "ReducedMuonsCov"],
  "processFullWithCent" : [],
  "processBarrelOnly" : [],
  "processBarrelOnlyWithCov" : ["ReducedTracksBarrelCov"],
  "processBarrelOnlyWithV0Bits" : [],
  "processBarrelOnlyWithEventFilter" : [],
  "processBarrelOnlyWithCent" : [],
  "processMuonOnly" : [],
  "processMuonOnlyWithCov" : ["ReducedMuonsCov"],
  "processMuonOnlyWithCent" : [],
  "processMuonOnlyWithFilter" : []
}

# Make some checks on provided arguments
if len(sys.argv) < 3:
  print("ERROR: Invalid syntax! The command line should look like this:")
  print("  ./runTableMaker.py <yourConfig.json> <runData|runMC|runMCwithConverter|runMCwithFddConverter> [task:param:value] ...")
  sys.exit()

# Load the configuration file provided as the first parameter
config = {}
with open(sys.argv[1]) as configFile:
  config = json.load(configFile)

# Check whether we run over data or MC
if not ((sys.argv[2] == "runMC") or (sys.argv[2] == "runMCwithConverter") or (sys.argv[2] == "runData") or (sys.argv[2] == "runMCwithFddConverter")):
  print("ERROR: You have to specify either runMC or runData !")
  sys.exit()

runOverMC = False
if ((sys.argv[2] == "runMC") or (sys.argv[2] == "runMCwithConverter") or (sys.argv[2] == "runMCwithFddConverter")):
  runOverMC = True

print("runOverMC ",runOverMC)

# Get all the user required modifications to the configuration file
for count in range(3, len(sys.argv)):
  param = sys.argv[count].split(":")
  if len(param) != 3:
    print("ERROR: Wrong parameter syntax: ", param)
    sys.exit()
  config[param[0]][param[1]] = param[2]


taskNameInConfig = "table-maker"
taskNameInCommandLine = "o2-analysis-dq-table-maker"
if runOverMC == True:
  taskNameInConfig = "table-maker-m-c"
  taskNameInCommandLine = "o2-analysis-dq-table-maker-mc"

if not taskNameInConfig in config:
  print("ERROR: Task to be run not found in the configuration file!")
  sys.exit()

# Write the updated configuration file into a temporary file
updatedConfigFileName = "tempConfig.json"
with open(updatedConfigFileName,'w') as outputFile:
  json.dump(config, outputFile)

# Check which dependencies need to be run  
depsToRun = {}
for dep in commonDeps:
  depsToRun[dep] = 1

for processFunc in specificDeps.keys():
  if not processFunc in config[taskNameInConfig].keys():
    continue        
  if config[taskNameInConfig][processFunc] == "true":      
    if "processFull" in processFunc or "processBarrel" in processFunc:
      for dep in barrelDeps:
        depsToRun[dep] = 1
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
    if "processFull" in processFunc or "processBarrel" in processFunc:
      print("common barrel tables==========")      
      for table in barrelCommonTables:
        print(table)      
        tablesToProduce[table] = 1
      if runOverMC == True:
        tablesToProduce["ReducedTracksBarrelLabels"] = 1
    if "processFull" in processFunc or "processMuon" in processFunc:
      print("common muon tables==========")      
      for table in muonCommonTables:
        print(table)
        tablesToProduce[table] = 1
      if runOverMC == True:
        tablesToProduce["ReducedMuonsLabels"] = 1  
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
  json.dump(writerConfig, writerConfigFile)  
  
print(writerConfig)
#sys.exit()
      
commandToRun = taskNameInCommandLine + " --configuration json://" + updatedConfigFileName + " --severity error --shm-segment-size 12000000000 --aod-writer-json " + writerConfigFileName + " -b"
for dep in depsToRun.keys():
  commandToRun += " | " + dep + " --configuration json://" + updatedConfigFileName + " -b"

if sys.argv[2] == "runMCwithConverter" :
  commandToRun += " | o2-analysis-mc-converter --configuration json://" + updatedConfigFileName + " -b" 

if sys.argv[2] == "runMCwithFddConverter" :
  commandToRun += " | o2-analysis-fdd-converter --configuration json://" + updatedConfigFileName + " -b"

print("====================================================================================================================")
print("Command to run:")
print(commandToRun)
print("====================================================================================================================")
print("Tables to produce:")
print(tablesToProduce.keys())
print("====================================================================================================================")
#sys.exit()

os.system(commandToRun)
