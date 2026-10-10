"""Two exploratory figures; reference figure can run before prediction counts."""
from __future__ import annotations
import argparse
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, TwoSlopeNorm
from matplotlib.ticker import FixedLocator, FuncFormatter, NullFormatter
import explore_sec33_reference_patch_types as b

plt.rcParams.update({'font.family':'SimHei','axes.unicode_minus':False,'font.size':10,
                     'svg.fonttype':'path','savefig.dpi':160})
COLORS={1:'#3479A8',2:'#D78530'}


def save(fig,name):
    b.FIG.mkdir(parents=True,exist_ok=True)
    for ext in ['png','svg']:fig.savefig(b.FIG/(name+'.'+ext),bbox_inches='tight')
    plt.close(fig)


def features():
    f=b.read(b.PROC/'frozen_patch_assignments.csv');f=f[f.crop.ne('other')]
    reps=b.read(b.SUM/'representative_patches.csv')
    fig=plt.figure(figsize=(16,10));gs=fig.add_gridspec(2,12,height_ratios=[1,1.2],hspace=.4,wspace=.95)
    for i,(m,title) in enumerate([('AREA','面积 AREA（ha，对数轴）'),('SHAPE','形状指数 SHAPE（对数轴）'),('ENN','同类最近邻距离 ENN（m，对数轴）')]):
        ax=fig.add_subplot(gs[0,4*i:4*i+4]);groups=[];ticks=[]
        for crop in ['corn','soybean']:
            for typ in [1,2]:
                groups.append(f[(f.crop==crop)&(f.spatial_type==typ)][m].values)
                ticks.append(('玉米' if crop=='corn' else '大豆')+f' T{typ}')
        bp=ax.boxplot(groups,showfliers=False,patch_artist=True,tick_labels=ticks,whis=(5,95))
        for patch,t in zip(bp['boxes'],[1,2,1,2]):patch.set_facecolor(COLORS[t]);patch.set_alpha(.6)
        ax.set_yscale('log');ax.set_title(title);ax.grid(axis='y',alpha=.2)
        ticks={'AREA':[.1,1,10,100],'SHAPE':[1,1.25,1.5,2,2.5],'ENN':[60,100,200,300]}[m]
        ax.yaxis.set_major_locator(FixedLocator(ticks));ax.yaxis.set_major_formatter(FuncFormatter(lambda x,pos:f'{x:g}'))
        ax.yaxis.set_minor_formatter(NullFormatter())
    for i,row in enumerate(reps.itertuples()):
        ax=fig.add_subplot(gs[1,3*i:3*i+3]);r=np.load(b.record(b.PROC/f'reference_full_{row.target}.npz'))
        pad=4;y0=max(0,row.row_min-pad);y1=min(2560,row.row_max+pad+1);x0=max(0,row.col_min-pad);x1=min(2560,row.col_max+pad+1)
        lab=r['label'][y0:y1,x0:x1];ids=r['ids'][y0:y1,x0:x1]
        ax.imshow(lab,cmap=ListedColormap(['#99bc73','#dddddd','#e5bb73']),vmin=0,vmax=2,interpolation='nearest',alpha=.45)
        mask=np.ma.masked_where(ids!=row.PID,np.ones_like(ids));ax.imshow(mask,cmap=ListedColormap([COLORS[row.spatial_type]]),vmin=0,vmax=1,interpolation='nearest')
        ax.set_aspect('equal');ax.set_title(f'{"玉米" if row.crop=="corn" else "大豆"} T{row.spatial_type} · {row.site}站 PID {row.PID}\nAREA {row.AREA:.2f} ha；SHAPE {row.SHAPE:.2f}\nENN {row.ENN:.2f} m',fontsize=10)
        ax.set_xlabel('参考标签列（局部视窗，每像元30 m）');ax.set_ylabel('参考标签行')
    fig.suptitle('参考作物斑块的两种空间类型：指标分布与真实代表斑块',fontsize=17,y=.99)
    fig.text(.5,.005,'四站、两作物共同分型；箱体为四分位范围，须为5%—95%；代表斑块按参考特征距簇中心最近选取。\n类型编号按中心面积排序；背景浅绿为玉米、浅黄为大豆、浅灰为其他，深色为选中斑块。\n局部视窗仅用于显示完整斑块，视窗范围不同，不是重新切片计算景观指标。',ha='center',fontsize=10)
    save(fig,'01_type_features_and_reference_patches')
    b.check('feature figure reference rows',len(f)==149234 and len(reps)==4)
    b.finish('plot_features')


def errors():
    d=b.read(b.SUM/'type_error_summary.csv')
    z=d[d.region.isin(['boundary','interior'])].copy()
    rows=[]
    for t in b.SITES:
        for s in b.SITES:
            if s!=t:rows.append((s,t))
    cols=[(typ,region,field) for typ in [1,2] for region in ['boundary','interior'] for field in ['other_crop_rate','other_rate']]
    finite=z[['delta_other_crop_rate_mean','delta_other_rate_mean']].to_numpy();limit=float(np.nanmax(abs(finite)))
    fig,axes=plt.subplots(3,2,figsize=(16,14),sharex=True,sharey=True)
    plotted=[]
    for mi,m in enumerate(b.MODELS):
        for ci,crop in enumerate(['corn','soybean']):
            ax=axes[mi,ci];a=np.full((12,8),np.nan)
            for ri,(source,target) in enumerate(rows):
                for co,(typ,region,field) in enumerate(cols):
                    r=z[(z.model==m)&(z.crop==crop)&(z.source==source)&(z.target==target)&(z.spatial_type==typ)&(z.region==region)]
                    b.require(len(r)==1,'one condition per plot cell');v=r.iloc[0]['delta_'+field+'_mean'];a[ri,co]=v
                    plotted.append(dict(model=m,crop=crop,source=source,target=target,spatial_type=typ,region=region,metric=field,value=v))
                    ax.text(co,ri,f'{v:.2f}',ha='center',va='center',fontsize=8,color='white' if abs(v)>limit*.55 else '#222222')
            im=ax.imshow(a,cmap='RdBu_r',norm=TwoSlopeNorm(0,vmin=-limit,vmax=limit),aspect='auto')
            ax.set_yticks(range(12),[b.SITES[s]+'→'+b.SITES[t] for s,t in rows]);ax.tick_params(labelleft=True,labelbottom=True)
            ax.set_xticks(range(8),[f'T{t}\n{"边界" if r=="boundary" else "内部"}\n→{"另一作物" if f=="other_crop_rate" else "其他类"}' for t,r,f in cols],fontsize=8)
            ax.set_title(['ConvGRU','3D U-Net','U-TAE'][mi]+' · '+['玉米','大豆'][ci],fontsize=13)
            for y in [2.5,5.5,8.5]:ax.axhline(y,color='black',lw=.8)
            ax.axvline(3.5,color='black',lw=1.2)
    fig.subplots_adjust(left=.06,right=.91,bottom=.09,top=.93,hspace=.45,wspace=.15)
    ca=fig.add_axes([.93,.22,.015,.55]);fig.colorbar(im,cax=ca,label='定向错误率增量（跨站五次均值减本站，原尺度）')
    fig.suptitle('相同空间类型中的边界、内部新增错误与错分去向',fontsize=18,y=.975)
    fig.text(.5,.015,'边界：0<d≤1像元；内部：d>1像元。分母为同目标站、同类型、同位置的真实作物像元数。\n每格为五次分别计算后的均值，完整逐次方向与波动见结果表；负值保留；图中数值不是ΔF1。',ha='center',fontsize=10)
    save(fig,'02_type_location_directed_error_increments');b.write(pd.DataFrame(plotted),'figure2_plot_data')
    b.check('error figure cells',len(plotted)==576)
    b.finish('plot_errors')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['features','errors']);globals()[p.parse_args().stage]()
