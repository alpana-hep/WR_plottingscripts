# WR_plottingscripts
Scripts to plot different variables in respect to WR analysis


1. Overlay of ee CR and SR in DY and TTbar
```
python3 diffKinem_CRvsSR_rooFit_plot.py data/inputfiles/WRAnalyzer_DYJets.root data/jsons/hists.json
```
OR
```
python3 diffKinem_CRvsSR_rooFit_plot.py data/inputfiles/WRAnalyzer_TTbar.root data/jsons/hists_ttbar.json
```

2. Overlay of mumu CR and SR in DY and TTbar
```
python3 diffKinem_CRvsSR_rooFit_plot.py data/inputfiles/WRAnalyzer_DYJets.root data/jsons/hists.json   
```

```
python3 diffKinem_CRvsSR_rooFit_plot.py data/inputfiles/WRAnalyzer_TTbar.root data/jsons/hists_mumu_ttbar.json
```

3. Overlay of different kinematics for different Wr masses and Nl masses
```
python3 v1_signal_diffkinem.py data/inputfiles/WRAnalyzer_signal_WR2000_N400.root data/inputfiles/WRAnalyzer_signal_WR2000_N800.root  data/inputfiles/WRAnalyzer_signal_WR2000_N1900.root data/jsons/hists_signal.json

```
Different Nl
```
python3 v1_signal_diffkinem.py data/inputfiles/WRAnalyzer_signal_WR2000_N800.root data/inputfiles/WRAnalyzer_signal_WR3200_N800.root  data/inputfiles/WRAnalyzer_signal_WR1200_N800.root data/jsons/hists_signal.json

```
4. Invariant mlljj - fit it using Gaussian
```
python3 rooFit_plot_Wrmass_BW.py WRAnalyzer_signal_WR3200_N1200.root
```

5. Or run all of it together
```
source runme.sh
```