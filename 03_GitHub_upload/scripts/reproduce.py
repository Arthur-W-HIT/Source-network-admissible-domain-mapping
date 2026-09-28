"""Verify supporting data and regenerate numerical comparisons and example plots."""
from pathlib import Path
import hashlib,json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reproduced';OUT.mkdir(exist_ok=True)
manifest=ROOT/'manifest.json'
if manifest.exists():
    for entry in json.loads(manifest.read_text(encoding='utf-8'))['files']:
        assert hashlib.sha256((ROOT/entry['path']).read_bytes()).hexdigest()==entry['sha256'],entry['path']

scheme=pd.read_csv(ROOT/'data/scheme_metrics.csv')
scenario=pd.read_csv(ROOT/'data/scenario_metrics.csv')
assert len(scenario)==1728 and len(scheme)==5184
assert scenario.scenario_id.is_unique
counts=scenario.groupby('stratum').size().to_dict()
assert counts=={'main_reference':12,'narrow_sensitivity':420,'historical_extension':1296},counts
main=scheme[scheme.stratum=='main_reference']
coverage=main.groupby('scheme').coupled_coverage.mean().reindex(['S1','S2a','S2b'])*100
assert np.allclose(coverage,[90.3229166667,92.2916666667,99.3645833333],atol=0.005),coverage
main_scenarios=scenario[scenario.stratum=='main_reference']
assert abs(main_scenarios.add31.mean()*100-9.0416666667)<0.005
assert abs(main_scenarios['none'].mean()*100-0.6354166667)<0.005
grouped=scheme.groupby(['stratum','scheme']).agg(coverage=('coupled_coverage','mean'),source_coverage=('source_coverage','mean'),max_heat_MW=('max_coupled_Q_MW','mean'),loss_per_heat=('mean_min_deltaP_per_Q','mean'))
grouped.to_csv(OUT/'grouped_results.csv')
coverage.to_csv(OUT/'reference_coverage_percent.csv',header=['coverage_percent'])
scenario.groupby(['load_frac','T_supply_max_C','T_return_C','winner']).size().to_csv(OUT/'interface_selection_counts.csv',header=['count'])
selected={}
for sid,g in scheme.groupby('scenario_id',sort=False):
    candidates=g.copy()
    for col,maximize in [('coupled_coverage',True),('max_coupled_Q_MW',True),('source_coverage',True),('mean_min_deltaP_per_Q',False)]:
        values=candidates[col].to_numpy()
        best=np.nanmax(values) if maximize else np.nanmin(values)
        candidates=candidates[np.isclose(values,best,rtol=1e-9,atol=1e-12)]
    selected[sid]='|'.join(sorted(candidates.scheme))
for row in scenario.itertuples():
    assert selected[row.scenario_id]==row.winner,(row.scenario_id,selected[row.scenario_id],row.winner)
pd.Series(selected,name='winner').rename_axis('scenario_id').to_csv(OUT/'recomputed_selection.csv')
labels={'S1':'C1','S2a':'C2','S2b':'C3'}
colors={'S1':'#4477aa','S2a':'#ee9933','S2b':'#228833'}
plt.rcParams.update({'font.family':'DejaVu Serif','font.size':10,'pdf.fonttype':42})
fig,axes=plt.subplots(2,2,figsize=(10,7),layout='constrained')
for ax,key,title in zip(axes.flat[:2],['load_frac','T_supply_max_C'],['Coverage by load','Coverage by supply-temperature ceiling']):
    for s,g in scheme.groupby('scheme'):
        means=g.groupby(key).coupled_coverage.mean()*100
        ax.plot(means.index,means.values,'o-',label=labels[s],color=colors[s])
    ax.set(title=title,xlabel=key,ylabel='Mean demand coverage (%)');ax.legend()
means=scheme.groupby('scheme').agg(source=('source_coverage','mean'),coupled=('coupled_coverage','mean')).reindex(labels)
x=np.arange(3)
axes[1,0].bar(x,100*(1-means.source),label='Outside source coverage')
axes[1,0].bar(x,100*(means.source-means.coupled),bottom=100*(1-means.source),label='Additional coupled restriction')
axes[1,0].set(xticks=x,xticklabels=list(labels.values()),ylabel='Mean uncovered demand (%)');axes[1,0].legend(fontsize=8)
w=scenario.groupby('winner').size().reindex(labels,fill_value=0)
axes[1,1].bar(list(labels.values()),w.values,color=[colors[s] for s in labels]);axes[1,1].set(ylabel='Selected scenarios',title='Interface selection (all 1728 conditions)')
fig.savefig(OUT/'all_scenario_overview.pdf');fig.savefig(OUT/'all_scenario_overview.png',dpi=160);plt.close(fig)

samples=pd.read_csv(ROOT/'figure_data/continuous_source_plot_samples.csv')
fig,ax=plt.subplots(figsize=(6,4),layout='constrained')
for s,g in samples.groupby('scheme'):
    q=g.Q_high_MW+g.Q_low_MW
    ax.scatter(q,g.P_el_MW,s=1,alpha=.35,label=labels.get(s,s),color=colors.get(s))
ax.set(xlabel='Heating output (MW)',ylabel='Electric output (MW)');ax.legend(markerscale=5)
fig.savefig(OUT/'source_domain_samples.pdf');plt.close(fig)
v=pd.read_csv(ROOT/'figure_data/violation_strength_summary_v14.csv')
fig,ax=plt.subplots(figsize=(5,3.5),layout='constrained')
ax.bar([labels[s] for s in v.scheme],v.mean_Phi,color=[colors[s] for s in v.scheme]);ax.set(ylabel='Weighted mean normalized violation')
fig.savefig(OUT/'weighted_violation_summary.pdf');plt.close(fig)

report={'scenario_counts':counts,'reference_coverage_percent':coverage.to_dict(),'reference_additional_C3_percent':main_scenarios.add31.mean()*100,'reference_jointly_uncovered_percent':main_scenarios['none'].mean()*100,'all_scenario_coverage_percent':(scheme.groupby('scheme').coupled_coverage.mean()*100).to_dict(),'physical_simulations_run':False}
(OUT/'verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2))
