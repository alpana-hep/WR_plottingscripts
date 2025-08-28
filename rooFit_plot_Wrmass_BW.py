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


def fit_and_plot(filename, histname="mass_fourobject_wr_ee_resolved_sr"):
    # Extract WR mass from filename
    match = re.search(r"_WR(\d+)_", filename)
    mass_str = match.group(1) if match else "Unknown"

    # Open ROOT file
    f = ROOT.TFile.Open(filename)
    hdir = f.Get("wr_ee_resolved_sr")
    h = hdir.Get(histname)
    if not h:
        raise RuntimeError(f"Histogram {histname} not found in {filename}")

    # Rebin histogram to ~100 GeV
    bin_width = h.GetBinWidth(1)
    rebin_factor = max(1, int(100/bin_width))
    h.Rebin(rebin_factor)
    bin_width = h.GetBinWidth(1)

    print(f"\nð File: {filename}")
    print(f"   â Using histogram {histname}, WR mass {mass_str}")
    print(f"   â Rebinning factor {rebin_factor}, new bin width {bin_width:.1f} GeV")

    # Do both fits
    g_mean, g_sigma = iterative_gaussian_fit(h, mass_str, bin_width)
    bw_mean, bw_width = iterative_breitwigner_fit(h, mass_str, bin_width)

    print(f"--- Comparison for WR{mass_str} ---")
    print(f"   Gaussian Ï = {g_sigma:.1f}, Breit-Wigner Î = {bw_width:.1f}")
    print("---------------------------------\n")

    return (g_mean, g_sigma, bw_mean, bw_width)


def main(files):
    for filename in files:
        fit_and_plot(filename)


if __name__ == "__main__":
    main(sys.argv[1:])


# import ROOT, sys, re

# # Run in batch mode (no interactive GUI)
# ROOT.gROOT.SetBatch(True)
# ROOT.gStyle.SetOptStat(0)

# def fit_and_overlay(filename, histname="mass_fourobject_wr_ee_resolved_sr"):
#     # Extract WR mass from filename
#     match = re.search(r"_WR(\d+)_", filename)
#     mass_str = match.group(1) if match else "Unknown"

#     f = ROOT.TFile.Open(filename)
#     hdir = f.Get("wr_ee_resolved_sr")
#     h = hdir.Get(histname)
#     if not h:
#         raise RuntimeError(f"Histogram {histname} not found in {filename}")

#     # Rebin to ~100 GeV
#     bin_width = h.GetBinWidth(1)
#     rebin_factor = max(1, int(100/bin_width))
#     h.Rebin(rebin_factor)
#     bin_width = h.GetBinWidth(1)

#     print(f"\nð File: {filename}, WR mass {mass_str}, new bin width {bin_width:.1f} GeV")

#     # RooFit variable and histogram
#     x = ROOT.RooRealVar("x", "m_{eejj} [GeV]", h.GetXaxis().GetXmin(), h.GetXaxis().GetXmax())
#     dh = ROOT.RooDataHist("dh", "dh", ROOT.RooArgList(x), h)

#     # --- Gaussian ---
#     mean_g = ROOT.RooRealVar("mean_g", "mean", h.GetMean(), h.GetXaxis().GetXmin(), h.GetXaxis().GetXmax())
#     sigma_g = ROOT.RooRealVar("sigma_g", "sigma", h.GetRMS(), 10., 1000.)
#     gauss = ROOT.RooGaussian("gauss", "Gaussian PDF", x, mean_g, sigma_g)

#     # Iterative Â±2Ï fit
#     for _ in range(3):
#         res_g = gauss.fitTo(dh, ROOT.RooFit.Save(), ROOT.RooFit.PrintLevel(-1))
#         mval, sval = mean_g.getVal(), sigma_g.getVal()
#         low, high = max(h.GetXaxis().GetXmin(), mval - 2*sval), min(h.GetXaxis().GetXmax(), mval + 2*sval)
#         x.setRange("gaussRange", low, high)

#     res_g = gauss.fitTo(dh, ROOT.RooFit.Save(), ROOT.RooFit.Range("gaussRange"), ROOT.RooFit.PrintLevel(-1))
#     mean_g_val, sigma_g_val = mean_g.getVal(), sigma_g.getVal()
#     mean_g_err, sigma_g_err = mean_g.getError(), sigma_g.getError()

#     # --- Breit-Wigner ---
#     mean_bw = ROOT.RooRealVar("mean_bw", "mean", h.GetMean(), h.GetXaxis().GetXmin(), h.GetXaxis().GetXmax())
#     width_bw = ROOT.RooRealVar("width_bw", "width", h.GetRMS(), 10., 1000.)
#     bw = ROOT.RooBreitWigner("bw", "Breit-Wigner PDF", x, mean_bw, width_bw)

#     for _ in range(3):
#         res_bw = bw.fitTo(dh, ROOT.RooFit.Save(), ROOT.RooFit.PrintLevel(-1))
#         mval, wval = mean_bw.getVal(), width_bw.getVal()
#         low, high = max(h.GetXaxis().GetXmin(), mval - 2*wval), min(h.GetXaxis().GetXmax(), mval + 2*wval)
#         x.setRange("bwRange", low, high)

#     res_bw = bw.fitTo(dh, ROOT.RooFit.Save(), ROOT.RooFit.Range("bwRange"), ROOT.RooFit.PrintLevel(-1))
#     mean_bw_val, width_bw_val = mean_bw.getVal(), width_bw.getVal()
#     mean_bw_err, width_bw_err = mean_bw.getError(), width_bw.getError()

#     # --- Plot ---
#     c = ROOT.TCanvas(f"c_{mass_str}", "", 800, 600)
#     frame = x.frame()
#     dh.plotOn(frame)
#     gauss.plotOn(frame, ROOT.RooFit.LineColor(ROOT.kBlue))
#     bw.plotOn(frame, ROOT.RooFit.LineColor(ROOT.kRed), ROOT.RooFit.LineStyle(2))
#     frame.GetYaxis().SetTitle("Event yield / bin")
#     frame.Draw()

#     # ÏÂ²/ndf
#     chi2_gauss = frame.chiSquare("gauss")
#     chi2_bw = frame.chiSquare("bw")

#     # Legend
#     leg = ROOT.TLegend(0.55, 0.55, 0.85, 0.85)
#     leg.SetTextSize(0.035)
#     leg.SetBorderSize(0)
#     leg.SetFillStyle(0)
#     leg.AddEntry(0, f"WR mass {mass_str} GeV", "")
#     leg.AddEntry(gauss, f"Gaussian: Î¼={mean_g_val:.1f}Â±{mean_g_err:.1f}, Ï={sigma_g_val:.1f}Â±{sigma_g_err:.1f}, ÏÂ²/ndf={chi2_gauss:.2f}", "l")
#     leg.AddEntry(bw, f"BW: Î¼={mean_bw_val:.1f}Â±{mean_bw_err:.1f}, Î={width_bw_val:.1f}Â±{width_bw_err:.1f}, ÏÂ²/ndf={chi2_bw:.2f}", "l")
#     leg.Draw()

#     outname = f"wr_mass_overlay_WR{mass_str}.png"
#     c.SaveAs(outname)
#     print(f"â Overlay plot saved: {outname}")

#     return {
#         "gauss": (mean_g_val, mean_g_err, sigma_g_val, sigma_g_err, chi2_gauss),
#         "bw": (mean_bw_val, mean_bw_err, width_bw_val, width_bw_err, chi2_bw)
#     }


# def main(files):
#     for filename in files:
#         fit_and_overlay(filename)


# if __name__ == "__main__":
#     main(sys.argv[1:])


# import ROOT
# import sys, re

# # Comment this out if you want interactive canvas
# ROOT.gROOT.SetBatch(True)
# ROOT.gStyle.SetOptStat(0)

# def iterative_gaussian_fit(h, mass_str, bin_width):
#     x = ROOT.RooRealVar("x", "m_{eejj} [GeV]", h.GetXaxis().GetXmin(), h.GetXaxis().GetXmax())
#     dh = ROOT.RooDataHist("dh_gauss", "dh_gauss", ROOT.RooArgList(x), h)

#     mean = ROOT.RooRealVar("mean", "mean", h.GetMean(), h.GetXaxis().GetXmin(), h.GetXaxis().GetXmax())
#     sigma = ROOT.RooRealVar("sigma", "sigma", h.GetRMS(), 10., 1000.)
#     gauss = ROOT.RooGaussian("gauss", "Gaussian PDF", x, mean, sigma)

#     # Iterative narrowing
#     for _ in range(3):
#         res = gauss.fitTo(dh, ROOT.RooFit.Save(), ROOT.RooFit.PrintLevel(-1))
#         mval, sval = mean.getVal(), sigma.getVal()
#         low, high = max(h.GetXaxis().GetXmin(), mval - 2*sval), min(h.GetXaxis().GetXmax(), mval + 2*sval)
#         x.setRange("narrow", low, high)

#     res = gauss.fitTo(dh, ROOT.RooFit.Save(), ROOT.RooFit.Range("narrow"), ROOT.RooFit.PrintLevel(-1))

#     # Extract uncertainties
#     mean_err = mean.getError()
#     sigma_err = sigma.getError()

#     # Plot
#     c = ROOT.TCanvas(f"c_gauss_{mass_str}", "", 800, 600)
#     frame = x.frame()
#     dh.plotOn(frame)
#     gauss.plotOn(frame, ROOT.RooFit.LineColor(ROOT.kBlue))
#     frame.GetYaxis().SetTitle("Event yield / bin")
#     frame.Draw()

#     leg = ROOT.TLegend(0.55, 0.65, 0.85, 0.85)
#     leg.SetTextSize(0.04)
#     leg.SetBorderSize(0)
#     leg.SetFillStyle(0)
#     leg.AddEntry(0, f"WR mass {mass_str} GeV", "")
#     leg.AddEntry(0, f"Ï = {sigma.getVal():.1f} Â± {sigma_err:.1f} GeV", "")
#     leg.Draw()

#     outname = f"wr_mass_gauss_WR{mass_str}.png"
#     c.SaveAs(outname)

#     print(f"â Gaussian fit saved: {outname}")
#     print(f"   mean = {mean.getVal():.1f} Â± {mean_err:.1f} GeV, Ï = {sigma.getVal():.1f} Â± {sigma_err:.1f} GeV, bin width = {bin_width:.1f} GeV")

#     return mean.getVal(), mean_err, sigma.getVal(), sigma_err


# def iterative_breitwigner_fit(h, mass_str, bin_width):
#     x = ROOT.RooRealVar("x", "m_{eejj} [GeV]", h.GetXaxis().GetXmin(), h.GetXaxis().GetXmax())
#     dh = ROOT.RooDataHist("dh_bw", "dh_bw", ROOT.RooArgList(x), h)

#     mean = ROOT.RooRealVar("mean", "mean", h.GetMean(), h.GetXaxis().GetXmin(), h.GetXaxis().GetXmax())
#     width = ROOT.RooRealVar("width", "width", h.GetRMS(), 10., 1000.)
#     bw = ROOT.RooBreitWigner("bw", "Breit-Wigner PDF", x, mean, width)

#     # Iterative narrowing
#     for _ in range(3):
#         res = bw.fitTo(dh, ROOT.RooFit.Save(), ROOT.RooFit.PrintLevel(-1))
#         mval, wval = mean.getVal(), width.getVal()
#         low, high = max(h.GetXaxis().GetXmin(), mval - 2*wval), min(h.GetXaxis().GetXmax(), mval + 2*wval)
#         x.setRange("narrow", low, high)

#     res = bw.fitTo(dh, ROOT.RooFit.Save(), ROOT.RooFit.Range("narrow"), ROOT.RooFit.PrintLevel(-1))

#     # Extract uncertainties
#     mean_err = mean.getError()
#     width_err = width.getError()

#     # Plot
#     c = ROOT.TCanvas(f"c_bw_{mass_str}", "", 800, 600)
#     frame = x.frame()
#     dh.plotOn(frame)
#     bw.plotOn(frame, ROOT.RooFit.LineColor(ROOT.kRed), ROOT.RooFit.LineStyle(2))
#     frame.GetYaxis().SetTitle("Event yield / bin")
#     frame.Draw()

#     leg = ROOT.TLegend(0.55, 0.65, 0.85, 0.85)
#     leg.SetTextSize(0.04)
#     leg.SetBorderSize(0)
#     leg.SetFillStyle(0)
#     leg.AddEntry(0, f"WR mass {mass_str} GeV", "")
#     leg.AddEntry(0, f"Î = {width.getVal():.1f} Â± {width_err:.1f} GeV", "")
#     leg.Draw()

#     outname = f"wr_mass_bw_WR{mass_str}.png"
#     c.SaveAs(outname)

#     print(f"â Breit-Wigner fit saved: {outname}")
#     print(f"   mean = {mean.getVal():.1f} Â± {mean_err:.1f} GeV, Î = {width.getVal():.1f} Â± {width_err:.1f} GeV, bin width = {bin_width:.1f} GeV")

#     return mean.getVal(), mean_err, width.getVal(), width_err


# def fit_and_plot(filename, histname="mass_fourobject_wr_ee_resolved_sr"):
#     # Extract WR mass
#     match = re.search(r"_WR(\d+)_", filename)
#     mass_str = match.group(1) if match else "Unknown"

#     f = ROOT.TFile.Open(filename)
#     hdir = f.Get("wr_ee_resolved_sr")
#     h = hdir.Get(histname)
#     if not h:
#         raise RuntimeError(f"Histogram {histname} not found in {filename}")

#     # Rebin ~100 GeV
#     bin_width = h.GetBinWidth(1)
#     rebin_factor = max(1, int(100/bin_width))
#     h.Rebin(rebin_factor)
#     bin_width = h.GetBinWidth(1)

#     print(f"\nð File: {filename}")
#     print(f"   Histogram {histname}, WR mass {mass_str}")
#     print(f"   Rebin factor = {rebin_factor}, new bin width = {bin_width:.1f} GeV")

#     # Perform fits
#     g_mean, g_mean_err, g_sigma, g_sigma_err = iterative_gaussian_fit(h, mass_str, bin_width)
#     bw_mean, bw_mean_err, bw_width, bw_width_err = iterative_breitwigner_fit(h, mass_str, bin_width)

#     print(f"--- Comparison for WR{mass_str} ---")
#     print(f"   Gaussian: mean = {g_mean:.1f} Â± {g_mean_err:.1f}, Ï = {g_sigma:.1f} Â± {g_sigma_err:.1f}")
#     print(f"   Breit-Wigner: mean = {bw_mean:.1f} Â± {bw_mean_err:.1f}, Î = {bw_width:.1f} Â± {bw_width_err:.1f}")
#     print("---------------------------------\n")

#     return (g_mean, g_mean_err, g_sigma, g_sigma_err,
#             bw_mean, bw_mean_err, bw_width, bw_width_err)


# def main(files):
#     for filename in files:
#         fit_and_plot(filename)


# if __name__ == "__main__":
#     main(sys.argv[1:])
