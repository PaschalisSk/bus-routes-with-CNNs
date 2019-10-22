import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

params = {
    'backend': 'ps',
    #'text.latex.preamble': ['\usepackage{gensymb}'],
    'axes.labelsize': 14, # fontsize for x and y labels (was 10)
    'axes.titlesize': 14,
    'font.size': 14, # was 10
    'legend.fontsize': 14, # was 10
    'xtick.labelsize': 14,
    'ytick.labelsize': 14,
    'text.usetex': True,
    'font.family': 'serif'
}
plt.rcParams.update(params)
# matplotlib.rcParams['text.usetex'] = True
# matplotlib.rcParams['text.latex.preview'] = True
# matplotlib.rcParams['text.fontsize'] = 15
# matplotlib.rcParams['font.family'] = 'serif'
# matplotlib.rcParams['font.size'] = 20

results_csv = '../../output/routes_data_analysis/stops_info.csv'
results_pd = pd.read_csv(results_csv)

training_imgs_dir = '../../data/datasets/routes_256/train'
training_imgs = [img.name for img in Path(training_imgs_dir).glob('*.jpg')]

results_pd = results_pd[results_pd['img'].isin(training_imgs)]

# ### -------- DRAW PLOT ------------- ###
# plt.style.use('ggplot')
# fig, ax = plt.subplots()
# ax.xaxis.set_label_text(r'Average Bus Stop Distance $(m)$', fontsize=16)
# ax.yaxis.set_label_text(r'Routes', fontsize=16)
# plt.hist(results_pd['avg_stop_distance'].values, 40)
# plt.gca().set_xlim(left=0)
# plt.savefig('D:/Google Drive/UoE/Thesis/figures/meth/stopanalplot.eps', bbox_inches='tight', dpi=1000)
# ### -------- DRAW PLOT ------------- ###
# desc_series = results_pd['avg_stop_distance'].describe()
# desc_series.to_csv('../../output/routes_data_analysis/describe.csv')
print('deb')
