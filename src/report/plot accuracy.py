import glob
import pandas as pd
import os
from pathlib import Path
import matplotlib.pyplot as plt

plt.style.use('ggplot')
params = {
    'backend': 'ps',
    #'text.latex.preamble': ['\usepackage{gensymb}'],
    'axes.labelsize': 22, # fontsize for x and y labels (was 10)
    'axes.titlesize': 14,
    'font.size': 14, # was 10
    'legend.fontsize': 10, # was 10
    'xtick.labelsize': 14,
    'ytick.labelsize': 16,
    'text.usetex': True,
    'font.family': 'serif'
}
plt.rcParams.update(params)

metrics_df = pd.read_csv('../../output/unet thresholds/metrics.csv')

fig, axs = plt.subplots(nrows=2, ncols=2, constrained_layout=True, figsize=(10, 10))

for i, metric in enumerate(['precision', 'recall', 'f1', 'binary_accuracy']):
    ax = axs.flat[i]
    ax.plot(metrics_df['threshold'].values, metrics_df[metric].values)
    ax.set_xlim(0.5, 0.0)
    ax.set_xlabel('Threshold')
    if metric == 'precision':
        ylabel = 'Precision'
    elif metric == 'recall':
        ylabel = 'Recall'
    elif metric == 'binary_accuracy':
        ylabel = 'Accuracy'
    elif metric == 'f1':
        ylabel = r'$F_1$ score'

    ax.set_ylabel(ylabel)

#plt.show()
plt.savefig('D:/Google Drive/UoE/Thesis/figures/exp/metricsthr.eps', bbox_inches='tight', dpi=1000)
print('deb')
