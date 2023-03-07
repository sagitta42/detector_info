import os
import json
import pandas as pd

# -------------------------------------------------------------------------------

# path to LEGEND detector metadata jsons
METADATA_PATH = "/home/sagitta/_legend/detectors/legend-detectors/germanium/diodes/"

# define json path to parameter keyword
JSON_FIELDS = {
    'date': ['production', 'delivered'],

    'mass': ['production', 'mass_in_g'],
    'radius': ['geometry', 'radius_in_mm'],
    'height': ['geometry', 'height_in_mm'],

    'depV': ['production', 'dep_voltage_in_V'], # measured at HADES
    'depV_man': ['characterization', 'manufacturer', 'dep_voltage_in_V'], # manufacturer depV

    'fwhm_Qbb': ['characterization', 'l200_site', 'fwhm_in_keV', 'qbb'], # FWHM @ QBB from Th228 char
    'fwhm_Co60': ['characterization', 'l200_site', 'fwhm_in_keV', 'co60fep'], # FWHM @ 60Co 2nd peak
    'fwhm_Co60_man': ['characterization', 'manufacturer', 'fwhm_co60fep_in_keV'], # FWHM @ 60Co 2nd peak

    'fwhm_TlFEP': ['characterization', 'l200_site', 'fwhm_in_keV', 'tl208fep'],
    'sf_TlDEP': ['characterization', 'l200_site', 'survival_fraction', 'tl208dep'],
    'sf_Qbb': ['characterization', 'l200_site', 'survival_fraction', 'qbb'],
    'sf_TlSEP': ['characterization', 'l200_site', 'survival_fraction', 'tl208sep'],
    'sf_TlFEP': ['characterization', 'l200_site', 'survival_fraction', 'tl208fep'],

    'dl_man': ['characterization', 'manufacturer', 'dl_thickness_in_mm'], # for standard format

    'daq': ['characterization', 'l200_site', 'daq'],

    'enr': ['production', 'enrichment'],
    'repr': ['production', 'reprocessing'],
    'cry': ['production', 'crystal']
}

# -------------------------------------------------------------------------------

def info_table(params, metadata_path=METADATA_PATH, det_type='all', max_order=10000):
    '''
    (list, string, list, int) -> pd.DataFrame

    Construct a DataFrame with given parameters as columns for each detector

    params [list]: list of parameter keywords as defined in JSON_FIELDS
    metadata_path [string]: path to folder with detector metadata jsons
    det_type [list|string]: string or list of strings - detector type(s) to analyze, V=ICPC, B=BEGe, P=PPC, C=Coax (semi-coax), 'all' for all types
    max_order [int]: maximum order to plot (default all orders)

    >>> info_table(['mass', 'fwhm_Qbb'], 'legend-detectors/germanium/detectors/', ['B'])
       det_name  order   mass  fwhm_Qbb
    0   B00000A      0  0.496      2.37
    1   B00000B      0  0.697      2.12
    2   B00000C      0  0.815      2.07
    ...
    27  B00091B      0  0.650      2.25
    28  B00091C      0  0.627      2.11
    29  B00091D      0  0.693      2.09
    '''
    if det_type == 'all':
        det_type = ['B','C','P','V']
    elif isinstance(det_type, str):
        det_type = [det_type]

    # list of detector names
    det_list = detector_list(metadata_path, max_order, det_type)

    ## get parameters from metadata
    df = get_params(det_list, params, metadata_path)
    df = df.sort_values(['order', 'det_name'])
    if 'mass' in params: df['mass'] = df['mass'] / 1000. # g -> kg

    return df

# -------------------------------------------------------------------------------
# helper functions
# -------------------------------------------------------------------------------

def get_params(det_list, params, metadata_path=METADATA_PATH):
    '''
    (list, list, string) -> dict

    Return dict of given parameters values for given detector names

    det_list [list]: list of detector json names (without extension)
    params [list]: list of parameter keywords as defined in JSON_FIELDS
    metadata_path [string]: path to folder with detector metadata jsons

    >>> get_params(['V06643A', 'V06649A'], ['mass', 'fwhm_Qbb'], 'legend-detectors/germanium/detectors/')
         det_name  order    mass  fwhm_Qbb
      0  V06643A      6  2286.2      2.54
      1  V06649A      6  2597.3      2.26
    '''

    # prepare empty result dict
    res = {'det_name': det_list}
    res['order'] = [int(x[1:3]) for x in det_list]
    for p in params: res[p] = []

    for det in det_list:
        # read metadata file into a dict
        f = open(os.path.join(metadata_path, det + '.json'))
        js = json.load(f)
        # obtain values of given params
        for p in params:
            res[p].append(get_json_field(js, p))

        f.close()

    return pd.DataFrame(res)


def detector_list(metadata_path, max_order, det_type):
    '''
    (string, int, list) -> list

    Return list of detector names from legend-metadata folder

    metadata_path [string]: path to folder with detector metadata jsons
    max_order [int]: maximum order to plot (default all orders)
    det_type [list]: detector types to analyze, V=ICPC, B=BEGe, P=PPC, C=Coax (semi-coax)

    >>> detector_list('legend-detectors/germanium/detectors/', 10, ['V'])
    ['V00048A', 'V00048B', ..., 'V09374A', 'V09724A', 'V10784A']

    '''

    det_list = [x.split('.')[0] for x in os.listdir(metadata_path) if (x[0] in det_type and int(x[1:3]) <= max_order)]
    det_list.sort()
    return det_list


def get_json_field(js, param):
    '''
    (json ?, string) -> value

    Find field corresponding to given parameter based on JSON_FIELDS definition and return its value from given json

    js [json?]: json ? of detector metadata format
    param [string]: parameter of interest as defined in JSON_FIELDS
    '''
    # start with full dictionary and home in on the field
    ret = js
    for f in JSON_FIELDS[param]:
        if not f in ret:
            # !! quickfix for DL check
            print('Parameter {} not in json!'.format(param))
            return 0
        ret = ret[f]

    return ret

if __name__ == '__main__':
    # lst = detector_list(METADATA_PATH, 10, ['V'])
    # lst = get_params(['V06643A', 'V06649A'], ['mass', 'fwhm_Qbb'], METADATA_PATH)
    lst = info_table(['mass', 'fwhm_Qbb'], METADATA_PATH, ['B'])

    print(lst)
