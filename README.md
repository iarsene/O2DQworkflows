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

# Instructions
Add extrac tables and converters with:
1. **--add_mc_conv**: conversion from o2mcparticle to o2mcparticle_001
2. **--add_fdd_conv**: conversion o2fdd from o2fdd_001
3. **--add_track_prop**: conversion from o2track to o2track_iu ([link](https://aliceo2group.github.io/analysis-framework/docs/helperTasks/trackPropagation.html))

Examples:
- Run TableMaker on Data
  ```ruby
  python runTableMaker.py configTableMakerDataRun3.json -runData table-maker:processMuonOnlyWithCov:true --add_track_prop
  ```
- Run TableMaker on MC
  ```ruby
  python runTableMaker.py configTableMakerMCRun3.json -runMC table-maker-m-c:processMuonOnlyWithCov:true --add_track_prop
  ```

In case of multiple text commands, separate them with comma:
```ruby
python runTableMaker.py configTableMakerDataRun3.json -runData internal-dpl-aod-reader:aod-file:AO2D.root,table-maker:processMuonOnly:true --add_track_prop
```
