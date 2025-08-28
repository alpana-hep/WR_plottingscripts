import ROOT
ROOT.gROOT.SetBatch(True)
import sys, json, re

def sanitize_filename(s):
    return re.sub(r"[^a-zA-Z0-9_\-]", "_", s)


def overlay_histograms(files, histname, hdir_str, op_str, xaxis_title, index=None):
    hists = []
    colors = [ROOT.kBlue, ROOT.kRed, ROOT.kGreen+2, ROOT.kMagenta]

    c = ROOT.TCanvas("c", "Overlay", 800, 600)
    legend = ROOT.TLegend(0.65, 0.7, 0.9, 0.88)
    legend.SetBorderSize(0)
    legend.SetFillStyle(0)

    for i, f in enumerate(files):
        match = re.search(r"_WR(\d+)_", f)
        mass_str = match.group(1) if match else f
        match = re.search(r"_N(\d+)\.root", f)
        Nmass_str = match.group(1) if match else f
        print(Nmass_str)
        tf = ROOT.TFile.Open(f)
        if not tf or tf.IsZombie():
            print(f"Could not open {f}")
            continue

        hdir = tf.Get(hdir_str)
        if not hdir:
            print(f"Directory {hdir_str} not found in {f}")
            tf.ls()  # debug: list directory contents
            tf.Close()
            continue

        h_orig = hdir.Get(histname)
        # Rebin to ~100 GeV                                                                                                                   
        bin_width = h_orig.GetBinWidth(1)
        rebin_factor = max(1, int(100/bin_width))
        h_orig.Rebin(rebin_factor)

        if not h_orig:
            print(f"Histogram {histname} not found in {f}")
            tf.Close()
            continue

        # fully clone histogram so it's independent of file
        h = h_orig.Clone(f"h_{i}")
        h.SetDirectory(0)
        tf.Close()

        if h.Integral() > 0:
            h.Scale(1.0 / h.Integral())

        h.SetLineColor(colors[i % len(colors)])
        h.SetLineWidth(2)
        h.GetYaxis().SetTitleOffset(1.2)
        hists.append(h)

        draw_opt = "HIST" if len(hists) == 1 else "HIST SAME"
        h.Draw(draw_opt)
        
        legend.AddEntry(h, f"(W,N)=({mass_str},{Nmass_str})", "l")

    if not hists:
        print("No histograms drawn.")
        return

    # Axis title
    hists[0].GetXaxis().SetTitle(xaxis_title)
    hists[0].GetYaxis().SetTitle("Normalized")
    hists[0].GetYaxis().SetTitleSize(0.04)
    hists[0].GetXaxis().SetTitleSize(0.04)
    hists[0].GetYaxis().SetLabelSize(0.04)
    hists[0].GetXaxis().SetLabelSize(0.04)

    ROOT.gPad.SetLogy()
    ROOT.gStyle.SetOptStat(0)
    legend.Draw()

    label = ROOT.TLatex()
    label.SetNDC()
    label.SetTextFont(42)
    label.SetTextSize(0.04)
    label.DrawLatex(0.11, 0.92, "CMS Work in Progress")
    label.DrawLatex(0.6, 0.92, "#sqrt{s} = 13 TeV, Lumi = 54 fb^{-1}")

    c.Update()
    outname = f"plot_{index}" if index is not None else f"overlay_{histname}_diffWR"
    c.SaveAs(outname + ".png")
    c.SaveAs(outname + ".pdf")

    return c, hists

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
