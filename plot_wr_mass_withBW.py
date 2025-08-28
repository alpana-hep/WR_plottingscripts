import ROOT
import sys, re

def breitwigner(x, par):
    # par[0] = normalization, par[1] = mean, par[2] = width
    return par[0] * (0.5*par[2])**2 / ((x[0]-par[1])**2 + (0.5*par[2])**2)

def iterative_gaussian_fit(hist, n_iter=3):
    """Iterative Gaussian fit within #pm#sigma"""
    fit_func = ROOT.TF1("gaus_tmp", "gaus", hist.GetXaxis().GetXmin(), hist.GetXaxis().GetXmax())
    hist.Fit(fit_func, "RQ0")

    mean, sigma = fit_func.GetParameter(1), fit_func.GetParameter(2)

    for _ in range(n_iter):
        fit_range_min = mean - 2*sigma
        fit_range_max = mean + 2*sigma
        fit_func = ROOT.TF1("gaus_fit", "gaus", fit_range_min, fit_range_max)
        hist.Fit(fit_func, "RQ0")
        mean, sigma = fit_func.GetParameter(1), fit_func.GetParameter(2)

    resolution = sigma / mean if mean != 0 else 0
    return fit_func, mean, sigma, resolution

def fit_breit_wigner(histo):
    # Define fit function with initial parameters
    fBW = ROOT.TF1("fBW", breit_wigner, histo.GetXaxis().GetXmin(), histo.GetXaxis().GetXmax(), 3)
    fBW.SetParNames("Norm", "Gamma", "M")
    fBW.SetParameters(histo.GetMaximum(), 50.0, histo.GetMean())  # initial guess

    # Iterative fitting: first full range, then Â±2Î
    histo.Fit(fBW, "RQ0")  # first quiet fit
    for _ in range(3):  # refine
        mean, gamma = fBW.GetParameter(2), abs(fBW.GetParameter(1))
        low, high = max(histo.GetXaxis().GetXmin(), mean - 2*gamma), min(histo.GetXaxis().GetXmax(), mean + 2*gamma)
        fBW.SetRange(low, high)
        histo.Fit(fBW, "RQ0")

    return fBW

def fit_and_plot(filename, histname="mass_fourobject_wr_ee_resolved_sr"):
    # Extract WR mass from filename
    match = re.search(r"_WR(\d+)_", filename)
    mass_str = match.group(1) if match else "Unknown"

    f = ROOT.TFile.Open(filename)
    hdir = f.Get("wr_ee_resolved_sr")
    h = hdir.Get(histname)
    if not h:
        raise RuntimeError(f"Histogram {histname} not found in {filename}")

    # Rebin to ~100 GeV
    bin_width = h.GetBinWidth(1)
    rebin_factor = max(1, int(100/bin_width))
    h.Rebin(rebin_factor)

    # Breit-Wigner TF1
    xmin = h.GetXaxis().GetXmin()
    xmax = h.GetXaxis().GetXmax()
    bw = ROOT.TF1(f"bw_{mass_str}", breitwigner, xmin, xmax, 3)
    bw.SetParNames("Norm", "Mean", "Width")
    bw.SetParameters(h.GetMaximum(), h.GetMean(), h.GetRMS())  # initial guesses

    # Iterative fit in 2*width region
    fit_result = h.Fit(bw, "SRQ0")  # quiet mode, store result
    if fit_result.Status() != 0:
        print(f"⚠️ Fit failed for {filename}")
    mean, width = bw.GetParameter(1), bw.GetParameter(2)
    print(mean, width)
    # Restrict range to ±2*width
    bw.SetRange(mean-2*width, mean+2*width)
    h.Fit(bw, "SRQ0")  # refit in restricted range
    mean, width = bw.GetParameter(1), bw.GetParameter(2)
    bw.SetRange(mean-2*width, mean+2*width)
    h.Fit(bw, "SRQ0")  # refit in restricted range
    mean, width = bw.GetParameter(1), bw.GetParameter(2)
    # Draw
    c = ROOT.TCanvas("c", "", 800, 600)
    h.SetLineColor(ROOT.kBlue)
    h.SetMarkerStyle(20)
    h.Draw("E")

    # Draw dotted fit
    bw.SetLineStyle(2)
    bw.SetLineColor(ROOT.kRed)
    bw.Draw("SAME")
    ROOT.gStyle.SetOptStat(0)
    # Legend
    leg = ROOT.TLegend(0.55, 0.65, 0.85, 0.85)
    leg.SetTextSize(0.04)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)
    leg.AddEntry(h, f"WR mass {mass_str} GeV", "lep")
    leg.AddEntry(bw, f"#Gamma= {width:.1f} GeV", "l")
    leg.Draw()

    c.Update()
    c.SaveAs(f"wr_mass_bw_WR{mass_str}.png")

    print(f"✅ Saved plot wr_mass_bw_WR{mass_str}.pdf")
    print(f"   Bin width after rebinning: {h.GetBinWidth(1):.1f} GeV")
    print(f"   Fit result: mean = {mean:.1f}, width = {width:.1f}")

    return mean, width

def main(files):
    for filename in files:
        fit_and_plot(filename)

if __name__ == "__main__":
    main(sys.argv[1:])
