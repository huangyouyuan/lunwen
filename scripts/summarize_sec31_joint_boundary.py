"""Write a bounded reading report and traceable prose values from verified tables."""
from pathlib import Path
import hashlib
import json

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results/summary/sec31_joint_boundary'
TABLE = ROOT / 'tables/sec31_spatial_text_values.tex'
MODELS = ['convgru', 'unet3d', 'utae']
NAMES = dict(convgru='ConvGRU', unet3d='3D U-Net', utae='U-TAE', corn='玉米', soybean='大豆', boundary='边界', interior='内部')


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def write(path, text):
    with path.open('x', encoding='utf-8', newline='\n') as f:
        f.write(text)


def pick(df, **where):
    for k, v in where.items():
        df = df[df[k].isin(v if isinstance(v, list) else [v])]
    return df


def display(x):
    return 'NA' if pd.isna(x) else f'{0 if abs(x) < .005 else x:.2f}'


def md_table(headers, rows):
    return '\n'.join(['| ' + ' | '.join(headers) + ' |', '|' + '|'.join(['---']*len(headers)) + '|'] +
                     ['| ' + ' | '.join(str(v).replace('|', r'\|') for v in row) + ' |' for row in rows])


def main():
    paths = [OUT/'analysis.md', OUT/'prose_evidence.csv', OUT/'reading_manifest.json', TABLE]
    if any(p.exists() for p in paths):
        raise FileExistsError('Preserve existing reading outputs before regeneration')
    files = ['reference_support.csv', 'within_position_metrics.csv', 'within_joint_metrics.csv',
             'within_site_position_metrics.csv', 'small_area_by_shape.csv', 'model_comparisons.csv']
    data = {f: pd.read_csv(OUT/f, float_precision='round_trip') for f in files}
    ref, pos, joint, whole, small, comp = [data[f] for f in files]
    evidence = []

    def add(macro, source, where, expression, meaning, unit='%'):
        x = pick(data[source], **where)
        # Expressions below are fixed author-owned code, not external input.
        value = float(eval(expression, {'__builtins__': {}}, {'x': x}))
        evidence.append(dict(macro=macro, source_file='results/summary/sec31_joint_boundary/'+source,
            selector=json.dumps(where, ensure_ascii=False, sort_keys=True), expression=expression,
            value=value, display=display(value), unit=unit, meaning=meaning))

    a = '100-<200|1.5-<2'
    for crop, suffix in [('corn', 'Corn'), ('soybean', 'Soy')]:
        add('SACrop'+suffix, files[0], dict(site='A', crop=crop, group=a), '100*x.area_share.iloc[0]', 'A站主要组合占全站该作物面积')
        add('SABound'+suffix, files[0], dict(site='A', crop=crop, group=a), '100*x.boundary_share.iloc[0]', 'A站主要组合的边界占比')
    add('SAInteriorMax', files[1], dict(site='A', group=a, position='interior'), '100*x.omission_rate.max()', 'A站两作物三模型主要组合内部漏分率最大值')
    b = dict(site='B', crop='soybean', shape_bin_order=0)
    add('SBSmallArea', files[4], b | dict(model='convgru'), '100*x.reference_pixels.sum()/x.whole_crop_pixels.iloc[0]', 'B站大豆小于50ha且SHAPE小于1.5面积占比')
    add('SBSmallFnMin', files[4], b, '100*x.groupby("model").error_share.sum().min()', '上述组合三模型全站漏分贡献最小值')
    add('SBSmallFnMax', files[4], b, '100*x.groupby("model").error_share.sum().max()', '上述组合三模型全站漏分贡献最大值')
    add('SBSmallBound', files[4], b | dict(model='convgru'), '100*x[x.position.eq("boundary")].reference_pixels.sum()/x.reference_pixels.sum()', '上述组合边界占比')
    add('SBSmallBoundaryFn', files[4], b | dict(model='convgru', position='boundary'), '100*x.omission_rate.iloc[0]', '上述组合ConvGRU边界漏分率')
    add('SBSmallInteriorFn', files[4], b | dict(model='convgru', position='interior'), '100*x.omission_rate.iloc[0]', '上述组合ConvGRU内部漏分率')
    add('SBComplexArea', files[4], dict(site='B', crop='soybean', shape_bin_order=3, model='convgru'), '100*x.reference_pixels.sum()/x.whole_crop_pixels.iloc[0]', 'B站大豆小于50ha且SHAPE至少3面积占比')
    add('SBComplexBound', files[4], dict(site='B', crop='soybean', shape_bin_order=3, model='convgru'), '100*x[x.position.eq("boundary")].reference_pixels.sum()/x.reference_pixels.sum()', '上述复杂形状组合边界占比')
    for crop, suffix in [('corn', 'Corn'), ('soybean', 'Soy')]:
        add('SDSmall'+suffix, files[4], dict(site='D', crop=crop, shape_bin_order=0, model='convgru'), '100*x.reference_pixels.sum()/x.whole_crop_pixels.iloc[0]', 'D站小于50ha且SHAPE小于1.5面积占比')
    dgroup = '10-<50|1-<1.5'
    add('SDMainArea', files[0], dict(site='D', crop='corn', group=dgroup), '100*x.area_share.iloc[0]', 'D站玉米10至50ha、SHAPE小于1.5面积占比')
    for position, suffix in [('boundary', 'Boundary'), ('interior', 'Interior')]:
        add('SDReduction'+suffix, files[5], dict(site='D', crop='corn', group=dgroup, baseline_model='convgru', comparison_model='unet3d', position=position), 'x.rate_reduction_pp.iloc[0]', 'D站该组3D U-Net相对ConvGRU漏分率降低值', '百分点')
    add('SDNetShare', files[5], dict(site='D', crop='corn', group=dgroup, baseline_model='convgru', comparison_model='unet3d'), '100*x.net_reduction_share.sum()', 'D站该组边界加内部占全站玉米漏分净减少量比例')
    cgroup = '200-<500|>=3'
    add('SCMainArea', files[0], dict(site='C', crop='corn', group=cgroup), '100*x.area_share.iloc[0]', 'C站玉米200至500ha、SHAPE至少3面积占比')
    for position, suffix in [('boundary', 'Boundary'), ('interior', 'Interior')]:
        add('SCReduction'+suffix, files[5], dict(site='C', crop='corn', group=cgroup, baseline_model='convgru', comparison_model='unet3d', position=position), 'x.rate_reduction_pp.iloc[0]', 'C站该组3D U-Net相对ConvGRU漏分率降低值', '百分点')
    add('SCNetShare', files[5], dict(site='C', crop='corn', group=cgroup, baseline_model='convgru', comparison_model='unet3d'), '100*x.net_reduction_share.sum()', 'C站该组边界加内部占全站玉米漏分净减少量比例')
    for crop, suffix in [('corn', 'Corn'), ('soybean', 'Soy')]:
        add('SDSoyNet'+suffix, files[5], dict(site='D', crop=crop, group=dgroup, baseline_model='convgru', comparison_model='utae'), '100*x.net_reduction_share.sum()', 'D站该组U-TAE相对ConvGRU全站净减少贡献')
    for position, suffix in [('boundary', 'Boundary'), ('interior', 'Interior')]:
        add('SCUtae'+suffix, files[3], dict(site='C', crop='corn', model='utae', position=position), '100*x.omission_rate.iloc[0]', 'C站玉米U-TAE全站位置漏分率')
        add('SCUnet'+suffix, files[3], dict(site='C', crop='corn', model='unet3d', position=position), '100*x.omission_rate.iloc[0]', 'C站玉米3D U-Net全站位置漏分率')
    add('SCNegativeArea', files[0], dict(site='C', crop='corn', group='>=500|>=3'), '100*x.area_share.iloc[0]', 'C站玉米至少500ha、SHAPE至少3面积占比')
    add('SCNegativePp', files[5], dict(site='C', crop='corn', group='>=500|>=3', baseline_model='convgru', comparison_model='utae', position='interior'), '-x.rate_reduction_pp.iloc[0]', 'C站该组U-TAE内部漏分率比ConvGRU高', '百分点')
    write(OUT/'prose_evidence.csv', pd.DataFrame(evidence).to_csv(index=False, float_format='%.17g', lineterminator='\n'))
    write(TABLE, '% Derived full-precision values; selectors and formulas in sec31_joint_boundary/prose_evidence.csv.\n' +
          ''.join('\\newcommand{\\'+e['macro']+'}{'+e['display']+'}\n' for e in evidence))

    report = ['# 3.1面积—形状与错误位置核查', '', '2026-10-17，derived；范围：四站站内预测。Verified（分组整数与原始像元核验另见verification记录）。', '',
        '本报告先读取全部组合，再挑选有面积支持且能回答3.1现象的例子。完整结果不因方向删减。表中率和贡献均为百分数，漏分率差为百分点，展示两位小数；NA为零分母。整数底表保持整数，计算与CSV不提前舍入。', '',
        '## 全站基准与分母', '',
        '同一站、作物、组合的三模型参考支持相同。边界为完整参考类别交界中心距≤30 m的作物像元；内部合并其余所有距离分组。共享边按有效四邻域定义，完整斑块为八邻域，两者用途不同。', '',
        '漏分贡献=该组合该位置FN/同模型全站该作物FN；净减少贡献=(ConvGRU FN−比较模型FN)/(ConvGRU全站FN−比较模型全站FN)。净贡献允许负值及超过100%；它不是逐像元纠正率。可加贡献用全站参考像元作分母。', '']
    rows=[]
    for (site, crop), x in whole.groupby(['site', 'crop'], sort=True):
        z=pick(x, model='convgru', position='boundary').iloc[0]
        rates=[]
        for position in ['boundary', 'interior']:
            rates.append(' / '.join(display(100*pick(x, model=m, position=position).omission_rate.iloc[0]) for m in MODELS))
        rows.append([site, NAMES[crop], display(100*z.area_share), *rates])
    report += [md_table(['站点','作物','边界面积占比','边界漏分率：ConvGRU / 3D / U-TAE','内部漏分率：同序'],rows),'',
        '## A站：较高精度对应的主要组合', '',
        '两作物面积最大的组合均为100–200 ha、SHAPE 1.5–2。它们的边界占比低于各作物全站边界占比，三模型的内部漏分率最高为0.64%，边界也低于同站全作物边界率。该对应支持具体组合表现良好的描述，不能单独分解F1，也不能据此认定面积或形状具有独立因果作用。', '']
    rows=[]
    for crop in ['corn','soybean']:
        for r in pick(ref,site='A',crop=crop).nlargest(4,'reference_pixels').itertuples():
            x=pick(pos,site='A',crop=crop,group=r.group)
            rates=[' / '.join(display(100*pick(x,model=m,position=p).omission_rate.iloc[0]) for m in MODELS) for p in ['boundary','interior']]
            rows.append([NAMES[crop],r.group,display(100*r.area_share),display(100*r.boundary_share),*rates])
    report += [md_table(['作物','完整斑块组合','作物面积占比','组内边界占比','边界漏分率：C / 3D / U','内部漏分率：同序'],rows),'',
        '## B站大豆与D站两作物：支持量与位置率分开看', '',
        'B站AREA<50 ha的大豆中，SHAPE<1.5的组合贡献最多漏分；SHAPE≥3组的边界占比和漏分率较高，但面积仅占0.49%，不能写成全站主因。较规则的小斑块也有较高边界占比和边界漏分率，两者分别反映位置构成与组内识别表现。D站两作物在该规则小斑块组的面积支持、边界占比和内部漏分率接近，与两作物F1接近相对应；但不能说各模型的边界漏分率作物差距都小于B站，3D U-Net及U-TAE即有相反对应。未排除其它误分的影响。', '']
    rows=[]
    for site,crops in [('B',['corn','soybean']),('D',['corn','soybean'])]:
        for crop in crops:
            for order in (range(4) if site=='B' and crop=='soybean' else [0]):
                x=pick(small,site=site,crop=crop,shape_bin_order=order)
                c=pick(x,model='convgru'); b=pick(c,position='boundary').iloc[0]
                rates=[' / '.join(display(100*pick(x,model=m,position=p).omission_rate.iloc[0]) for m in MODELS) for p in ['boundary','interior']]
                shares=' / '.join(display(100*pick(x,model=m).error_share.sum()) for m in MODELS)
                rows.append([site,NAMES[crop],b.shape_bin,display(100*c.reference_pixels.sum()/b.whole_crop_pixels),
                             display(100*b.reference_pixels/c.reference_pixels.sum()),*rates,shares])
    report += [md_table(['站点','作物','SHAPE（AREA<50 ha）','作物面积占比','组内边界占比','边界漏分率：C / 3D / U','内部漏分率：同序','占全站作物FN：同序'],rows),'',
        '## C、D站模型差异：逐组合的带符号净差', '',
        '下面按每站、作物、比较模型的边界+内部净减少量排列前三个组合，所有组合仍保留在model_comparisons.csv。D站两作物净减少较集中于10–50 ha、SHAPE<1.5组，且边界和内部均改善。C站玉米净减少较分散：3D U-Net的最大组合为200–500 ha、SHAPE≥3；U-TAE的最大组合却为10–50 ha、SHAPE<1.5。不能用“C站复杂斑块多”直接推定模型差距大小。', '']
    rows=[]
    for site in ['C','D']:
        for crop in ['corn','soybean']:
            for model in ['unet3d','utae']:
                x=pick(comp,site=site,crop=crop,baseline_model='convgru',comparison_model=model)
                totals=x.groupby('group').net_fewer_pixels.sum().nlargest(3)
                for group,net in totals.items():
                    r=pick(ref,site=site,crop=crop,group=group).iloc[0]
                    z=pick(x,group=group).set_index('position')
                    rows.append([site,NAMES[crop],NAMES[model],group,display(100*r.area_share),display(net),
                        display(100*z.net_reduction_share.sum()),display(z.loc['boundary','rate_reduction_pp']),display(z.loc['interior','rate_reduction_pp'])])
    report += [md_table(['站点','作物','对照模型（相对ConvGRU）','组合','面积占比','净减少像元','全站净减少贡献','边界降低（百分点）','内部降低（百分点）'],rows),'',
        '## ConvGRU内部漏分来自哪些组合', '',
        '每站每作物只列内部漏分计数最多的一组作定位，其余组不删除。A站两作物、B站大豆、D站两作物主要为10–50 ha、SHAPE<1.5；B站玉米和C站两作物则主要为更大或较复杂的组合。ConvGRU内部识别不足并非只发生于一种面积或形状组。下表“内部漏分贡献”的分母仅用于本段定位，是ConvGRU全站该作物内部FN，不是正式组表的全站总FN分母。', '']
    rows=[]
    for site in SITES_ORDER:
        for crop in ['corn','soybean']:
            x=pick(pos,site=site,crop=crop,position='interior',model='convgru')
            r=x.nlargest(1,'fn').iloc[0]
            rates=' / '.join(display(100*pick(pos,site=site,crop=crop,group=r.group,position='interior',model=m).omission_rate.iloc[0]) for m in MODELS)
            rows.append([site,NAMES[crop],r.group,display(100*r.group_area_share),display(r.fn),display(100*r.fn/x.fn.sum()),rates])
    report += [md_table(['站点','作物','组合','作物面积占比','ConvGRU内部FN','内部FN贡献','内部漏分率：C / 3D / U'],rows),'',
        '## U-TAE与3D U-Net：位置优势及反例', '',
        '正数表示U-TAE比3D U-Net少漏分，负数表示多漏分。C站玉米与D站大豆均出现边界少漏分、内部多漏分；C站大豆两处均为3D U-Net漏分较少，尽管U-TAE的完整F1略高。遗漏参考其它地类误分入作物的像元使漏分排序不能替代F1排序。', '']
    rows=[]
    for (site,crop), x in pick(comp,baseline_model='unet3d',comparison_model='utae').groupby(['site','crop']):
        z=x.groupby('position').net_fewer_pixels.sum()
        rows.append([site,NAMES[crop],display(z['boundary']),display(z['interior']),display(z.sum())])
    report += [md_table(['站点','作物','边界净少漏分像元','内部净少漏分像元','全站净少漏分像元'],rows),'',
        '对ConvGRU的两种比较各有8个组合×位置出现负向净变化，下面全部列出，不只保留正向结果。C站玉米≥500 ha、SHAPE≥3组占8.63%的玉米面积，其内部U-TAE比ConvGRU多漏分320个像元、漏分率高0.18个百分点，是有面积支持的反例。', '']
    rows=[]
    for r in pick(comp,baseline_model='convgru').query('net_fewer_pixels < 0').sort_values('net_fewer_pixels').itertuples():
        rows.append([r.site,NAMES[r.crop],NAMES[r.comparison_model],r.group,NAMES[r.position],
            display(100*r.group_reference_pixels/r.whole_crop_pixels),display(r.net_fewer_pixels),display(r.rate_reduction_pp)])
    report += [md_table(['站点','作物','比较模型','组合','位置','组合面积占比','净减少像元（负为变差）','漏分率降低（百分点）'],rows),'',
        '## 图文用途与尚不能回答的问题', '',
        '新图4为全站4×3作物参考像元对错分布，可观察红色聚集与模型差异。原2560×2560像元完整嵌入5.2 cm图框，纸面不能逐个辨认30 m像元；细小边界及组合差异以全站整数统计为证。此前最大分歧局部图、坐标和统计留在sec31_spatial_examples，作为补充和选择追溯，不支持全站典型性判断。', '',
        '这些数据能够定位漏分及其净差，不能分离AREA与SHAPE的独立作用，不能由描述性对应推断机制，也不能由漏分净差分解F1。当前分析没有按完整斑块组合归属参考其它地类误分入作物的像元，因此不强行解释剩余F1差异。未新增训练、推理、景观指标、回归体系或分组图。', '',
        '正文数值逐项来源：prose_evidence.csv；原整数与分母：reference_support.csv、within_position_metrics.csv、model_comparisons.csv。源数据追溯见manifest.json与figure_manifest.json。']
    write(OUT/'analysis.md', '\n'.join(report)+'\n')
    write(OUT/'reading_manifest.json', json.dumps(dict(date='2026-10-17', data_status='derived',
        script_sha256=digest(Path(__file__)), input_sha256={str((OUT/f).relative_to(ROOT).as_posix()):digest(OUT/f) for f in files},
        output_sha256={str(p.relative_to(ROOT).as_posix()):digest(p) for p in paths if p.name!='reading_manifest.json'}),ensure_ascii=False,indent=2)+'\n')
    print('Wrote analysis report,',len(evidence),'traceable prose values and LaTeX macros.')


SITES_ORDER = ['A','B','C','D']
if __name__ == '__main__':
    main()
