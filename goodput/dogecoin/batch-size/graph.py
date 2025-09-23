import matplotlib.pyplot as plt
from matplotlib import rcParams

# Set the font type globally
rcParams['font.family'] = 'Courier New'

# Data
data = {
    '1': 1.83,
    '2': 2.29,
    '4': 2.65,
    '8': 2.98,
    '16': 3.26,
    '32': 3.48,
    '64': 3.56,
    '128': 3.54
}

# Error values for each datapath
errors = {
    '1': .060,
    '2': .101,
    '4': .103,
    '8': .176,
    '16': .188,
    '32': .182,
    '64': .185,
    '128': .137
}

# Subsets of datapaths for each graph
subsets = [
    ['1', '2', '4', '8', '16', '32', '64', '128'],
]

# Titles for each graph
titles = [
    'Comparison: XDP_DRV+zero-copy Batch Sizes',
]

X_LABEL = "Batch Sizes"
Y_LABEL = "Goodput (Gbps)"

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
    plt.ylim(0, max(data.values()) + 1.2)  # Add extra space above bars to avoid overlap

    # Add labels and title
    plt.xlabel(X_LABEL, fontsize=12, fontweight='bold', labelpad=9)
    plt.ylabel(Y_LABEL, fontsize=12, fontweight='bold')
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