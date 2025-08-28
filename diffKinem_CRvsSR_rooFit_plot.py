import ROOT
import sys, re, json

ROOT.gROOT.SetBatch(True)  
ROOT.gStyle.SetOptStat(0)


def fit_and_plot(filename, histname, histname1, hdir_str, hdir_cr_str, op_str, xaxis_title):
    # Extract WR mass from filename
    match = re.search(r"_WR(\d+)_", filename)
    mass_str = match.group(1) if match else "Unknown"

    # Open ROOT file
    f = ROOT.TFile.Open(filename)

    hdir = f.Get(hdir_str)  #"wr_ee_resolved_sr")
    h_sr = hdir.Get(histname)
    hdir_cr = f.Get(hdir_cr_str)
    h_cr = hdir_cr.Get(histname1) 

    if not h_sr or not h_cr:
        raise RuntimeError(f"Histograms {histname} and {histname1} not found in {filename}")

    # Rebin to ~100 GeV
    bin_width = h_sr.GetBinWidth(1)
    rebin_factor = max(1, int(100/bin_width))
    h_sr.Rebin(rebin_factor)
    h_cr.Rebin(rebin_factor)

    # Draw
    c = ROOT.TCanvas("c_bw", "", 800, 600)
    ROOT.gPad.SetLogy()

    for h, col, label in [(h_sr, ROOT.kRed, "SR"),
                          (h_cr, ROOT.kBlue, "CR")]:
        h.SetLineColor(col)
        h.SetMarkerColor(col)
        h.SetMarkerStyle(8)
        h.SetMarkerSize(1.2)
        h.GetXaxis().SetTitle(xaxis_title)
        h.GetYaxis().SetTitle("Normalized")
        h.GetYaxis().SetRangeUser(1e-8, 1)

    h_sr.Draw("ep")
    h_cr.Draw("ep same")

    leg = ROOT.TLegend(0.55, 0.65, 0.85, 0.85)
    leg.SetTextSize(0.04)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)
    leg.SetHeader(op_str)
    leg.AddEntry(h_sr, "SR","ep")
    leg.AddEntry(h_cr, "CR","ep")
    leg.Draw()

    outname = f"SRvsCR_{op_str}_{histname}_norm.png"
    c.SaveAs(outname)
    print(f"Saved {outname}")


def main(files, config_file="hists.json"):
    with open(config_file, "r") as f:
        hist_configs = json.load(f)

    for filename in files:
        for cfg in hist_configs:
            fit_and_plot(filename, **cfg)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 diffKinem_CRvsSR_rooFit_plot.py <rootfiles...> <config.json>")
        sys.exit(1)

    *rootfiles, config_file = sys.argv[1:]
    main(rootfiles, config_file)


