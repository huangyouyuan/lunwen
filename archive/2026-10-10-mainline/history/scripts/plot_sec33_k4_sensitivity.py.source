"""Two candidate figures for the saved K4 sensitivity; no fitting or inference."""
import argparse
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap,TwoSlopeNorm
from matplotlib.ticker import FixedLocator,FuncFormatter,NullFormatter
import explore_sec33_k4_sensitivity as b

plt.rcParams.update({'font.family':'SimHei','axes.unicode_minus':False,'font.size':10,'svg.fonttype':'path','savefig.dpi':170})
COLORS=['#878787','#bda86b','#3877ae','#cb6639']


def save(fig,name):
    b.FIG.mkdir(parents=True,exist_ok=True)
    for ext in ['png','svg']:fig.savefig(b.FIG/(name+'.'+ext),bbox_inches='tight')
    plt.close(fig)


def features():
    b.verify_selection();f=b.read(b.PROC/'selected_assignments.csv')
    reps=b.read(b.SUM/'representative_patches.csv');reps=reps[reps.selection_domain.eq('crop')]
    fig=plt.figure(figsize=(18,13));gs=fig.add_gridspec(3,12,height_ratios=[.9,1,1],hspace=.52,wspace=.9)
    distribution=[]
    for i,(metric,title,ticks) in enumerate([('AREA','AREA（ha）',[.1,1,10,100]),('SHAPE','SHAPE',[1,1.5,2,3]),('ENN','ENN（m）',[60,100,200,500])]):
        ax=fig.add_subplot(gs[0,i*4:i*4+4]);vals=[];labels=[]
        for crop in b.CROPS:
            for typ in b.TYPES:
                a=f[f.crop.eq(crop)&f.spatial_type.eq(typ)][metric].to_numpy()
                vals.append(a);labels.append(('玉米' if crop=='corn' else '大豆')+'\n'+typ.replace('K4-',''))
                qs=np.quantile(a,[.05,.25,.5,.75,.95]);distribution.append(dict(crop=crop,spatial_type=typ,metric=metric,q05=qs[0],q25=qs[1],median=qs[2],q75=qs[3],q95=qs[4]))
        bp=ax.boxplot(vals,showfliers=False,patch_artist=True,whis=(5,95),tick_labels=labels)
        for p,c in zip(bp['boxes'],COLORS*2):p.set_facecolor(c);p.set_alpha(.65)
        ax.set_yscale('log');ax.yaxis.set_major_locator(FixedLocator(ticks));ax.yaxis.set_major_formatter(FuncFormatter(lambda x,pos:f'{x:g}'));ax.yaxis.set_minor_formatter(NullFormatter())
        ax.set_title(title+' · 对数轴');ax.grid(axis='y',alpha=.2);ax.axvline(4.5,color='#aaaaaa',lw=.8)
    for ci,crop in enumerate(b.CROPS):
        for ti,typ in enumerate(b.TYPES):
            rr=reps[reps.crop.eq(crop)&reps.spatial_type.eq(typ)].iloc[0]
            ax=fig.add_subplot(gs[ci+1,3*ti:3*ti+3])
            with np.load(b.record(b.BASE/f'reference_full_{rr.target}.npz')) as r:
                pad=4;y0=max(0,int(rr.row_min)-pad);y1=min(2560,int(rr.row_max)+pad+1);x0=max(0,int(rr.col_min)-pad);x1=min(2560,int(rr.col_max)+pad+1)
                lab=r['label'][y0:y1,x0:x1];ids=r['ids'][y0:y1,x0:x1]
            ax.imshow(lab,cmap=ListedColormap(['#97b96b','#dddddd','#e4b768']),vmin=0,vmax=2,interpolation='nearest',alpha=.5)
            ax.imshow(np.ma.masked_where(ids!=rr.PID,np.ones_like(ids)),cmap=ListedColormap([COLORS[ti]]),vmin=0,vmax=1,interpolation='nearest')
            b.check('representative full patch pixels '+crop+typ,int((ids==rr.PID).sum())==rr.reference_pixels)
            ax.set_title(f'{"玉米" if crop=="corn" else "大豆"} · {typ} · {rr.site}站 PID {rr.PID}\nAREA {rr.AREA:.2f} ha；SHAPE {rr.SHAPE:.2f}；ENN {rr.ENN:.2f} m',fontsize=9)
            ax.set_xlabel('局部视窗列（每像元30 m）',fontsize=9);ax.set_ylabel('局部视窗行',fontsize=9)
    fig.suptitle('既有K=4类型的参考特征与完整参考作物斑块',fontsize=18,y=.98)
    fig.text(.5,.025,'类型统一标为K4-C1—C4；上图按斑块统计，箱体为25%—75%，须为5%—95%。\n代表斑块只按参考特征距既有中心最近选取；深色突出完整斑块，浅绿/浅黄/灰为玉米/大豆/其他参考标签。\n视窗只用于显示周围标签，未重新切片；不同视窗的显示比例不同。',ha='center',fontsize=10)
    save(fig,'01_K4_features_and_reference_patches');b.write(pd.DataFrame(distribution),'figure1_distribution_data');b.record(__file__);b.finish('plot_features')


def errors():
    d=b.read(b.SUM/'C4_minus_C3_summary.csv')
    columns=[('all','C4_minus_C3_leakage_mean','全斑块\n跨站绝对率差'),('all','C4_minus_C3_delta_leakage_mean','全斑块\n漏分增量差'),
             ('boundary','C4_minus_C3_delta_leakage_mean','边界\n漏分增量差'),('interior','C4_minus_C3_delta_leakage_mean','内部\n漏分增量差'),
             ('all','C4_minus_C3_delta_other_crop_rate_mean','全斑块\n→另一作物增量差'),('all','C4_minus_C3_delta_other_rate_mean','全斑块\n→其他类增量差')]
    paths=[(s,t) for t in b.old.SITES for s in b.old.SITES if s!=t]
    data=[]
    for m in b.old.MODELS:
        for c in b.CROPS:
            for s,t in paths:
                for col,(reg,field,label) in enumerate(columns):
                    z=d[d.model.eq(m)&d.crop.eq(c)&d.source.eq(s)&d.target.eq(t)&d.region.eq(reg)]
                    b.old.require(len(z)==1,'one condition per plotted cell');r=z.iloc[0]
                    data.append(dict(model=m,crop=c,source=s,target=t,region=reg,metric=field,column=col,value=r[field],
                        direction=r[field.replace('_mean','_direction')]))
    p=pd.DataFrame(data);lim=float(p.value.abs().max());fig,axes=plt.subplots(3,2,figsize=(15,13))
    for mi,m in enumerate(b.old.MODELS):
        for ci,c in enumerate(b.CROPS):
            ax=axes[mi,ci];v=p[p.model.eq(m)&p.crop.eq(c)];arr=v.value.to_numpy().reshape(12,6)
            im=ax.imshow(arr,cmap='RdBu_r',norm=TwoSlopeNorm(0,vmin=-lim,vmax=lim),aspect='auto')
            for ri in range(12):
                for co in range(6):
                    cell=v.iloc[ri*6+co];symbol='●' if cell.direction in ['all_positive','all_negative'] else ''
                    ax.text(co,ri,f'{cell.value:.2f}{symbol}',ha='center',va='center',fontsize=8,color='white' if abs(cell.value)>.6*lim else '#222222')
            ax.set_xticks(range(6),[v[2] for v in columns],fontsize=8)
            ax.set_yticks(range(12),[b.old.SITES[s]+'→'+b.old.SITES[t] for s,t in paths])
            for y in [2.5,5.5,8.5]:ax.axhline(y,color='black',lw=.7)
            ax.axvline(.5,color='black',lw=1);ax.axvline(3.5,color='black',lw=.7)
            ax.set_title(['ConvGRU','3D U-Net','U-TAE'][mi]+' · '+['玉米','大豆'][ci],fontsize=13)
    fig.subplots_adjust(left=.06,right=.89,top=.93,bottom=.105,hspace=.38,wspace=.2)
    ca=fig.add_axes([.92,.23,.017,.53]);fig.colorbar(im,cax=ca,label='K4-C4减K4-C3（原尺度错误率之差）')
    fig.suptitle('主要作物面积内部：C4相对C3的绝对漏分与跨站增量',fontsize=17,y=.98)
    fig.text(.5,.025,'每格为同模型、源站、目标站和作物的五次对照均值；●表示五次严格同向，不是显著性标记。\n第一列比较跨站绝对漏分率；其余列比较“跨站减本站”的增量。边界：(0,1]像元；内部：>1像元。\n负值表示C4更低；两类是不同参考斑块集合，未作斑块一一配对；完整本站率、支持量和五次值见表。',ha='center',fontsize=10)
    save(fig,'02_C4_minus_C3_errors');b.write(p,'figure2_plot_data')
    b.check('432 plotted cells',len(p)==432);b.record(__file__);b.finish('plot_errors')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['features','errors']);globals()[p.parse_args().stage]()
