import ROOT
import sys, re

def breit_wigner(x, par):
    """Breit-Wigner function"""
    return par[0] * (par[1]**2) / ((x[0]-par[2])**2 + (par[1]**2)/4)

def fit_breit_wigner(histo):
    # Define fit function with initial parameters
    fBW = ROOT.TF1("fBW", breit_wigner, histo.GetXaxis().GetXmin(), histo.GetXaxis().GetXmax(), 3)
    fBW.SetParNames("Norm", "Gamma", "M")
    fBW.SetParameters(histo.GetMaximum(), 50.0, histo.GetMean())  # initial guess

    # Iterative fitting: first full range, then ±2Γ
    histo.Fit(fBW, "RQ0")  # first quiet fit
    for _ in range(3):  # refine
        mean, gamma = fBW.GetParameter(2), abs(fBW.GetParameter(1))
        low, high = max(histo.GetXaxis().GetXmin(), mean - 2*gamma), min(histo.GetXaxis().GetXmax(), mean + 2*gamma)
        fBW.SetRange(low, high)
        histo.Fit(fBW, "RQ0")

    return fBW

def extract_wr_mass(filename):
    match = re.search(r"_WR(\d+)_", filename)
    return int(match.group(1)) if match else None

def main(files):
    ROOT.gStyle.SetOptStat(0)  # remove stat box
    ROOT.gStyle.SetLegendBorderSize(0)  # no legend border
    c = ROOT.TCanvas("c", "WR mass comparison", 800, 600)
    legend = ROOT.TLegend(0.55, 0.65, 0.85, 0.88)
    legend.SetTextSize(0.035)

    colors = [ROOT.kRed, ROOT.kBlue, ROOT.kGreen+2, ROOT.kMagenta, ROOT.kOrange]
    fits = []

    for i, f in enumerate(files):
        wr_mass = extract_wr_mass(f)
        infile = ROOT.TFile.Open(f)
        hist = infile.Get("wr_ee_resolved_sr/mass_fourobject_wr_ee_resolved_sr")

        if not hist:
            print(f"Histogram not found in {f}")
            continue

        hist.Rebin(int(100/hist.GetBinWidth(1)))  # rebin to 100 GeV
        hist.SetLineColor(colors[i % len(colors)])
        hist.SetLineWidth(2)
        hist.Scale(1.0/hist.Integral())  # normalize

        if i == 0:
            hist.SetTitle("")
            hist.GetXaxis().SetTitle("M_{eejj} [GeV]")
            hist.GetYaxis().SetTitle("Event yield / bin")
            hist.Draw("HIST")
        else:
            hist.Draw("HIST SAME")

        # Fit with adaptive Breit-Wigner
        fBW = fit_breit_wigner(hist)
        fBW.SetLineColor(colors[i % len(colors)])
        fBW.SetLineStyle(2)  # dotted line
        fBW.Draw("SAME")

        fits.append(fBW)

        legend.AddEntry(hist, f"WR {wr_mass} GeV, Γ={fBW.GetParameter(1):.1f} GeV", "l")

    legend.Draw()
    c.SaveAs("wr_mass_breitwigner_iterative.pdf")
    print("Plot saved as wr_mass_breitwigner_iterative.pdf")

if __name__ == "__main__":
    main(sys.argv[1:])
