import json
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

def load_data(directory):
    all_down_x = []
    all_down_y = []
    all_up_x = []
    all_up_y = []

    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            file_path = os.path.join(directory, filename)
            with open(file_path, 'r') as f:
                data = json.load(f)
                all_down_x.append(data['down_x'])
                all_down_y.append(data['down_y'])
                all_up_x.append(data['up_x'])
                all_up_y.append(data['up_y'])
    
    return all_down_x, all_down_y, all_up_x, all_up_y

def interpolate_data(x_data, y_data, new_x):
    interpolated_y_data = []
    for x, y in zip(x_data, y_data):
        f = interp1d(x, y, kind='linear', bounds_error=False, fill_value='extrapolate')
        interpolated_y_data.append(f(new_x))
    return np.array(interpolated_y_data)

def average_data(data_list):
    return np.mean(data_list, axis=0), np.std(data_list, axis=0)

def plot_data(avg_down_x, avg_down_y, std_down_y, avg_up_x, avg_up_y, std_up_y):
    fig, ax = plt.subplots()
    plt.subplots_adjust(bottom=0.2)

    plt.xlabel("travel, mm")
    plt.ylabel("weight, g")
    plt.grid(color='green', linestyle='--', linewidth=0.5)

    ax.plot(avg_down_x, avg_down_y, lw=1, label='Down')
    ax.fill_between(avg_down_x, avg_down_y - std_down_y, avg_down_y + std_down_y, alpha=0.2)
    ax.plot(avg_up_x, avg_up_y, lw=1, label='Up')
    ax.fill_between(avg_up_x, avg_up_y - std_up_y, avg_up_y + std_up_y, alpha=0.2)
    
    plt.legend()
    
    plt.savefig('results/averaged_plot.png', dpi=300)
    plt.savefig('results/averaged_plot.svg', dpi=300)

def save_averaged_data(file_path, avg_down_x, avg_down_y, std_down_y, avg_up_x, avg_up_y, std_up_y):
    data = {
        "avg_down_x": [round(val, 4) for val in avg_down_x],
        "avg_down_y": [round(val, 4) for val in avg_down_y],
        "std_down_y": [round(val, 4) for val in std_down_y],
        "avg_up_x": [round(val, 4) for val in avg_up_x],
        "avg_up_y": [round(val, 4) for val in avg_up_y],
        "std_up_y": [round(val, 4) for val in std_up_y]
    }
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

def main():
    directory = 'results'

    all_down_x, all_down_y, all_up_x, all_up_y = load_data(directory)
    
    min_x = max([min(x) for x in all_down_x])
    max_x = min([max(x) for x in all_down_x])
    new_x = np.linspace(min_x, max_x, num=200)
    
    interpolated_down_y = interpolate_data(all_down_x, all_down_y, new_x)
    interpolated_up_y = interpolate_data(all_up_x, all_up_y, new_x)
    
    avg_down_y, std_down_y = average_data(interpolated_down_y)
    avg_up_y, std_up_y = average_data(interpolated_up_y)
    
    plot_data(new_x, avg_down_y, std_down_y, new_x, avg_up_y, std_up_y)

    # Сохраняем усредненные данные в JSON с округлением до 4 знаков после запятой
    save_averaged_data('results/averaged_data.json', new_x, avg_down_y, std_down_y, new_x, avg_up_y, std_up_y)

if __name__ == "__main__":
    main()
