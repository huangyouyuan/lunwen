#!/usr/bin/env python3
"""Three exploratory figures only; source values and five-run ranges are auditable."""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import explore_sec33_crop_spatial_context as m
import figstyle as fs

SITE=dict(zip(m.SITES,'ABCD'))
COLORS=fs.MODEL_COLORS
LABELS=fs.MODEL_LABELS
SOURCE_COLORS={'iw_2023':'#2864A5','iw2_2023':'#C34339','ida_2023':'#27805D','il_2023':'#9460A1'}
X=np.array([0,1,2,3,4,5,7])
BT=['(0,1]','(1,2]','(2,3]','(3,4]','(4,5]','(5,6]','>6']


def style():
    fs.setup()
    plt.rcParams.update({'font.size':11,'axes.labelsize':11,'axes.titlesize':13,
                         'xtick.labelsize':10,'ytick.labelsize':10,'legend.fontsize':10,
                         'savefig.dpi':170,'savefig.pad_inches':.14})


def clean(ax):
    ax.spines[['top','right']].set_visible(False)
    ax.grid(axis='y',color='#DDDDDD',linewidth=.5,zorder=0)


def save(fig,name):
    m.FIG.mkdir(parents=True,exist_ok=True)
    fig.savefig(m.FIG/(name+'.png'),bbox_inches='tight')
    fig.savefig(m.FIG/(name+'.svg'),bbox_inches='tight')
    plt.close(fig)


def weights():
    w=m.read(m.SUM/'distance_common_weights.csv')
    g=m.read(m.SUM/'weighted_crop_gap_summary.csv')
    rows=[]
    fig,axs=plt.subplots(3,4,figsize=(17,11))
    fig.subplots_adjust(left=.07,right=.99,bottom=.13,top=.87,hspace=.48,wspace=.30)
    for ci,t in enumerate(m.SITES):
        ax=axs[0,ci];z=w[w.target.eq(t)].set_index('band').loc[list(m.BANDS)]
        ax.bar(X-.17,z.corn_share,.32,color=fs.CLASS_COLORS[1],label='玉米')
        ax.bar(X+.17,z.soybean_share,.32,color=fs.CLASS_COLORS[3],label='大豆')
        ax.set_xticks(X,BT,rotation=35);ax.set_ylim(0,.32);ax.set_title('目标站 '+SITE[t])
        ax.set_xlabel('距类别交界的距离带／像元')
        for b,r in z.iterrows():rows.append(dict(panel='distribution',target=t,band=b,corn=r.corn_share,soybean=r.soybean_share))
        z=g[g.target.eq(t)].drop_duplicates('model').set_index('model')
        ax=axs[1,ci];ax.axhline(0,color='black',lw=.7)
        for mi,model in enumerate(m.MODELS):
            r=z.loc[model];a=r.within_full_original_gap;b=r.within_common_weighted_gap
            ax.plot([mi,mi],[a,b],color=COLORS[model],lw=2)
            ax.scatter(mi,a,facecolors='white',edgecolors=COLORS[model],s=54,zorder=3)
            ax.scatter(mi,b,color=COLORS[model],marker='s',s=35,zorder=4)
            rows.append(dict(panel='within_gap',target=t,model=model,original=a,weighted=b))
        ax.set_xticks(range(3),[LABELS[x] for x in m.MODELS],rotation=15)
        ax.set_ylim(-.008,.031);ax.set_title('本站：共同权重前后')
        ax=axs[2,ci];ax.axhline(0,color='black',lw=.7)
        sources=[s for s in m.SITES if s!=t]
        for si,s in enumerate(sources):
            z=g[g.target.eq(t)&g.source.eq(s)].set_index('model')
            for mi,model in enumerate(m.MODELS):
                r=z.loc[model];a=r.cross_full_original_gap_mean;b=r.cross_common_weighted_gap_mean;x=si+(mi-1)*.21
                ax.plot([x,x],[a,b],color=COLORS[model],lw=2)
                ax.scatter(x,a,facecolors='white',edgecolors=COLORS[model],s=40,zorder=3)
                ax.scatter(x,b,color=COLORS[model],marker='s',s=28,zorder=4)
                rows.append(dict(panel='cross_gap',target=t,source=s,model=model,original=a,weighted=b))
        ax.set_xticks(range(3),[SITE[s]+'源' for s in sources]);ax.set_ylim(-.05,.145)
        ax.set_title('跨站：五次均值')
    axs[0,0].set_ylabel('该作物像元占比')
    for row in [1,2]:axs[row,0].set_ylabel('大豆漏分率 − 玉米漏分率\n原尺度差值')
    for ax in axs.flat:clean(ax)
    fig.suptitle('距离分布不同，并不能替代相同距离条件下的错误比较',fontsize=18,y=.975)
    handles=[Line2D([],[],color=fs.CLASS_COLORS[1],lw=6,label='玉米像元分布'),Line2D([],[],color=fs.CLASS_COLORS[3],lw=6,label='大豆像元分布')]
    handles += [Line2D([],[],color=COLORS[x],lw=2,label=LABELS[x]) for x in m.MODELS]
    handles += [Line2D([],[],marker='o',mfc='white',mec='black',ls='',label='各自原分布'),Line2D([],[],marker='s',color='black',ls='',label='共同距离权重')]
    fig.legend(handles=handles,ncol=7,loc='upper center',bbox_to_anchor=(.5,.938),frameon=False)
    fig.text(.07,.045,'共同权重＝同站两作物在共同支持七带内归一分布的算术平均；本次四站覆盖率均为100%。\n差值为正表示大豆漏分率更高；这不是调整后的F1。>6为开放区间，与前六带留有间隔。',fontsize=11)
    m.save(pd.DataFrame(rows),'figure1_plot_data');save(fig,'01_distance_distribution_common_weights')


def boundary():
    per=m.read(m.PROC/'boundary_asymmetry_per_prediction.csv')
    per=per[per.boundary_type.eq('corn_soybean')&per.band.eq(m.BANDS[0])]
    summary=m.read(m.SUM/'boundary_asymmetry_summary.csv')
    summary=summary[summary.boundary_type.eq('corn_soybean')&summary.band.eq(m.BANDS[0])]
    rows=[]
    fig,axs=plt.subplots(3,4,figsize=(17,10),sharex=True)
    fig.subplots_adjust(left=.10,right=.99,bottom=.13,top=.87,hspace=.30,wspace=.30)
    for mi,model in enumerate(m.MODELS):
        for ti,t in enumerate(m.SITES):
            ax=axs[mi,ti];src=[s for s in m.SITES if s!=t]
            z=summary[summary.target.eq(t)&summary.model.eq(model)].set_index('source')
            baseline=float(z.within_rate_asymmetry.iloc[0]);ax.axvline(0,color='black',lw=.7)
            ax.axvline(baseline,color=COLORS[model],lw=1.4,ls='--')
            for si,s in enumerate(src):
                v=per[per.model.eq(model)&per.target.eq(t)&per.source.eq(s)&per.kind.eq('cross')].sort_values('fold')
                stat=m.strict_stats(v.rate_asymmetry,v.fold);r=z.loc[s]
                m.close_values('figure2 mean '+str((model,s,t)),stat['mean'],r.cross_rate_asymmetry_mean)
                ax.plot([stat['min'],stat['max']],[si,si],color=COLORS[model],lw=1.5)
                ax.scatter(v.rate_asymmetry,np.full(5,si),color=COLORS[model],s=14,alpha=.45,zorder=3)
                ax.scatter(stat['mean'],si,color=COLORS[model],marker='D',s=40,zorder=4)
                rows.append(dict(model=model,target=t,source=s,within=baseline,mean=stat['mean'],minimum=stat['min'],maximum=stat['max'],delta=r.delta_rate_asymmetry,five_delta_direction=r.delta_rate_asymmetry_direction))
            ax.set_yticks(range(3),[SITE[s]+'源' for s in src]);ax.set_ylim(2.6,-.6);ax.set_xlim(-.28,.28)
            if mi==0:ax.set_title('目标站 '+SITE[t])
            if ti==0:ax.set_ylabel(LABELS[model]+'\n来源')
            if mi==2:ax.set_xlabel('大豆→玉米率 − 玉米→大豆率')
            clean(ax)
    fig.suptitle('同类玉米—大豆边界附近：错分不对称随模型与来源改变',fontsize=18,y=.973)
    fig.legend(handles=[Line2D([],[],color='black',ls='--',label='本站不对称值'),Line2D([],[],color='black',marker='D',ls='',label='跨站五次均值'),Line2D([],[],color='gray',marker='o',lw=1,label='五次逐值及最小—最大范围')],ncol=3,loc='upper center',bbox_to_anchor=(.5,.933),frameon=False)
    fig.text(.10,.047,'仅使用已有直接边界两侧像元，均在(0,1]带；正值表示大豆→玉米率较高。分母分别为同条件真实大豆和真实玉米像元数。\n横线不是置信区间。类型允许交汇重叠；没有边段身份，不能称“同一段边界两侧”，也不能外推到内部。',fontsize=11)
    m.save(pd.DataFrame(rows),'figure2_plot_data');save(fig,'02_corn_soy_boundary_asymmetry')


def d_diagnostic():
    d=m.read(m.SUM/'distance_direction_summary.csv');d=d[d.target.eq('il_2023')&d.true_class.eq('soybean')]
    cp=m.read(m.PROC/'matched_contrast_per_prediction.csv');cp=cp[cp.true_class.eq('soybean')&cp.predicted_class.eq('corn')]
    cs=m.read(m.SUM/'matched_contrast_summary.csv');cs=cs[cs.true_class.eq('soybean')&cs.predicted_class.eq('corn')]
    rows=[];fig,axs=plt.subplots(2,3,figsize=(16,10))
    fig.subplots_adjust(left=.08,right=.99,bottom=.16,top=.86,hspace=.39,wspace=.22)
    for mi,model in enumerate(m.MODELS):
        ax=axs[0,mi];ax.set_title(LABELS[model]);ax.axhline(0,color='black',lw=.7)
        for source in m.SITES[:3]:
            for pred,ls in [('corn','-'),('other','--')]:
                z=d[d.model.eq(model)&d.source.eq(source)&d.predicted_class.eq(pred)].set_index('band').loc[list(m.BANDS)]
                ax.plot(X[:6],z.delta_rate.iloc[:6],ls,color=SOURCE_COLORS[source],marker='o' if pred=='corn' else '^',ms=3)
                ax.scatter(X[6],z.delta_rate.iloc[6],color=SOURCE_COLORS[source],marker='o' if pred=='corn' else '^',s=28)
                for band,r in z.iterrows():rows.append(dict(panel='distance',model=model,source=source,band=band,predicted_class=pred,mean=r.delta_rate,within=r.within_rate,cross=r.cross_rate_mean))
        ax.set_xticks(X,BT,rotation=35);ax.set_ylim(-.015,.15);ax.set_xlabel('距类别交界的距离带／像元')
        ax=axs[1,mi];ax.axhline(0,color='black',lw=.7)
        for ci,contrast in enumerate(['area_at_close_composition','composition_at_close_area']):
            for si,s in enumerate(m.SITES[:3]):
                z=cp[cp.model.eq(model)&cp.source.eq(s)&cp.contrast.eq(contrast)&cp.kind.eq('cross')].sort_values('fold')
                baseline=cp[cp.model.eq(model)&cp.contrast.eq(contrast)&cp.kind.eq('within')].right_minus_left_rate.item()
                vals=z.right_minus_left_rate.to_numpy()-baseline;stat=m.strict_stats(vals,z.fold)
                r=cs[cs.model.eq(model)&cs.source.eq(s)&cs.contrast.eq(contrast)].iloc[0]
                m.close_values('figure3 matched difference '+str((model,s,contrast)),stat['mean'],r.delta_right_minus_left_rate)
                x=ci+(si-1)*.20
                ax.plot([x,x],[stat['min'],stat['max']],color=SOURCE_COLORS[s],lw=1.5)
                ax.scatter(np.full(5,x),vals,color=SOURCE_COLORS[s],s=15,alpha=.45)
                ax.scatter(x,stat['mean'],color=SOURCE_COLORS[s],marker='D',s=45,zorder=3)
                rows.append(dict(panel='matched',model=model,source=s,contrast=contrast,mean=stat['mean'],minimum=stat['min'],maximum=stat['max'],direction=stat['direction']))
        ax.set_xticks([0,1],['组成接近：AREA高−低\n30对图块','AREA接近：其他占比高−低\n36对图块']);ax.set_xlim(-.55,1.55);ax.set_ylim(-.045,.24)
        ax.set_title('固定图块对照中的额外错分差')
    axs[0,0].set_ylabel('大豆定向错误率增量\n跨站均值 − 本站，原尺度')
    axs[1,0].set_ylabel('大豆→玉米率增量：右组 − 左组\n原尺度差值')
    for ax in axs.flat:clean(ax)
    fig.suptitle('D站大豆：错成玉米可延续到内部，有限条件对照仍有模型与来源差异',fontsize=17,y=.977)
    handles=[Line2D([],[],color=SOURCE_COLORS[s],lw=2,label=SITE[s]+'源') for s in m.SITES[:3]]
    handles += [Line2D([],[],color='black',marker='o',lw=1.5,label='大豆→玉米'),Line2D([],[],color='black',marker='^',ls='--',lw=1.5,label='大豆→其他'),Line2D([],[],color='gray',marker='D',label='下排：均值、五次逐值及范围')]
    fig.legend(handles=handles,ncol=6,loc='upper center',bbox_to_anchor=(.5,.937),frameon=False)
    fig.text(.08,.055,'上排断开>6开放区间；该带未被赋予最近边界类型。下排按预测编号计算组间增量差，范围不是置信区间。\n组成接近要求玉米和大豆占比各差≤0.05；AREA接近要求较大/较小≤1.10。对照仅覆盖D站少量图块，仍有组成残差，不能解释为独立结构效应。',fontsize=11)
    m.save(pd.DataFrame(rows),'figure3_plot_data');save(fig,'03_d_soybean_distance_and_fixed_contrasts')


if __name__=='__main__':
    style();weights();boundary();d_diagnostic();m.record(__file__,'plot script');m.finish('plot')
