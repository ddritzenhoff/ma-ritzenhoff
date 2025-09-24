import json
import matplotlib.pyplot as plt
import os
import argparse

plt.rcParams['font.family'] = 'Courier New'
plt.rcParams['font.monospace'] = 'Courier New'

def load_deltas_from_json(filepath):
    deltas = []
    if not os.path.exists(filepath):
        print(f"Error: File not found at '{filepath}'")
        return deltas
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        if "packets" in data and isinstance(data["packets"], list):
            for packet in data["packets"]:
                if "delta_microseconds" in packet:
                    deltas.append(packet["delta_microseconds"])
        else:
            print(f"Warning: 'packets' key missing or not a list in '{filepath}'.")
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{filepath}'.")
    except Exception as e:
        print(f"Unexpected error reading '{filepath}': {e}")
    return deltas

def plot_delta_boxplots(deltas_list, labels, title, output_filename):
    if all(len(d) == 0 for d in deltas_list):
        print("No data to plot. All delta lists are empty.")
        return

    fig, ax = plt.subplots(figsize=(8, 4))

    bp = ax.boxplot(deltas_list, labels=labels, patch_artist=True,
                    medianprops={'color': '#EA7237', 'linewidth': 1.5})

    for patch in bp['boxes']:
        patch.set_facecolor('#64a0c8')
        patch.set_edgecolor('#0065bd')
        patch.set_linewidth(1.5)

    for whisker in bp['whiskers']:
        whisker.set(color='#005293', linewidth=1.5)
    for cap in bp['caps']:
        cap.set(color='#005293', linewidth=1.5)

    ax.set_ylabel("Time Difference (us)", fontsize=12, fontweight='bold')
    ax.set_xlabel("Datapaths", fontsize=12, fontweight='bold', labelpad=9)
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    plt.xticks(fontsize=11)
    plt.tight_layout()
    plt.savefig("figure0.pdf")

    try:
        plt.savefig(output_filename, bbox_inches='tight', dpi=300)
        print(f"Plot saved as '{output_filename}'")
    except Exception as e:
        print(f"Error saving plot: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Boxplot of delta_microseconds from JSON files.")
    parser.add_argument('--files', nargs='+', required=True, help="Paths to JSON files")
    parser.add_argument('--labels', nargs='*', help="Optional labels for each file")
    parser.add_argument('--output', type=str, default='delta_boxplots.png', help="Output filename")
    parser.add_argument('--title', type=str, default='Delta Value Distributions', help="Plot title")

    args = parser.parse_args()

    if args.labels and len(args.labels) != len(args.files):
        print("Error: Number of labels must match number of files.")
        exit(1)

    deltas_list = []
    labels = args.labels if args.labels else [os.path.basename(f) for f in args.files]

    for filepath in args.files:
        deltas = load_deltas_from_json(filepath)
        deltas_list.append(deltas)

    plot_delta_boxplots(deltas_list, labels, args.title, args.output)

# python3 delta-boxplots.py --file1 no-xdp-log/no-xdp-zipped.json --file2 xdp-log/xdp-zipped.json --output graphs/figure0.pdf --label1 "No XDP" --label2 "XDP" --title "Network Stack Traversal Time Differences (ns)"

# python3 delta-boxplots.py --files no-xdp-log/no-xdp-zipped.json xdp-log/xdp-zipped.json --output figure0.pdf --labels "No XDP" "XDP"