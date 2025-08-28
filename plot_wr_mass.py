# #!/usr/bin/env python3

# import ROOT
# import argparse
# import re

# def get_histogram(filename, histdir, histname):
#     f = ROOT.TFile.Open(filename)
#     if not f or f.IsZombie():
#         raise RuntimeError(f"Could not open file {filename}")
#     hist = f.Get(f"{histdir}/{histname}")
#     if not hist:
#         raise RuntimeError(f"Histogram {histdir}/{histname} not found in {filename}")
#     hist.SetDirectory(0)
#     f.Close()
#     return hist.Clone()  # clone so it survives after file close

# def fit_histogram(hist):
#     # First rough fit over full range
#     tmpfit = ROOT.TF1("tmpfit", "gaus", hist.GetXaxis().GetXmin(), hist.GetXaxis().GetXmax())
#     hist.Fit(tmpfit, "RQ0")
#     mean, sigma = tmpfit.GetParameter(1), tmpfit.GetParameter(2)

#     # Refit in Â±2Ï range
#     fit_func = ROOT.TF1("fit_func", "gaus", mean - 2*sigma, mean + 2*sigma)
#     hist.Fit(fit_func, "RQ0")  # do not spam output
#     mean, sigma = fit_func.GetParameter(1), fit_func.GetParameter(2)
#     resolution = sigma / mean if mean != 0 else 0
#     return fit_func, mean, sigma, resolution

# def extract_mass_from_filename(filename):
#     match = re.search(r"_WR(\d+)", filename)
#     return match.group(1) if match else "unknown"

# def main():
#     parser = argparse.ArgumentParser(description="Fit and overlay CMS histograms")
#     parser.add_argument("files", nargs="+", help="Input ROOT files")
#     parser.add_argument("--histdir", default="wr_ee_resolved_sr")
#     parser.add_argument("--histname", default="mass_fourobject_wr_ee_resolved_sr")
#     parser.add_argument("--output", default="overlay.pdf")
#     args = parser.parse_args()
    
#     ROOT.gStyle.SetOptStat(0)
#     ROOT.gStyle.SetOptFit(0)

#     # --- First loop: prepare histograms & get max value
#     hists, fits = [], []
#     max_val = 0
#     for filename in args.files:
#         hist = get_histogram(filename, args.histdir, args.histname)

#         # Rebin to 100 GeV
#         bin_width = hist.GetXaxis().GetBinWidth(1)
#         rebin_factor = max(1, int(round(100.0 / bin_width)))
#         hist.Rebin(rebin_factor)

#         # Normalize
#         if hist.Integral() > 0:
#             hist.Scale(1.0 / hist.Integral())

#         # Track max for scaling
#         if hist.GetMaximum() > max_val:
#             max_val = hist.GetMaximum()

#         hists.append((filename, hist))

#     # --- Draw everything
#     c = ROOT.TCanvas("c", "c", 800, 600)
#     leg = ROOT.TLegend(0.55, 0.65, 0.88, 0.88)
#     leg.SetTextSize(0.04)
#     leg.SetBorderSize(0)
#     leg.SetFillStyle(0)

#     colors = [ROOT.kRed, ROOT.kBlue, ROOT.kGreen+2, ROOT.kMagenta, ROOT.kOrange+7, ROOT.kCyan+2]

#     for i, (filename, hist) in enumerate(hists):
#         hist.SetLineColor(colors[i % len(colors)])
#         hist.SetLineWidth(2)
#         hist.GetYaxis().SetTitle("Event yield / bin")
#         hist.GetXaxis().SetTitle("Mass [GeV]")
#         hist.SetMaximum(max_val * 1.2)  # ensure visibility for all

#         # Fit
#         fit_func, mean, sigma, resolution = fit_histogram(hist)
#         print(f"File: {filename}, mean = {mean:.2f}, sigma = {sigma:.2f}, resolution (Ï/Î¼) = {resolution:.4f}")

#         # Draw histogram
#         drawopt = "HIST E" if i == 0 else "HIST E SAME"
#         hist.Draw(drawopt)

#         # Draw Gaussian
#         fit_func.SetLineColor(colors[i % len(colors)])
#         fit_func.SetLineStyle(2)
#         fit_func.Draw("SAME")

#         # Legend entry with WR mass
#         wr_mass = extract_mass_from_filename(filename)
#         leg.AddEntry(hist, f"WR {wr_mass} GeV (Ï/Î¼={resolution:.3f})", "l")

#     leg.Draw()
#     c.SaveAs(args.output)

# if __name__ == "__main__":
#     main()


#!/usr/bin/env python3

import ROOT
import argparse
import re

def get_histogram(filename, histdir, histname):
    f = ROOT.TFile.Open(filename)
    if not f or f.IsZombie():
        raise RuntimeError(f"Could not open file {filename}")
    hist = f.Get(f"{histdir}/{histname}")
    if not hist:
        raise RuntimeError(f"Histogram {histdir}/{histname} not found in {filename}")
    hist.SetDirectory(0)
    f.Close()
    return hist.Clone()

def iterative_gaussian_fit(hist, n_iter=3):
    """Iterative Gaussian fit within Â±2Ï"""
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

def extract_mass_from_filename(filename):
    match = re.search(r"_WR(\d+)", filename)
    return match.group(1) if match else "unknown"

def main():
    parser = argparse.ArgumentParser(description="Fit and overlay CMS histograms")
    parser.add_argument("files", nargs="+", help="Input ROOT files")
    parser.add_argument("--histdir", default="wr_ee_resolved_sr")
    parser.add_argument("--histname", default="mass_fourobject_wr_ee_resolved_sr")
    parser.add_argument("--output", default="overlay.pdf")
    args = parser.parse_args()
    
    ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetOptFit(0)

    hists, max_val = [], 0
    for filename in args.files:
        hist = get_histogram(filename, args.histdir, args.histname)

        # Rebin to ~100 GeV
        bin_width = hist.GetXaxis().GetBinWidth(1)
        rebin_factor = max(1, int(round(100.0 / bin_width)))
        hist.Rebin(rebin_factor)
        final_bin_width = hist.GetXaxis().GetBinWidth(1)
        print(f"{filename}: rebinned to bin width = {final_bin_width} GeV")

        if hist.Integral() > 0:
            hist.Scale(1.0 / hist.Integral())

        max_val = max(max_val, hist.GetMaximum())
        hists.append((filename, hist))

    c = ROOT.TCanvas("c", "c", 800, 600)
    leg = ROOT.TLegend(0.55, 0.65, 0.88, 0.88)
    leg.SetTextSize(0.04)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)

    colors = [ROOT.kRed, ROOT.kBlue, ROOT.kGreen+2, ROOT.kMagenta, ROOT.kOrange+7, ROOT.kCyan+2]

    for i, (filename, hist) in enumerate(hists):
        hist.SetLineColor(colors[i % len(colors)])
        hist.SetLineWidth(2)
        hist.GetYaxis().SetTitle("Event yield / bin")
        hist.GetXaxis().SetTitle("Mass [GeV]")
        hist.SetMaximum(max_val * 1.2)

        fit_func, mean, sigma, resolution = iterative_gaussian_fit(hist)
        print(f"{filename}: mean={mean:.2f}, sigma={sigma:.2f}, Ï/Î¼={resolution:.4f}")

        opt = "HIST E" if i == 0 else "HIST E SAME"
        hist.Draw(opt)

        fit_func.SetLineColor(colors[i % len(colors)])
        fit_func.SetLineStyle(3)  # dotted line
        fit_func.Draw("SAME")

        wr_mass = extract_mass_from_filename(filename)
        leg.AddEntry(hist, f"WR {wr_mass} GeV (Ï/Î¼={resolution:.3f})", "l")

    leg.Draw()
    c.SaveAs(args.output)

if __name__ == "__main__":
    main()
