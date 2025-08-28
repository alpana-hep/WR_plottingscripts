import ROOT
import sys, re, json

ROOT.gROOT.SetBatch(True)  
ROOT.gStyle.SetOptStat(0)

def overlay_histograms(files, histname, hdir_str, op_str, xaxis_title):
    c = ROOT.TCanvas("c_"+histname, "", 800, 600)
    ROOT.gPad.SetLogy()
    leg = ROOT.TLegend(0.55, 0.65, 0.85, 0.85)
    leg.SetTextSize(0.04)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)
    leg.SetHeader(op_str)

    first = True
    for i, filename in enumerate(files):
        # Extract WR mass from filename
        match = re.search(r"_WR(\d+)_", filename)
        mass_str = match.group(1) if match else filename

        f = ROOT.TFile.Open(filename)
        hdir = f.Get(hdir_str)
        h_sr = hdir.Get(histname) if hdir else None
        if not h_sr:
            print(f"Histogram {histname} not found in {filename}")
            continue

        h_sr.SetDirectory(0)   # detach from file
        f.Close()              # safe to close now

        # Rebin to ~100 GeV
        bin_width = h_sr.GetBinWidth(1)
        rebin_factor = max(1, int(100/bin_width))
        h_sr.Rebin(rebin_factor)

        # Style
        h_sr.SetLineColor(i+2)
        h_sr.SetMarkerColor(i+2)
        h_sr.SetMarkerStyle(8)
        h_sr.SetMarkerSize(1.2)
        h_sr.GetXaxis().SetTitle(xaxis_title)
        h_sr.GetYaxis().SetTitle("Normalized")
        h_sr.GetYaxis().SetRangeUser(1e-8, 1)

        # Draw overlay
        if first:
            h_sr.Draw("ep")
            first = False
        else:
            h_sr.Draw("ep same")

        leg.AddEntry(h_sr, mass_str, "ep")

    leg.Draw()
    outname = f"overlay_{op_str}_{histname}.png"
    c.SaveAs(outname)
    print(f"Saved {outname}")

def main(files, config_file="hists.json"):
    with open(config_file, "r") as f:
        hist_configs = json.load(f)
    for cfg in hist_configs:
        overlay_histograms(files, **cfg)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 script.py <rootfiles...> <config.json>")
        sys.exit(1)

    *rootfiles, config_file = sys.argv[1:]
    main(rootfiles, config_file)
