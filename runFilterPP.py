#!/usr/bin/env python3

import sys
import json
import os

commonDeps = ["o2-analysis-timestamp", "o2-analysis-fdd-converter",  "o2-analysis-event-selection", "o2-analysis-multiplicity-table", "o2-analysis-trackselection", "o2-analysis-trackextension", "o2-analysis-pid-tof", "o2-analysis-pid-tof-full", "o2-analysis-pid-tof-beta", "o2-analysis-pid-tpc-full"]

# Make some checks on provided arguments
if len(sys.argv) < 3:
  print("ERROR: Invalid syntax! The command line should look like this:")
  print("  ./runTableMaker.py <yourConfig.json> <runData|runMC> [task|param|value] ...")
  sys.exit()

# Load the configuration file provided as the first parameter
config = {}
with open(sys.argv[1]) as configFile:
  config = json.load(configFile)

# Check whether we run over data or MC
if not ((sys.argv[2] == "runMC") or (sys.argv[2] == "runData")):
  print("ERROR: You have to specify either runMC or runData !")
  sys.exit()

runOverMC = False
if sys.argv[2] == "runMC":
  runOverMC = True

# Get all the user required modifications to the configuration file
for count in range(3, len(sys.argv)):
  param = sys.argv[count].split(":")
  if len(param) != 3:
    print("ERROR: Wrong parameter syntax: ", param)
    sys.exit()
  config[param[0]][param[1]] = param[2]


taskNameInConfig = "d-q-filter-p-p-task"
taskNameInCommandLine = "o2-analysis-dq-filter-pp"
if runOverMC == True:
  taskNameInConfig = "d-q-filter-p-p-task"
  taskNameInCommandLine = "o2-analysis-dq-filter-pp"

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
      
commandToRun = taskNameInCommandLine + " --configuration json://" + updatedConfigFileName + " --severity error --shm-segment-size 12000000000 -b"
for dep in depsToRun.keys():
  commandToRun += " | " + dep + " --configuration json://" + updatedConfigFileName + " -b"

print("====================================================================================================================")
print("Command to run:")
print(commandToRun)
print("====================================================================================================================")
os.system(commandToRun)
