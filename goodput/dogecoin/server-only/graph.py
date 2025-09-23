import matplotlib.pyplot as plt
from matplotlib import rcParams

# Set the font type globally
rcParams['font.family'] = 'Courier New'

# Data
data = {
    'default-GSO/GRO': 1.69,
    'default': 4.11,
    'XDP_SKB': 2.16,
    'XDP_DRV': 2.07,
    'XDP_DRV+zc': 3.03,
}

# Error values for each datapath
errors = {
    'default-GSO/GRO': .052,
    'default': 0.207,
    'XDP_SKB': 0.086,
    'XDP_DRV': 0.098,
    'XDP_DRV+zc': 0.087,
}

# Subsets of datapaths for each graph
subsets = [
    ['default-GSO/GRO', 'default', 'XDP_SKB', 'XDP_DRV', 'XDP_DRV+zc'],  # Third graph
]

# Titles for each graph
titles = [
    'XDP Modes: Server-Side Comparison (ixgbe)',
]

# Create each graph
for i, subset in enumerate(subsets):
    versions = subset
    throughput = [data[version] for version in versions]
    error_values = [errors[version] for version in versions]

    plt.figure(figsize=(7, 4))
    # Customize error bar color and cap size
    error_kw = {'ecolor': '#005293', 'capsize': 5, 'elinewidth': 1.5}
    plt.bar(versions, throughput, yerr=error_values, error_kw=error_kw, color='#64a0c8', edgecolor='#0065bd')

    # Adjust y-axis limits
    plt.ylim(0, max(data.values()) + 2.0)  # Add extra space above bars to avoid overlap

    # Add labels and title
    plt.xlabel('Datapaths', fontsize=12, fontweight='bold', labelpad=9)
    plt.ylabel('Goodput (Gbps)', fontsize=12, fontweight='bold')
    # plt.title(titles[i], fontsize=14, fontweight='bold')
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Increase font size of x-axis labels
    plt.xticks(fontsize=11)

    # Show values on top of bars, adjusted to avoid overlap with error bars
    for j, value in enumerate(throughput):
        plt.text(j, value + error_values[j] + 0.2, f'{value}', ha='center', fontsize=10, fontweight='bold')

    # Show the plot
    plt.tight_layout()
    # plt.show()
    plt.savefig(f"figure{i}.pdf")