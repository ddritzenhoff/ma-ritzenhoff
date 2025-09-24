import json
import numpy as np
import matplotlib.pyplot as plt
import sys
import os
from matplotlib import rcParams

def main(json_files, legend_labels=None):
    """
    Main function to load data from multiple JSON files, process it, 
    and generate a comparative CDF plot with custom styling.

    Args:
        json_files (list): A list of paths to the JSON files.
        legend_labels (list, optional): A list of strings to use as legend labels, 
                                        corresponding to the order of json_files.
                                        If None, filenames will be used.
    """
    # --- Plotting Setup ---
    plt.style.use('seaborn-v0_8-whitegrid') # Apply the style first

    # Set the font type globally *after* applying the style
    rcParams['font.family'] = 'Courier New'

    # Define a color palette
    colors = ['#64a0c8', '#005293', '#0065bd', '#ff7f0e', '#2ca02c', '#d62728']

    fig, ax = plt.subplots(figsize=(7, 4))

    # --- Process each file and plot its CDF ---
    for i, file_path in enumerate(json_files):
        try:
            print(f"Processing file: {file_path}...")
            # --- Load data from the current file ---
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            packets = data.get("packets", [])

            if not packets:
                print(f"Warning: No packets found in {file_path}. Skipping.")
                continue

            # Extract the 'delta_microseconds' from each packet record
            deltas = [p['delta_microseconds'] for p in packets if 'delta_microseconds' in p]

            if not deltas:
                print(f"Warning: No 'delta_microseconds' field found in {file_path}. Skipping.")
                continue

            # --- Calculate CDF ---
            delta_array = np.array(deltas)
            sorted_deltas = np.sort(delta_array)
            y_values = np.arange(1, len(sorted_deltas) + 1) / len(sorted_deltas)

            # --- Plot the CDF for the current file ---
            # Use the provided legend label if available, otherwise use the filename
            if legend_labels and i < len(legend_labels):
                label = legend_labels[i]
            else:
                label = os.path.basename(file_path)
            
            color = colors[i % len(colors)] # Cycle through colors
            ax.plot(sorted_deltas, y_values, drawstyle='steps-post', alpha=0.8, label=label, color=color, linewidth=2)

        except FileNotFoundError:
            print(f"Error: The file '{file_path}' was not found.")
        except json.JSONDecodeError:
            print(f"Error: The file '{file_path}' is not a valid JSON.")
        except KeyError:
            print(f"Error: A packet record in '{file_path}' is missing the 'delta_microseconds' key.")
        except Exception as e:
            print(f"An unexpected error occurred while processing {file_path}: {e}")

    # --- Finalize Plot ---
    # Set plot titles and labels with bold font weight
    # ax.set_title('CDF of Packet Latency (NIC to Userspace)', fontsize=16, fontweight='bold')
    ax.set_xlabel('Time Difference (microseconds)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Percentage of Packets (CDF)', fontsize=12, fontweight='bold')

    # Set axis limits
    ax.set_ylim(0, 1.05)
    ax.set_xlim(left=0)

    # Customize grid and ticks
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    plt.xticks(fontsize=11)
    plt.yticks(fontsize=11)

    # Add a legend to identify the different files
    if ax.get_legend_handles_labels()[0]:
        legend = ax.legend(fontsize=10)
        # Bold the legend labels
        for text in legend.get_texts():
            text.set_fontweight('bold')
    
    # Improve layout and display the plot
    plt.tight_layout()
    # plt.show()
    plt.savefig(f"ptp-log-cdf.pdf")


if __name__ == '__main__':
    # Get file paths and optional legend labels from command-line arguments
    if len(sys.argv) > 1:
        files = []
        labels = None
        
        # We need to distinguish between file paths and potential labels.
        # A simple approach is to look for a specific flag or separator,
        # or assume labels come after all files. Let's assume files first,
        # then if there's a '--labels' flag, the next arguments are labels.
        
        # Find the index of '--labels' if it exists
        try:
            labels_flag_idx = sys.argv.index('--labels')
            files = sys.argv[1:labels_flag_idx]
            labels = sys.argv[labels_flag_idx + 1:]
            
            # Basic validation: ensure number of labels matches number of files
            if len(labels) != len(files):
                print("Error: The number of provided labels must match the number of input files.")
                print("Usage: python cdf-graph.py <file1.json> [file2.json] ... [--labels <label1> <label2> ...]")
                sys.exit(1)

        except ValueError: # '--labels' not found, so all are files
            files = sys.argv[1:]
        
        if not files:
            print("Error: No input files provided.")
            print("Usage: python cdf-graph.py <file1.json> [file2.json] ... [--labels <label1> <label2> ...]")
            sys.exit(1)
            
        main(files, labels)
    else:
        print("Usage: python cdf-graph.py <file1.json> [file2.json] ... [--labels <label1> <label2> ...]")
        sys.exit(1)