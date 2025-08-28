## SR versus CR plots for TTBar and DY background
python3 diffKinem_CRvsSR_rooFit_plot.py data/inputfiles/WRAnalyzer_DYJets.root data/jsons/hists_mumu.json
python3 diffKinem_CRvsSR_rooFit_plot.py data/inputfiles/WRAnalyzer_DYJets.root data/jsons/hists.json ## for ee channel

python3 diffKinem_CRvsSR_rooFit_plot.py data/inputfiles/WRAnalyzer_TTbar.root data/jsons/hists_ttbar.json
python3 diffKinem_CRvsSR_rooFit_plot.py data/inputfiles/WRAnalyzer_TTbar.root data/jsons/hists_mumu_ttbar.json


## overlay for signal
python3 v1_signal_diffkinem.py data/inputfiles/WRAnalyzer_signal_WR2000_N400.root data/inputfiles/WRAnalyzer_signal_WR2000_N800.root  data/inputfiles/WRAnalyzer_signal_WR2000_N1900.root data/jsons/hists_signal.json

python3 v1_signal_diffkinem.py data/inputfiles/WRAnalyzer_signal_WR2000_N800.root data/inputfiles/WRAnalyzer_signal_WR3200_N800.root  data/inputfiles/WRAnalyzer_signal_WR1200_N800.root data/jsons/hists_signal.json


python3 rooFit_plot_Wrmass_BW.py data/inputfiles/WRAnalyzer_signal_WR3200_N800.root
