## SR versus CR plots for TTBar and DY background
python3 diffKinem_CRvsSR_rooFit_plot.py WRAnalyzer_DYJets.root hists_mumu.json
python3 diffKinem_CRvsSR_rooFit_plot.py WRAnalyzer_DYJets.root hists.json ## for ee channel

python3 diffKinem_CRvsSR_rooFit_plot.py WRAnalyzer_TTbar.root hists_ttbar.json
python3 diffKinem_CRvsSR_rooFit_plot.py WRAnalyzer_TTbar.root hists_mumu_ttbar.json


## overlay for signal
python3 v1_signal_diffkinem.py WRAnalyzer_signal_WR2000_N400.root WRAnalyzer_signal_WR2000_N1000.root  WRAnalyzer_signal_WR2000_N1900.root hists_signal.json

python3 v1_signal_diffkinem.py WRAnalyzer_signal_WR2000_N1000.root WRAnalyzer_signal_WR3200_N800.root  WRAnalyzer_signal_WR2800_N600.root hists_signal.json
