import json
import sys

import matplotlib.pyplot as plt
import numpy as np
import matplotlib.colors as mcolors


def draw_time(qiskit_file_path, qpanda_file_path, name1='Qiskit 1.3.0', name2='QPanda3',
              bench_type: str = 'transpiler'):
    qiskit_mean_times = []
    qpanda_mean_times = []
    number_of_qubits = []
    names = []
    qpanda_info_map = dict()
    qiskit_info_map = dict()

    with open(qpanda_file_path, 'r') as file:
        data = json.load(file)

        for item in data["benchmarks"]:
            try:
                mean_value = item['stats']['mean']
                name = item['name']
                if 'input_num_qubits' in item['extra_info']:
                    qubit = item['extra_info']['input_num_qubits']
                else:
                    qubit = 0
                qpanda_info_map[name] = (mean_value, qubit)
            except KeyError:
                print(f"Key not found in item: {item}")

    with open(qiskit_file_path, 'r') as file:
        data = json.load(file)

        i = 0
        for item in data["benchmarks"]:
            try:
                name = item['name']
                if name not in qpanda_info_map:
                    print(name)
                    continue
                mean_value = item['stats']['mean']
                if 'input_num_qubits' in item['extra_info']:
                    qubit = item['extra_info']['input_num_qubits']
                else:
                    qubit = 0
                qiskit_info_map[name] = (mean_value, qubit)
                i += 1
            except KeyError:
                print(f"Key not found in item: {item}")

    if len(qpanda_info_map) != len(qiskit_info_map):
        print('len(qpanda_info_map)!= len(qiskit_info_map)')
        exit(1)
    for k, v in qpanda_info_map.items():
        names.append(k)
        qpanda_mean_times.append(v[0])
        number_of_qubits.append(v[1])
        qiskit_mean_times.append(qiskit_info_map[k][0])
    sorted_arrays = sorted(zip(qpanda_mean_times, qiskit_mean_times, number_of_qubits, names))

    qpanda_mean_times, qiskit_mean_times, number_of_qubits, names = zip(*sorted_arrays)

    for i in range(len(qiskit_mean_times)):
        if qiskit_mean_times[i] < qpanda_mean_times[i]:
            print(names[i], qiskit_mean_times[i] / qpanda_mean_times[i])

    # Create figure and axes
    fig, ax = plt.subplots(figsize=(10, 8))

    # Scatter plot for Qiskit 1.3.0 runtimes (Y-axis) vs pyqpanda3 runtimes (X-axis)
    scatter = ax.scatter(
        qpanda_mean_times,
        qiskit_mean_times,
        c=number_of_qubits,
        cmap='viridis',
        norm=mcolors.NoNorm(vmin=min(number_of_qubits), vmax=max(number_of_qubits)),
        alpha=0.8
    )

    # Log-log scale
    ax.set_xscale('log')
    ax.set_yscale('log')

    # Plot diagonal reference line (y = x)
    x = np.logspace(-3, 3, 1000)
    ax.plot(x, x, '--', linewidth=1, label='Equal Runtime')

    # Performance improvement zones using fill_between
    speedup_regions = [5, 20, 80, 320]
    colors = ['blue', 'green', 'orange', 'purple', ]
    for i, factor in enumerate(speedup_regions):
        lower_bound = x / factor
        upper_bound = x / (speedup_regions[i - 1]) if i > 0 else x

        ax.fill_betweenx(x, lower_bound, upper_bound, color=colors[i], alpha=0.2,
                         label=f"{speedup_regions[i - 1] if i > 0 else 1}-{factor}x Speedup")

    # Colorbar
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Number of Qubits')

    # Labels and title
    ax.set_xlabel(f'{name2} Runtime (sec.)', fontsize=12)
    ax.set_ylabel(f'{name1} Runtime (sec.)', fontsize=12)
    ax.set_title(f'{name2} vs {name1} running benchpress {bench_type} benchmarks', fontsize=14)

    plt.xlim(1e-5, 1e3)
    plt.ylim(1e-3, 1e3)

    # Add legend for speedup regions
    ax.legend(loc='upper left', fontsize=10)

    # Performance improvement/regression zones labels
    ax.text(1.5e-4, 5e1, "Improvement", fontsize=14,
            color='white',
            bbox=dict(facecolor='blue', alpha=0.5, edgecolor='black', boxstyle='round,pad=0.5'),
            # ha='center',
            va='center')

    ax.text(7e1, 2e-3, "Regression", fontsize=14,
            color='white',
            bbox=dict(facecolor='blue', alpha=0.5, edgecolor='black', boxstyle='round,pad=0.5'),
            # ha='center',
            va='center')

    # Grid and layout
    ax.grid(linestyle='--', linewidth=0.5)
    plt.tight_layout()
    plt.show()


def draw_2q_depth(qiskit_file_path, qpanda_file_path, name1='Qiskit 1.3.0', name2='QPanda3'):
    qiskit_mean_times = []
    qpanda_mean_times = []
    number_of_qubits = []
    names = []

    with open(qpanda_file_path, 'r') as file:
        data = json.load(file)

        for item in data["benchmarks"]:
            try:
                mean_value = item['extra_info']['output_depth_2q']
                qpanda_mean_times.append(mean_value)
                name = item['name']
                qubit = item['extra_info']['input_num_qubits']
                names.append(name)
                number_of_qubits.append(qubit)
            except KeyError:
                print(f"Key not found in item: {item}")

    with open(qiskit_file_path, 'r') as file:
        data = json.load(file)

        i = 0
        for item in data["benchmarks"]:
            try:
                name = item['name']
                if name != names[i]:
                    print(name)
                    continue
                mean_value = item['extra_info']['output_depth_2q']
                qiskit_mean_times.append(mean_value)
                i += 1

            except KeyError:
                print(f"Key not found in item: {item}")

    if len(qpanda_mean_times) != len(qiskit_mean_times):
        print('len(qpanda_mean_times)!= len(qiskit_mean_times)')
        exit(1)

    sorted_arrays = sorted(zip(qpanda_mean_times, qiskit_mean_times, number_of_qubits, names))

    qpanda_mean_times, qiskit_mean_times, number_of_qubits, names = zip(*sorted_arrays)

    for i in range(len(qiskit_mean_times)):
        if qiskit_mean_times[i] < qpanda_mean_times[i]:
            print(names[i], qiskit_mean_times[i] / qpanda_mean_times[i])

    # Create figure and axes
    fig, ax = plt.subplots(figsize=(10, 8))

    # Scatter plot for Qiskit 1.3.0 runtimes (Y-axis) vs pyqpanda3 runtimes (X-axis)
    scatter = ax.scatter(
        qpanda_mean_times,
        qiskit_mean_times,
        c=number_of_qubits,
        cmap='viridis',
        norm=mcolors.LogNorm(vmin=min(number_of_qubits), vmax=max(number_of_qubits)),
        alpha=0.8
    )

    # Log-log scale
    ax.set_xscale('log')
    ax.set_yscale('log')

    # Plot diagonal reference line (y = x)
    x = np.logspace(-0, 6, 1000)
    ax.plot(x, x, '--', linewidth=1, label='Equal Runtime')

    # Performance improvement zones using fill_between
    speedup_regions = [5, 20, 80, 320]
    colors = ['blue', 'green', 'orange', 'purple', ]
    for i, factor in enumerate(speedup_regions):
        lower_bound = x / factor
        upper_bound = x / (speedup_regions[i - 1]) if i > 0 else x

        ax.fill_betweenx(x, lower_bound, upper_bound, color=colors[i], alpha=0.2,
                         label=f"{speedup_regions[i - 1] if i > 0 else 1}-{factor}x Speedup")

    # Colorbar
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Number of Qubits')

    # Labels and title
    ax.set_xlabel(f'{name2} 2q_depth ', fontsize=12)
    ax.set_ylabel(f'{name1} 2q_depth ', fontsize=12)
    ax.set_title(f'{name1} vs {name2} running benchpress transpile benchmarks', fontsize=14)

    plt.xlim(1, 1e6)
    plt.ylim(1, 1e6)

    # Add legend for speedup regions
    ax.legend(loc='upper left', fontsize=10)

    # Performance improvement/regression zones labels
    ax.text(1.5e0, 5e4, "Improvement", fontsize=14,
            color='white',
            bbox=dict(facecolor='blue', alpha=0.5, edgecolor='black', boxstyle='round,pad=0.5'),
            # ha='center',
            va='center')

    ax.text(7e4, 2e0, "Regression", fontsize=14,
            color='white',
            bbox=dict(facecolor='blue', alpha=0.5, edgecolor='black', boxstyle='round,pad=0.5'),
            # ha='center',
            va='center')

    # Grid and layout
    ax.grid(linestyle='--', linewidth=0.5)
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    arguments = sys.argv[1:]
    print("argv:", arguments)
    qiskit_file_path = arguments[0]
    qpanda_file_path = arguments[1]
    bench_type = 'transpiler'
    draw_time(qiskit_file_path, qpanda_file_path, bench_type=bench_type)
