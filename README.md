# O2DQworkflows
Contains O2/DQ workflow json configuration files and python scripts to run them

Contents:
1) Scripts:
1.1) runTableMaker.py - script used to run both the skimming tasks (tableMaker.cxx and tableMakerMC.cxx)

2) Workflow configuration files
2.1) configTableMakerDataRun2.json - run over Run-2 converted data
2.2) configTableMakerDataRun3.json - run over Run-3 data
2.3) configTableMakerMCRun2.json - run over Run-2 converted MC
2.4) configTableMakerMCRun3.json - run over Run-3 MC
2.5) configAnalysisData.json - run with tableReader.cxx
2.6) configAnalysisMC.json - run with dqEfficiency.cxx

3) Reader configurations for the DQ skimmed tables
3.1) readerConfiguration_reducedEvent.json - for data
3.1) readerConfiguration_reducedEventMC.json - for MC
