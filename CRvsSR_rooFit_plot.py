### To fit the mass distributions with Gauss and BW functions, run
### python3 rooFit_plot_Wrmass_BW.py WRAnalyzer_signal_WR3200_N1200.root
### To overlay CR & SR - run 
import ROOT
import sys, re

# Comment out next line if you want interactive canvas pop-ups
ROOT.gROOT.SetBatch(True)  
ROOT.gStyle.SetOptStat(0)

def iterative_gaussian_fit(h, mass_str, bin_width):
    x = ROOT.RooRealVar("x", "m_{eejj} [GeV]", h.GetXaxis().GetXmin(), h.GetXaxis().GetXmax())
    dh = ROOT.RooDataHist("dh_gauss", "dh_gauss", ROOT.RooArgList(x), h)

    mean = ROOT.RooRealVar("mean", "mean", h.GetMean(), h.GetXaxis().GetXmin(), h.GetXaxis().GetXmax())
    sigma = ROOT.RooRealVar("sigma", "sigma", h.GetRMS(), 10., 1000.)
    gauss = ROOT.RooGaussian("gauss", "Gaussian PDF", x, mean, sigma)

    # Iterative narrowing
    for _ in range(3):
        gauss.fitTo(dh, ROOT.RooFit.Save(), ROOT.RooFit.PrintLevel(-1))
        mval, sval = mean.getVal(), sigma.getVal()
        low, high = max(h.GetXaxis().GetXmin(), mval - 1.5*sval), min(h.GetXaxis().GetXmax(), mval + 1.5*sval)
        x.setRange("narrow", low, high)

    gauss.fitTo(dh, ROOT.RooFit.Save(), ROOT.RooFit.Range("narrow"), ROOT.RooFit.PrintLevel(-1))

    # Plot
    c = ROOT.TCanvas("c_gauss", "", 800, 600)
    frame = x.frame()
    dh.plotOn(frame)
    gauss.plotOn(frame, ROOT.RooFit.LineColor(ROOT.kBlue))
    frame.GetYaxis().SetTitle("Event yield / bin")
    frame.SetTitle("")
    frame.Draw()

    leg = ROOT.TLegend(0.55, 0.65, 0.85, 0.85)
    leg.SetTextSize(0.04)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)
    leg.AddEntry(0, f"M_WR = {mass_str} GeV", "")
    leg.AddEntry(0, f"#sigma = {sigma.getVal():.1f} GeV", "")
    leg.Draw()

    outname = f"wr_mass_gauss_WR{mass_str}.png"
    c.SetTitle("")
    c.SaveAs(outname)

    print(f"â Saved {outname}")
    print(f"   Gaussian mean = {mean.getVal():.1f}, Ï = {sigma.getVal():.1f} (bin width {bin_width:.1f} GeV)")

    return mean.getVal(), sigma.getVal()


def iterative_breitwigner_fit(h, mass_str, bin_width):
    x = ROOT.RooRealVar("x", "m_{eejj} [GeV]", h.GetXaxis().GetXmin(), h.GetXaxis().GetXmax())
    dh = ROOT.RooDataHist("dh_bw", "dh_bw", ROOT.RooArgList(x), h)

    mean = ROOT.RooRealVar("mean", "mean", h.GetMean(), h.GetXaxis().GetXmin(), h.GetXaxis().GetXmax())
    width = ROOT.RooRealVar("width", "width", h.GetRMS(), 10., 1000.)
    bw = ROOT.RooBreitWigner("bw", "Breit-Wigner PDF", x, mean, width)

    # Iterative narrowing
    for _ in range(3):
        bw.fitTo(dh, ROOT.RooFit.Save(), ROOT.RooFit.PrintLevel(-1))
        mval, wval = mean.getVal(), width.getVal()
        low, high = max(h.GetXaxis().GetXmin(), mval - 2*wval), min(h.GetXaxis().GetXmax(), mval + 2*wval)
        x.setRange("narrow", low, high)

    bw.fitTo(dh, ROOT.RooFit.Save(), ROOT.RooFit.Range("narrow"), ROOT.RooFit.PrintLevel(-1))

    # Plot
    c = ROOT.TCanvas("c_bw", "", 800, 600)
    frame = x.frame()
    dh.plotOn(frame)
    bw.plotOn(frame, ROOT.RooFit.LineColor(ROOT.kRed), ROOT.RooFit.LineStyle(2))
    frame.GetYaxis().SetTitle("Event yield / bin")
    frame.SetTitle("")
    frame.Draw()

    leg = ROOT.TLegend(0.55, 0.65, 0.85, 0.85)
    leg.SetTextSize(0.04)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)
    leg.AddEntry(0, f"M_WR = {mass_str} GeV", "")
    leg.AddEntry(0, f"#Gamma/2 = {width.getVal()/2:.1f} GeV", "")
    leg.Draw()

    outname = f"wr_mass_bw_WR{mass_str}.png"
    c.SaveAs(outname)

    print(f"â Saved {outname}")
    print(f"   Breit-Wigner mean = {mean.getVal():.1f}, Î = {width.getVal():.1f} (bin width {bin_width:.1f} GeV)")

    return mean.getVal(), width.getVal()


def fit_and_plot(filename, histname="mass_fourobject_wr_ee_resolved_sr", histname1="mass_fourobject_wr_ee_resolved_dy_cr", hdir_cr_str="wr_ee_resolved_dy_cr", op_str="DyJets"):
    # Extract WR mass from filename
    match = re.search(r"_WR(\d+)_", filename)
    mass_str = match.group(1) if match else "Unknown"

    # Open ROOT file
    f = ROOT.TFile.Open(filename)
    f_signal = ROOT.TFile.Open("WRAnalyzer_signal_WR2400_N800.root") ## Extract signal distribution -comment it out if you don't want to plot an overlay of signal and bkg in SR 
    hdir1 = f_signal.Get("wr_ee_resolved_sr")
    h_signal = hdir1.Get("mass_fourobject_wr_ee_resolved_sr")
    
    hdir = f.Get("wr_ee_resolved_sr")
    h_sr = hdir.Get(histname)
    hdir_cr = f.Get(hdir_cr_str) #"wr_ee_resolved_dy_cr")
    #hdir_cr.cd()
    h_cr = hdir_cr.Get(histname1) 
    if not h_sr:
        raise RuntimeError(f"Histograms {histname} and {histname1} not found in {filename}")

    # Rebin histogram to ~100 GeV
    bin_width = h_sr.GetBinWidth(1)
    rebin_factor = max(1, int(100/bin_width))
    h_sr.Rebin(rebin_factor)
    h_cr.Rebin(rebin_factor)
    h_signal.Rebin(rebin_factor)
    bin_width = h_cr.GetBinWidth(1)

    # print(f"\nð File: {filename}")
    # print(f"   â Using histogram {histname}, WR mass {mass_str}")
    # print(f"   â Rebinning factor {rebin_factor}, new bin width {bin_width:.1f} GeV")
    #    if(normalized):
    # h_cr.Scale(1.0/h_cr.Integral())
    # h_sr.Scale(1.0/h_sr.Integral())
    # h_signal.Scale(1.0/h_signal.Integral())
    # x = ROOT.RooRealVar("x", "m_{eejj} [GeV]", h_sr.GetXaxis().GetXmin(), h_sr.GetXaxis().GetXmax())
    # dh = ROOT.RooDataHist("dh_bw", "dh_bw", ROOT.RooArgList(x), h_sr)
    # x_cr = ROOT.RooRealVar("x_cr", "m_{eejj} [GeV]", h_cr.GetXaxis().GetXmin(), h_cr.GetXaxis().GetXmax())
    # dh_cr = ROOT.RooDataHist("dh_bw_cr", "dh_bw", ROOT.RooArgList(x), h_cr)
    c = ROOT.TCanvas("c_bw", "", 800, 600)
    # frame = x.frame()
    # dh.plotOn(frame)
    # dh_cr.plotOn(frame,ROOT.RooFit.LineColor(ROOT.kRed), ROOT.RooFit.LineStyle(2))
    # frame.GetYaxis().SetTitle("Normalized")
    # frame.SetTitle("")
    # frame.Draw()
    ROOT.gPad.SetLogy()
    h_sr.SetLineColor(ROOT.kRed)
    h_cr.SetLineColor(ROOT.kBlue)
    h_sr.SetMarkerSize(1.2)
    h_cr.SetMarkerSize(1.2)
    h_sr.SetMarkerStyle(8)
    h_cr.SetMarkerStyle(8)
    h_sr.SetMarkerColor(ROOT.kRed)
    h_cr.SetMarkerColor(ROOT.kBlue)
    h_signal.SetLineColor(ROOT.kViolet)
    h_signal.SetMarkerSize(1.2)
    h_signal.SetMarkerStyle(8)
    h_signal.SetMarkerColor(ROOT.kViolet)
    
    h_cr.GetYaxis().SetRangeUser(0.00000001,1)
    h_sr.GetYaxis().SetRangeUser(0.00000001,1)
    h_signal.GetYaxis().SetRangeUser(0.00000001,1)
    h_sr.Draw("ep")
    h_cr.Draw("ep same")
    h_signal.Draw("ep same")
    leg = ROOT.TLegend(0.55, 0.65, 0.85, 0.85)
    leg.SetTextSize(0.04)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)
    
    leg.SetHeader(op_str)
    leg.AddEntry(h_sr, "SR","ep") #f"M_WR = {mass_str} GeV", "")
    leg.AddEntry(h_cr, "CR","ep") #f"#Gamma/2 = {width.getVal()/2:.1f} GeV", "")
    leg.AddEntry(h_signal,"WR (2TeV)","ep")
    leg.Draw()
    
    outname = f"SRvsCR_{op_str}_norm.png"
    c.SaveAs(outname)
    
    # Do both fits
    # g_mean, g_sigma = iterative_gaussian_fit(h, mass_str, bin_width)
    # bw_mean, bw_width = iterative_breitwigner_fit(h, mass_str, bin_width)
    
    # print(f"--- Comparison for WR{mass_str} ---")
    # print(f"   Gaussian Ï = {g_sigma:.1f}, Breit-Wigner Î = {bw_width:.1f}")
    # print("---------------------------------\n")

    return 0#(g_mean, g_sigma, bw_mean, bw_width)


def main(files):
    i=-1
    for filename in files:
        i+=1
        if(i==0):
            fit_and_plot(filename)
        if(i==1):
            fit_and_plot(filename,histname="mass_fourobject_wr_ee_resolved_sr", histname1="mass_fourobject_wr_resolved_flavor_cr",hdir_cr_str="wr_resolved_flavor_cr", op_str="TTbar")
            
            
if __name__ == "__main__":
    main(sys.argv[1:])

