import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog, simpledialog

# File selection function
root = tk.Tk()
root.withdraw()

control_file = filedialog.askopenfilename(title="Select the control data file")
experiment_file = filedialog.askopenfilename(title="Select the experimental data file")

# Input parameters
chromosome = simpledialog.askstring("Chromosome selection", "Enter chromosome number (e.g., chr1)")
threshold = simpledialog.askfloat("Difference threshold", "Enter difference threshold (%)", minvalue=0, maxvalue=100)
min_region_size = simpledialog.askinteger("Minimum region size", "Enter minimum region size", minvalue=1)
window_size = simpledialog.askinteger("Window size", "Enter window size for change density calculation (in bp)", minvalue=1000)

# Load files
control_data = pd.read_csv(control_file, sep="\t", header=None, names=["chr", "start", "end", "signal"])
experiment_data = pd.read_csv(experiment_file, sep="\t", header=None, names=["chr", "start", "end", "signal"])

# Keep only the selected chromosome
control_chr = control_data[control_data["chr"] == chromosome].copy()
experiment_chr = experiment_data[experiment_data["chr"] == chromosome].copy()

# Merge two dataframes by coordinates
comparison = pd.merge(control_chr, experiment_chr, on=["chr", "start", "end"], suffixes=("_control", "_experiment"))

# Calculate signal difference
comparison["diff"] = comparison["signal_experiment"] - comparison["signal_control"]

# Filter — keep regions with a difference greater than the specified threshold
significant_changes = comparison[abs(comparison["diff"]) > threshold].copy()

# Save to file
output_file = f"significant_changes_{chromosome}.txt"
significant_changes.to_csv(output_file, sep="\t", index=False)

print(f"Found {len(significant_changes)} significant changes!")

# Corrected region size calculation
significant_changes.loc[:, "region_size"] = significant_changes["end"] - significant_changes["start"]

# Region size statistics
print("Minimum region size:", significant_changes["region_size"].min())
print("Average region size:", significant_changes["region_size"].mean())
print("Maximum region size:", significant_changes["region_size"].max())

# Filter by region size
long_regions = significant_changes[significant_changes["region_size"] >= min_region_size].copy()

print(f"Remaining {len(long_regions)} long regions with changes!")

# Calculate change density in windows
chrom_length = max(comparison["end"])
bins = list(range(0, chrom_length, window_size))
change_density = [((long_regions["start"] >= start) & (long_regions["start"] < start + window_size)).sum() 
                  for start in bins]

plt.figure(figsize=(10, 5))
plt.bar(bins, change_density, width=window_size, color="red", edgecolor="black")
plt.title(f"Methylation change density on {chromosome} (Experiment vs Control)")
plt.xlabel("Chromosome coordinate")
plt.ylabel(f"Number of significant changes per {window_size} bp")
plt.grid(axis="y")

# Save plot as PNG
plt.savefig(f"methylation_changes_{chromosome}.png", dpi=300)
plt.show()

print(f"Plot saved as methylation_changes_{chromosome}.png")
