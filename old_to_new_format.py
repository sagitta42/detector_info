import os
import json
from collections import OrderedDict
import pprint
import numpy as np
import pandas as pd

METADATA_PATH = "/home/sagitta/_legend/detectors/legend-detectors/germanium/detectors/"
TEST_PATH = 'new_format/'

def parse_old_to_new(metadata_path=METADATA_PATH):
    det_list = detector_list(metadata_path)

    # some dets have non-zero dl saved under geometry -> save for later since the field will be removed
    dct_dl = {'det_name': [], 'dl_thickness_in_mm': []}

    for det in det_list:
        # print('--------', det)
        js = get_dict(det)
        # f = open(os.path.join(metadata_path, det+'.json'))
        # js = order_dict(json.load(f))
        # js = MyOrderedDict(json.load(f))
        # pprint.pprint(js, indent=1)
        # return

        ## remove char data path and ELOG URL
        js['characterization']['l200_site'].pop('data')
        js['characterization']['l200_site'].pop('elog')

        ## rename "det_name" to "name"
        js.rename('det_name', 'name')
        js.move_to_end('name', last=False)
        # sanity check
        if js['name'] != det:
            print('Detector json field name ({}) is not the same as filename ({})!'.format(js['name'], det))
            return

        ## descriptive names
        js['geometry'].rename('bottom_cyl', 'bottom_cylinder')
        # !! not sure still if this will move under char/l200_site
        js['production'].rename('dep_voltage_in_V', 'depletion_voltage_in_V')
        js['production'].rename('rec_voltage_in_V', 'recommended_voltage_in_V')
        js['characterization']['manufacturer'].rename('dep_voltage_in_V', 'depletion_voltage_in_V')
        # change opV to recV to follow the same format as L200 result
        js['characterization']['manufacturer'].rename('op_voltage_in_V', 'recommended_voltage_in_V')
        js['characterization']['l200_site'].rename('res', 'fwhm')
        js['characterization']['l200_site'].rename('sf', 'survival_fraction')

        js['characterization']['manufacturer'].rename('57co_fep_res_in_keV', 'fwhm_co57fep_in_keV')
        js['characterization']['manufacturer'].rename('60co_fep_res_in_keV', 'fwhm_co60fep_in_keV')

        ## move mass from "geometry" to "production"
        js['production']['mass_in_g'] = js['geometry']['mass_in_g']
        del js['geometry']['mass_in_g']
        # move mass to be after "reprocessing"
        js['production'].move_to_end('mass_in_g', last=False)
        for key in ['reprocessing', 'enrichment', 'slice', 'crystal', 'serialno', 'order', 'manufacturer']:
            js['production'].move_to_end(key, last=False)

        ## remove dead layer from "geometry" -> wait, some are non-zero!? -> for BEGes only
        dl = 'dl_thickness_in_mm'
        # some dets don't have this field
        if dl in js['geometry']:
            # check if non-zero to save for later
            if js['geometry'][dl] > 0:
                dct_dl['det_name'].append(det)
                dct_dl[dl].append(js['geometry'][dl])
            # remove
            del js['geometry'][dl]
        else:
            print('{} missing dl field'.format(det))

        ## date format from DD-MM-YYYY to YYYY-MM-DD
        # some detectors had "" in the "delivered" field -> missing info should be listed as null
        if js['production']['delivered'] == '':
            js['production']['delivered'] = None # will convert to null when written
        else:
            dd, mm, yyyy = js['production']['delivered'].split('-')
            js['production']['delivered'] = '-'.join([yyyy,mm,dd])

        ## missing values as null

        if js['production']['enrichment'] == 0:
            print('{} enrichment info is missing!'.format(det))
            js['production']['enrichment'] = None

        if js['production']['depletion_voltage_in_V'] == 0:
            print('{} char site depV info is missing!'.format(det))
            js['production']['depletion_voltage_in_V'] = None

        for v in ['depletion_voltage_in_V', 'recommended_voltage_in_V']:
            if js['characterization']['manufacturer'][v] == 0:
                print('Detector {} has no {} info from vendor'.format(det, v))
                if 'rec' in v:
                    print("Some vendors do not give depV, but must have recV!")
                    return
                js['characterization']['manufacturer'][v] = None

        for src in ['fwhm_co57fep_in_keV', 'fwhm_co60fep_in_keV']:
            if js['characterization']['manufacturer'][src] == 0:
                js['characterization']['manufacturer'][src] = None

        for src in ['cofep_in_keV', 'tlfep_in_keV', 'qbb_in_keV']:
            # some detectors have missing FWHM @ Qbb
            if ( not src in js['characterization']['l200_site']['fwhm'] ) or ( js['characterization']['l200_site']['fwhm'][src] == 0 ):
                js['characterization']['l200_site']['fwhm'][src] = None

        for src in ['tldep_in_pc', 'qbb_in_pc', 'tlsep_in_pc', 'tlfep_in_pc']:
            if js['characterization']['l200_site']['survival_fraction'][src] == 0:
                js['characterization']['l200_site']['survival_fraction'][src] = None

        # pprint.pprint(js, indent=1)
        # return

        with open(os.path.join(TEST_PATH, 'detectors', det+'.json'), 'w', encoding='utf-8') as f:
            json.dump(js, f, ensure_ascii=False, indent=2)
        
        # if det[0] not in ['B', 'C', 'P']: return

    ## save the removed non-zero dl info
    df_dl = pd.DataFrame(dct_dl)
    df_dl.to_csv(dl + '.csv', index=False, header=True)
    print('Dl info from geometry is saved to' + dl + '.csv')


def crystal_json():
    ## for now just start with ICPCs, because I have impurity information for them, and in general vendor documents
    # list of ICPC
    det_list = detector_list()
    icpc_list = [x for x in det_list if x[0] == 'V']

    # collect unique crystal names, keep detectors as reference for serialno etc
    crystals = {}
    for det in icpc_list:
        cryst = det[3:6]
        if not cryst in crystals:
            crystals[cryst] = []
        crystals[cryst].append(det)

    # pprint.pprint(crystals)

    for cry in crystals:
        print('----- ' + cry)
        dct = OrderedDict({})
        dct['name'] = cry

        ## serialno
        # get serialno from detectors
        serialno = []; order = []; enr = []
        for det in crystals[cry]:
            # detector serialno (usually contains slice A/B at the end, V10 does not)
            det_js = get_dict(det)
            det_serialno = det_js['production']['serialno']
            cry_serialno = det_serialno[:-1] if det_serialno[-1] in ['A', 'B'] else det_serialno
            serialno.append(cry_serialno)
            enr.append(det_js['production']['enrichment'])
            order.append(det[:3])

        serialno = np.unique(serialno)
        order = np.unique(order)
        enr = np.unique(enr)
        # sanity check: should be unique -> passed sanity check after some corrections of detector jsons with wrong serialno
        # print(crystals[cry])
        # print(serialno)
        # if len(serialno) > 1:
            # print ('More than one serialno for detectors based on same crystal!')
            # return
        if len(enr) > 1:
            print('More than one enrichment for detectors based on the same crystal!')

        dct['serialno'] = serialno[0]

        ## enrichment
        # no info for ICPC, yes for other types
        dct['enrichment'] = None if enr[0] == 0 else enr[0]

        ## detector Z=0 position in crystal
        # crystal is shaved, so there is offset, not just slice A + slice B = crystal
        # check David Radford's config files to figure it all out

        ## impurity measurements: done once
        # !! BE CAREFUL DO NOT OVERWRITE PAINSTAKING MANUAL IMPURITY INPUTS
        # create template, have to fill by hand from spreadsheets
        # dct['impurity_measurements'] = OrderedDict({})
        # dct['impurity_measurements']['value_in_1e9e_cm3'] = []
        # dct['impurity_measurements']['distance_from_seed_end_mm'] = []

        ## impurity profile
        dct['final_impurity_curve'] = OrderedDict({})
        funcs = {
            'polynomial': ['a0', 'a1', 'a2'],
            'empirical': ['a', 'b', 'c', 'tau']
        }
        for f in funcs:
            dct['final_impurity_curve'][f] = OrderedDict({})
            for param in funcs[f]:
                dct['final_impurity_curve'][f][param] = None

        ## save file
        with open(os.path.join(TEST_PATH, 'crystals', order[0] + cry+'.json'), 'w', encoding='utf-8') as f:
            json.dump(dct, f, ensure_ascii=False, indent=2)





    # print(crystals)

# --------------------------------

class MyOrderedDict(OrderedDict):

    # def rename(self, key_old, key_new):
    #     self[key_new] = self.pop(key_old)
    #     # self[key_new] = self[key_old]
    #     # del self[key_old]

    def rename(self, key_old, key_new):
        for _ in range(len(self)):
            k, v = self.popitem(False)
            self[key_new if key_old == k else k] = v

# --------------------------------
# helper functions
# --------------------------------

def order_dict(dct):
    ''' make nested OrderedDict '''

    for key in dct:
        if type(dct[key]) == dict:
            dct[key] = order_dict(dct[key])

    return MyOrderedDict(dct)


def get_dict(det_name, metadata_path=METADATA_PATH):
    f = open(os.path.join(metadata_path, det_name+'.json'))
    # return OrderedDict(json.load(f))
    return order_dict(json.load(f))


def detector_list(metadata_path=METADATA_PATH):
    '''
    (string, int, list) -> list

    Return list of detector names from legend-metadata folder

    metadata_path [string]: path to folder with detector metadata jsons
    max_order [int]: maximum order to plot (default all orders)
    det_type [list]: detector types to analyze, V=ICPC, B=BEGe, P=PPC, C=Coax (semi-coax)

    >>> detector_list('legend-detectors/germanium/detectors/', 10, ['V'])
    ['V00048A', 'V00048B', ..., 'V09374A', 'V09724A', 'V10784A']

    '''
    det_list = [x.split('.')[0] for x in os.listdir(metadata_path) if '.json' in x]
    det_list.sort()
    return det_list

parse_old_to_new()
# crystal_json()