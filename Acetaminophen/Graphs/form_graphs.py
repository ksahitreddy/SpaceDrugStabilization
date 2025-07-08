import matplotlib.pyplot as plt

def load_xvg(filename):
    x, y = [], []
    with open(filename, 'r') as f:
        for line in f:
            if line.startswith(('#', '@')):
                continue
            parts = line.strip().split()
            if len(parts) >= 2:
                x.append(float(parts[0]))
                y.append(float(parts[1]))
    return x, y

# List of .xvg files and plot labels
files = [
    ('kinetic_earth.xvg', 'KE (kJ/mol)', 'Time (ps)'),
    ('kinetic_space.xvg', 'KE (kJ/mol)', 'Time (ps)'),
    ('kinetic_dppc.xvg', 'KE (kJ/mol)', 'Time (ps)')
]

# Create 1 row, 3 columns of subplots
fig, axs = plt.subplots(1, 3, figsize=(15, 4))  # Adjust width for clarity

for i, (file, ylabel, xlabel) in enumerate(files):
    x, y = load_xvg(file)
    axs[i].plot(x, y, color='tab:blue')
    axs[i].set_xlabel(xlabel)
    axs[i].set_ylabel(ylabel)
    axs[i].grid(True)

plt.tight_layout()
plt.savefig("acetaminophen_KE_earth_space_DPPC.png", dpi=300)
plt.show()

