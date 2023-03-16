import matplotlib.pyplot as plt
# increase all font sizes
plt.rcParams.update({'font.size': 10})
from info_table import *

# -------------------------------------------------------------------------------

COLORS = {
    'ICPC (new)': '#07a9ff', # LEGEND blue
    'BEGe (GERDA)': '#2ca02c', # green
    'Coax (GERDA)': '#9467bd', # purple
    'ICPC (GERDA)' : '#1f77b4', # dark blue
    'PPC (MJD)': '#ff7f0e', # orange
    'ICPC (planned)': '#cccccc', # grey
}

# ICPC GERDA label assigned later by subselecting order 0
LABELS = {
    'V': 'ICPC (new)',
    'B': 'BEGe (GERDA)',
    'P': 'PPC (MJD)',
    'C':'Coax (GERDA)'
}

# -------------------------------------------------------------------------------

def det_pie():
    '''
    Plot a pie chart of current status of L200 detector production

    >>> det_pie()
    total number of detectors: XXX
    total mass: XXX
    ----BEGe (GERDA)
    N detectors - XXkg
    ----Coax (GERDA)
    N detectors - XXkg
    ----ICPC (GERDA)
    N detectors - XXkg
    ----ICPC (new)
    N detectors - XXkg
    ----PPC (MJD)
    N detectors - XXkg
    leftover: XXkg
                   mass    color                             label
    det_type
    BEGe (GERDA)     XX  #2ca02c  BEGe (GERDA)\nN detectors\nXXkg
    Coax (GERDA)     XX  #9467bd   Coax (GERDA)\nN detectors\nXXkg
    ICPC (GERDA)     XX  #1f77b4   ICPC (GERDA)\nN detectors\nXXkg
    ICPC (new)       XX  #07a9ff    ICPC (new)\nN detectors\nXXkg
    ICPC (planned)   XX  #cccccc              ICPC (planned)\nXXkg
    PPC (MJD)        XX  #ff7f0e     PPC (MJD)\nN detectors\nXXkg
    Saving as plots/L200_detector_pie.pdf
    '''
    ## 1. Read table
    df = info_table(['mass'], det_type='all')

    print('total number of detectors: {}'.format(len(df)))
    print('total mass: {}'.format(df['mass'].sum()))

    df['det_type'] = df['det_name'].apply(lambda x: x[0])
    # here GERDA ICPCs will be marked as 'ICPC (new)' via LABELS['V']
    df['label'] = df['det_name'].apply(lambda x: LABELS[x[0]])
    # change label for GERDA ICPCs
    df.loc[ df[ (df['det_type'] == 'V') & (df['order'] == 0) ].index, 'label'] = 'ICPC (GERDA)'

    ## 2. Plot pie

    # empty dataframe to fill later
    dfpie = pd.DataFrame(columns=['mass', 'det_type', 'color', 'label'])
    dfpie = dfpie.set_index('det_type')

    for label, group in df.groupby('label'):
        print('----' + label)
        dfpie.at[label, 'mass'] = int(round(group['mass'].sum(), 0))
        num = len(group)
        dfpie.at[label, 'label'] = '{}\n{} detectors\n{}kg'.format(label, num, dfpie.loc[label]['mass'])
        dfpie.at[label, 'color'] = COLORS[label]
        print('{} detectors - {}kg'.format(num, dfpie.loc[label]['mass']))

    ## leftover from 200kg
    label = 'ICPC (planned)'
    dfpie.at[label, 'mass'] = 200 - dfpie['mass'].sum()
    dfpie.at[label, 'color'] = COLORS[label]
    dfpie.at[label, 'label'] = '{}\n{}kg'.format(label, dfpie.loc[label]['mass'])
    print('leftover: {}kg'.format(dfpie.loc[label]['mass']))

    dfpie = dfpie.sort_values('det_type')
    print(dfpie)

    fig, ax = plt.subplots(figsize=(4,4))
    _, _, pcts = ax.pie(dfpie['mass'], labels=dfpie['label'], autopct='%1.f%%',\
            colors=dfpie['color'], shadow=False, startangle=90,\
            explode = [0.02]*len(dfpie))
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    # total text (comment out if not wanted)
    total_text = "Total mass: {} kg".format(int(round(df['mass'].sum(),0)))
    total_text += "\nTotal # detectors: {}".format(len(df))
    fig.text(0.82, 0.15, total_text)

    plt.setp(pcts, color='white')#, fontweight='bold')
    # plt.tight_layout()
    figname = 'L200_detector_pie'
    print('Saving as {}'.format(figname))
    plt.savefig(figname + '.pdf', bbox_inches='tight')
    plt.savefig(figname + '.png', bbox_inches='tight')

if __name__ == '__main__':
    det_pie()
