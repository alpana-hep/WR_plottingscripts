#!/usr/bin/env python3

import uproot
import numpy as np
import matplotlib.pyplot as plt
import argparse
import re
from scipy.optimize import curve_fit

# -----------------
# Gaussian function
# -----------------
def gauss(x, A, mu, sigma):
    return A * np.exp(-0.5 * ((x - mu) / sigma) ** 2)

# -----------------
# Extract WR mass from filename
# -----------------
def extract_mass_from_filename(filename):
    match = re.search(r"_WR(\d+)", filename)
    return match.group(1) if match else "unknown"

# -----------------
# Main
# -----------------
def main():
    parser = argparse.ArgumentParser(description="Overlay WR mass histograms with Gaussian fits")
    parser.add_argument("files", nargs="+", help="Input ROOT files")
    parser.add_argument("--histdir", default="wr_ee_resolved_sr")
    parser.add_argument("--histname", default="mass_fourobject_wr_ee_resolved_sr")
    parser.add_argument("--output", default="overlay.pdf")
    args = parser.parse_args()

    plt.figure(figsize=(8,6))
    colors = ["r", "b", "g", "m", "orange", "c"]

    for i, filename in enumerate(args.files):
        # --- Read histogram
        with uproot.open(filename) as f:
            h = f[f"{args.histdir}/{args.histname}"]
            values = h.values()
            edges = h.axes[0].edges()
            centers = 0.5 * (edges[1:] + edges[:-1])

        # --- Rebin to 100 GeV
        bin_width = edges[1] - edges[0]
        rebin_factor = max(1, int(round(100.0 / bin_width)))
        values = values[: len(values) - len(values) % rebin_factor]  # trim if not divisible
        values = values.reshape(-1, rebin_factor).sum(axis=1)
        edges = edges[::rebin_factor]
        centers = 0.5 * (edges[1:] + edges[:-1])

        # --- Normalize
        if values.sum() > 0:
            values = values / values.sum()

        # --- First rough Gaussian fit
        try:
            p0 = [values.max(), centers[np.argmax(values)], 200.]  # initial guess
            popt, pcov = curve_fit(gauss, centers, values, p0=p0)
            mu, sigma = popt[1], abs(popt[2])

            # Refit within Â±2Ï
            mask = (centers > mu - 2*sigma) & (centers < mu + 2*sigma)
            popt, pcov = curve_fit(gauss, centers[mask], values[mask], p0=popt)
            mu, sigma = popt[1], abs(popt[2])
            resolution = sigma / mu if mu != 0 else 0.0

            # --- Plot histogram
            plt.step(centers, values, where="mid", color=colors[i % len(colors)], lw=2,
                     label=f"WR {extract_mass_from_filename(filename)} GeV (Ï/Î¼={resolution:.3f})")

            # --- Plot fit
            xfit = np.linspace(mu - 4*sigma, mu + 4*sigma, 200)
            plt.plot(xfit, gauss(xfit, *popt), "--", color=colors[i % len(colors)])
            print(f"{filename}: mu={mu:.2f}, sigma={sigma:.2f}, Ï/Î¼={resolution:.4f}")

        except RuntimeError:
            print(f"Fit failed for {filename}")
            plt.step(centers, values, where="mid", color=colors[i % len(colors)], lw=2,
                     label=f"WR {extract_mass_from_filename(filename)} GeV (fit failed)")

    # --- CMS-style cosmetics
    plt.xlabel("Mass [GeV]", fontsize=14)
    plt.ylabel("Event yield / bin", fontsize=14)
    plt.legend(fontsize=12, frameon=False)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(args.output)
    print(f"Saved {args.output}")

if __name__ == "__main__":
    main()
