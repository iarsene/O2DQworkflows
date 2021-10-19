import sys
import json
import os

commonDeps = ["o2-analysis-timestamp", "o2-analysis-event-selection", "o2-analysis-multiplicity-table"]
barrelDeps = ["o2-analysis-trackselection", "o2-analysis-trackextension", "o2-analysis-pid-tof", "o2-analysis-pid-tof-full", "o2-analysis-pid-tof-beta", "o2-analysis-pid-tpc-full"]
specificDeps = {
  "processFull" : [],
  "processFullWithCent" : ["o2-analysis-centrality-table"],
  "processFullWithV0Bits" : ["o2-analysis-dq-v0-selector", "o2-analysis-weak-decay-indices"],
  "processFullWithEventFilter" : ["o2-analysis-dq-filter-pp"],
  "processFullWithCentWithV0Bits" : ["o2-analysis-centrality-table","o2-analysis-dq-v0-selector", "o2-analysis-weak-decay-indices"],
  "processFullWithEventFilterWithV0Bits" : ["o2-analysis-dq-filter-pp","o2-analysis-dq-v0-selector", "o2-analysis-weak-decay-indices"],
  "processBarrelOnly" : [],
  "processBarrelOnlyWithCent" : ["o2-analysis-centrality-table"],
  "processMuonOnly" : [],
  "processMuonOnlyWithCent" : ["o2-analysis-centrality-table"],
  "processMuonOnlyWithFilter" : ["o2-analysis-dq-filter-pp"]
}        

config = {}
with open(sys.argv[1]) as configFile:
  config = json.load(configFile)

for count in range(2, len(sys.argv)):
  param = sys.argv[count].split(":")
  if len(param) != 3:
    print("ERROR: Wrong parameter syntax: ", param)
    sys.exit()
  config[param[0]][param[1]] = param[2]

with open('config.json','w') as outputFile:
  json.dump(config, outputFile)
  
depsToRun = {}
for dep in commonDeps:
  depsToRun[dep] = 1

for processFunc in specificDeps.keys():
  if config["table-maker"][processFunc] == "true":      
    if "processFull" in processFunc or "processBarrel" in processFunc:
      for dep in barrelDeps:
        depsToRun[dep] = 1
    if config["table-maker"][processFunc] == "true":
      for dep in specificDeps[processFunc]:
        depsToRun[dep] = 1
      
commandToRun = "o2-analysis-dq-table-maker --configuration json://config.json --severity error --shm-segment-size 12000000000 -b"
for dep in depsToRun.keys():
  commandToRun += " | " + dep + " --configuration json://config.json -b"

print("====================================================================================================================")
print("Command to run:")
print(commandToRun)
print("====================================================================================================================")
os.system(commandToRun)
