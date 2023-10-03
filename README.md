# O2DQworkflows
Contains O2/DQ workflow json configuration files and python scripts to run them

Contents:
1) Scripts:
1.1) runTableMaker.py - script used to run both the skimming tasks (tableMaker.cxx and tableMakerMC.cxx)
1.2) runAnalysis.py - script used to run both the analyzing tasks (tableReader.cxx and dqEfficiency.cxx)
1.3) runFilterPP.py - script used to run filterPP.cxx

2) Workflow configuration files
2.1) configTableMakerDataRun2.json - run over Run-2 converted data with tableMaker.cxx
2.2) configTableMakerDataRun3.json - run over Run-3 data with tableMaker.cxx
2.3) configTableMakerMCRun2.json - run over Run-2 converted MC with tableMakerMC.cxx
2.4) configTableMakerMCRun3.json - run over Run-3 MC with tableMakerMC.cxx
2.5) configAnalysisData.json - run with tableReader.cxx
2.6) configAnalysisMC.json - run with dqEfficiency.cxx
2.7) configFilterPPDataRun2.json - run over Run-2 converted data with filterPP.cxx
2.8) configFilterPPDataRun3.json - run over Run-3 data with filterPP.cxx

3) Reader configurations for the DQ skimmed tables
3.1) readerConfiguration_reducedEvent.json - for data
3.2) readerConfiguration_reducedEventMC.json - for MC
3.3) readerConfiguration_dileptons.json - read dilepton tables for data
3.4) readerConfiguration_dileptonMC.json - read dilepton tables for MC

4) Writer configurations for the DQ skimmed tables (dileptons)
4.1) writerConfiguration_dileptons.json - extract to extra dilepton tables for data
4.2) writerConfiguration_dileptonMC.json - extract to extra dilepton tables for MC

# Instructions
Add extrac tables and converters with:
1. **--add_mc_conv**: conversion from o2mcparticle to o2mcparticle_001
2. **--add_fdd_conv**: conversion o2fdd from o2fdd_001
3. **--add_track_prop**: conversion from o2track to o2track_iu ([link](https://aliceo2group.github.io/analysis-framework/docs/helperTasks/trackPropagation.html))
4. **--add_weakdecay_ind**: Converts V0 and cascade version 000 to 001 
5. **--add_zdc_conv**: Converts ZDC version 000 to 001 
6. **--add_bc_conv**: Converts BC version 000 to 001 

Examples:
- Run TableMaker on Data
  ```ruby
  python runTableMaker.py configTableMakerDataRun3.json -runData --arg table-maker:processMuonOnlyWithCov:true --add_track_prop
  ```
- Run TableMaker on MC
  ```ruby
  python runTableMaker.py configTableMakerMCRun3.json -runMC --arg table-maker-m-c:processMuonOnlyWithCov:true --add_track_prop
  ```

In case of multiple text commands, separate them with comma:
```ruby
python runTableMaker.py configTableMakerDataRun3.json -runData --arg internal-dpl-aod-reader:aod-file:AO2D.root,table-maker:processMuonOnly:true --add_track_prop
```

- Run tableReader on Skimmed Data
  ```ruby
  python runAnalysis.py configAnalysisData.json -runData --arg analysis-same-event-pairing:processDecayToEESkimmed:true
  ```
- Run dqEfficiency on Skimmed MC
  ```ruby
  python runAnalysis.py configAnalysisMC.json -runMC --arg analysis-same-event-pairing:processDecayToEESkimmed:true
  ```

In case of multiple text commands, separate them with comma:
```ruby
python runAnalysis.py configAnalysisData.json -runData --arg internal-dpl-aod-reader:aod-file:reducedAod.root,analysis-same-event-pairing:processDecayToEESkimmed:true
```

Produce dilepton tables with --aod-writer-json (example for MC):
```ruby
python runAnalysis.py configAnalysisMC.json -runMC --aod-writer-json writerConfiguration_dileptonMC.json --arg internal-dpl-aod-reader:aod-file:reducedAod.root,analysis-same-event-pairing:processDecayToMuMuVertexingSkimmed:true
```

For read dilepton tables, change --aod-reader-json and give aod path of dileptonAod.root (example for dilepton track, dimuon-muon analysis):
```ruby
python runAnalysis.py configAnalysisMC.json -runMC --arg internal-dpl-aod-reader:aod-file:dileptonAod.root,analysis-dilepton-track:processDimuonMuonSkimmed:true,analysis-dilepton-track:processDummy:false
```

- Run FilterPP on Data:
  ```ruby
  python runFilterPP.py configFilterPPDataRun3.json
  ```