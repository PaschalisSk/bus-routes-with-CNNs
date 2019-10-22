import pandas as pd

b3_df = pd.read_csv('../../output/paths compare/comp3.csv')
b5_df = pd.read_csv('../../output/paths compare/comp5.csv')
b7_df = pd.read_csv('../../output/paths compare/comp7.csv')
all_df = pd.concat([b3_df, b5_df, b7_df], axis=0)
b3_df['my_route_wait_time'] = (b3_df['my_route_duration'] / b3_df['buses'])/2
b3_df['gtfs_route_wait_time'] = (b3_df['gtfs_route_duration'] / b3_df['buses'])/2
b5_df['my_route_wait_time'] = (b5_df['my_route_duration'] / b5_df['buses'])/2
b5_df['gtfs_route_wait_time'] = (b5_df['gtfs_route_duration'] / b5_df['buses'])/2
b7_df['my_route_wait_time'] = (b7_df['my_route_duration'] / b7_df['buses'])/2
b7_df['gtfs_route_wait_time'] = (b7_df['gtfs_route_duration'] / b7_df['buses'])/2
all_df['my_route_wait_time'] = (all_df['my_route_duration'] / all_df['buses'])/2
all_df['gtfs_route_wait_time'] = (all_df['gtfs_route_duration'] / all_df['buses'])/2
b3_mean = b3_df.mean(0, numeric_only=True).round(0).astype(int).apply(str)
b5_mean = b5_df.mean(0, numeric_only=True).round(0).astype(int).apply(str)
b7_mean = b7_df.mean(0, numeric_only=True).round(0).astype(int).apply(str)
all_mean = all_df.mean(0, numeric_only=True).round(0).astype(int).apply(str)
b3_sem = b3_df.sem(0, numeric_only=True).map(lambda x: '{0:.1f}'.format(x))
b5_sem = b5_df.sem(0, numeric_only=True).map(lambda x: '{0:.1f}'.format(x))
b7_sem = b7_df.sem(0, numeric_only=True).map(lambda x: '{0:.1f}'.format(x))
all_sem = all_df.sem(0, numeric_only=True).map(lambda x: '{0:.1f}'.format(x))
b3_comb = b3_mean + r' $\pm$ ' + b3_sem
b5_comb = b5_mean + r' $\pm$ ' + b5_sem
b7_comb = b7_mean + r' $\pm$ ' + b7_sem
all_comb = all_mean + r' $\pm$ ' + all_sem
comp = pd.concat([b3_comb, b5_comb, b7_comb, all_comb], axis=1)
print(comp.to_latex(escape=False))
print('deb')
