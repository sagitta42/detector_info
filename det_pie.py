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
    total number of detectors: 116
    total mass: 163.89079999999998
    ----BEGe (GERDA)
    30 detectors - 20kg
    ----Coax (GERDA)
    6 detectors - 15kg
    ----ICPC (GERDA)
    5 detectors - 10kg
    ----ICPC (new)
    42 detectors - 92kg
    ----PPC (MJD)
    33 detectors - 28kg
    leftover: 35kg
                   mass    color                             label
    det_type
    BEGe (GERDA)     20  #2ca02c  BEGe (GERDA)\n30 detectors\n20kg
    Coax (GERDA)     15  #9467bd   Coax (GERDA)\n6 detectors\n15kg
    ICPC (GERDA)     10  #1f77b4   ICPC (GERDA)\n5 detectors\n10kg
    ICPC (new)       92  #07a9ff    ICPC (new)\n42 detectors\n92kg
    ICPC (planned)   35  #cccccc              ICPC (planned)\n35kg
    PPC (MJD)        28  #ff7f0e     PPC (MJD)\n33 detectors\n28kg
    Saving as plots/L200_detector_pie.pdf
    '''
    ## 1. Read table
    df = info_table(['mass'], det_type=['V', 'B', 'P', 'C'])

    print('total number of detectors: {}'.format(len(df)))
    print('total mass: {}'.format(df['mass'].sum()))

    df['det_type'] = df['det_name'].apply(lambda x: x[0])
    # here GERDA ICPCs will be marked as 'ICPC (new)' via LABELS['V']
    df['label'] = df['det_name'].apply(lambda x: LABELS[x[0]])
    # change label for GERDA ICPCs
    df.at[df[ (df['det_type'] == 'V') & (df['order'] == 0) ].index, 'label'] = 'ICPC (GERDA)'

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

    plt.setp(pcts, color='white')#, fontweight='bold')
    # plt.tight_layout()
    figname = 'plots/L200_detector_pie.pdf'
    print('Saving as {}'.format(figname))
    plt.savefig(figname, bbox_inches='tight')

if __name__ == '__main__':
    det_pie()
