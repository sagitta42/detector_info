import matplotlib.pyplot as plt
# increase all font sizes
plt.rcParams.update({'font.size': 18})

from info_table import *

# define as preferred
# -------------------------------------------------------------------------------

# symbols for parameters (includes line or no line)
# if parameter is in SYMBOL, the marker will be empty, otherwise defaults to solid dot
# (convenient to highlight L200 measurement vs other when more than 1 param is plotted)
SYMBOL = {
    'depV_man': '^',
    'dl_man': '^'
}

# the marker will be solid by default or if label is 'L200 measurement' (to contrast with vendor)
# if parameter not in LABELS, there will be no legend label
LABELS = {
    'depV': 'L200 measurement',
    'depV_man': 'vendor specification',
}

# y-axis titles
# note that in info_table.py mass is converted to kg
TITLES = {
    'depV': 'Depletion voltage [V]',
    'depV_man': 'Depletion voltage [V]',
    'mass': 'Mass [kg]',
    'dl': 'Dead layer [mm]',
    'dl_man': 'Dead layer [mm]',
    'enr': 'Enrichment (%)'
}

# colors for ICPC orders (order 0 = GERDA ICPC)
COLORS = {
    0: '#bcbd22', # mustard
    1: 'r',
    2: 'm',
    4: 'b',
    5: 'c',
    7: 'g',
    8: '#8c564b', # brown
    9: 'orange',
    10: '#5c00a3', # violet
    6: '#de3163' # pink
}

# -------------------------------------------------------------------------------

def params_vs_det(params, det_type=['V'], avg=False):
    '''
    (list, list, bool) -> pdf image

    Plot given parameters vs detector name

    params [list]: list of parameter keywords as defined in JSON_FIELDS in info_table.py
    det_type [list]: detector types to analyze, V=ICPC, B=BEGe, P=PPC, C=Coax (semi-coax)
    avg [bool]: plot average line for each order and total

    >>> params_vs_det(['depV', 'depV_man'], det_type=['V'])
    --- order # 0
    --- order # 1
    No data for depV_man for order 1
    --- order # 2
    --- order # 4
    --- order # 5
    --- order # 6
    No data for depV_man for order 6
    --- order # 7
    --- order # 8
    --- order # 9
    --- order # 10
    Saving as plots/det_typeV_depV-depV_man.pdf
    '''
    ## 1. get param info
    # pandas dataframe with columns for given params for each detector of given type
    df = info_table(params, det_type=det_type)

    # order index for gaps between orders of ICPC
    # for non-ICPC since there is only one "order" will be simply a normal plot
    order_idx = -1
    # collect xticks to create gaps between orders
    xticks = []

    fig, ax = plt.subplots(figsize=(20,8))

    for order, group in df.groupby('order'):
        print('--- order #', order)
        order_idx += 1

        # collect xticks for adding spaces between orders
        # index is default int from 0 to N - easier for plotting thatn string det names
        xticks += list(group.index + order_idx)

        for p in params:
            # remove parameters that have zero value - means there is no information
            # in the future should be set to a value like "null" to emphasize it's not actually zero
            group = group[group[p] != 0]

            if len(group) == 0:
                print('No data for {} for order {}'.format(p, order))
                continue

            ## plot style
            label = '_nolegend'
            # order label applies only to ICPC; order 0 = GERDA
            if det_type == ['V']:
                label = 'GERDA' if order == 0 else 'Order #{}{}'.format(0 if order < 10 else '', order)
            # only want to plot label once per parameter
            label = label if p == params[0] else '_nolegend_'
            color = COLORS[order]
            symbol = SYMBOL[p][0] if p in SYMBOL else 'o'
            # the marker will be solid by default or if label is 'L200 measurement' (to contrast with vendor)
            # otherwise no facecolor
            mfc=color if not p in LABELS or LABELS[p] == 'L200 measurement' else 'none'
            # deafult solid line, otherwise defined in SYMBOL (only marker for no line)
            lstyle = '-'
            if p in SYMBOL: lstyle = SYMBOL[p][1:] if len(SYMBOL[p]) > 1 else 'none'

            ## 2. Plot parameters
            # by adding order_idx to group.index (element-wise) we add the gap between orders
            plt.plot(group.index + order_idx, group[p],\
                    marker=symbol, ms=10, mfc=mfc,\
                    linestyle=lstyle, linewidth=1.5,\
                    c=color, label=label)

            # 3. Plot averages if requested
            unit = {'mass': 'kg', 'fwhm_Qbb': 'keV', 'depV': 'V'}
            if avg:
                # average for order
                plt.hlines(y=group[p].mean(), xmin=group.index[0]+ order_idx, xmax=group.index[-1]+ order_idx, color=color, linestyle='--', linewidth=2)
                if p not in unit:
                    # will be printed before the error in next line if p not in unit
                    print('Add {} in unit dict to plot averages'.format(p))
                # total average
                text = '-- average: {} {}'.format(round(df[p].mean(), 2), unit[p])
                # add total if param is mass
                if p == 'mass': text += '\ntotal: {} {}'.format(round(df[p].sum(), 2), unit[p])
                plt.axhline(df[p].mean(), color='dimgrey', linestyle='--', linewidth=2)
                x = 0.05; y = 0.85
                plt.text(x, y, text, transform=pp.ax.transAxes, fontsize=16, color='dimgrey', bbox=dict(facecolor='w', edgecolor='dimgrey', boxstyle='round'))

    ## 4. Plot label for parameters once (phantom plot for legend)
    for p in params:
        plt.plot(-2,-2,\
            marker = SYMBOL[p][0] if p in SYMBOL else 'o',\
            ms=10, mfc='k' if not p in LABELS or LABELS[p] == 'L200 measurement' else 'none',\
            linestyle='none', c = 'k', label=LABELS[p] if p in LABELS else '_nolegend_')

    ## 5. Style plot
    # force xlim because of the phantom points at (-2,-2)
    ax.set_xlim(xmin=-1)
    ax.set_xticks(xticks)
    ax.set_xticklabels(df['det_name'])
    ax.grid(linestyle='--',zorder=0, which='major')
    fig.autofmt_xdate(rotation=90, ha='center')

    plt.ylabel(TITLES[params[0]])

    x = 0.98; y = 0.55
    plt.text(x, y, 'L200 - preliminary', transform=ax.transAxes, fontsize=16, rotation=90)
    # legend outside on top
    leg = plt.legend(loc = 'lower center', ncol=6, bbox_to_anchor=(0.5, 1.0))
    # remove legend if empty
    handles, labels = ax.get_legend_handles_labels()
    if len(handles) == 0: leg.remove()

    ave = '_avg' if avg else ''
    figname = 'plots/det_type{}_{}{}.pdf'.format('-'.join(det_type), '-'.join(params), ave)
    print('Saving as {}'.format(figname))
    plt.tight_layout()
    plt.savefig(figname)



if __name__ == '__main__':
    # default METADATA_PATH defined in info_table.py
#    params_vs_det(['depV', 'depV_man'], det_type=['V'])
#    params_vs_det(['mass'], det_type=['B'])
    # --- tests
    params_vs_det(['dl', 'dl_man'], det_type=['B', 'P', 'C'])
    # params_vs_det(['enr'], det_type=['B', 'P', 'C'])
    # params_vs_det(['enr'], det_type=['V'])

    # params_vs_det([''])
