# detector_plots
 
 Collection of scripts to plot parameters from detector metadata json based on `legend-detectors/germanium/detectors/` format.
 The path to the folder containing detector jsons is defined on top of `info_table.py` and used as default in `info_table()` in the plotting functions.
 Note that the format is subject to change. This repo will be updated and a note will be send once the transition to new format is complete.
 
 See function doc strings for more details.
 
## Table with detector info
 
The script `info_table.py` contains a function `info_table()` that reads the metadata of detectors of given type from the metadata folder, and constructs a `pd.DataFrame` with columns corresponding to given parameters.
Define path to your local detector json folder in `METADATA_PATH` on top of `info_table.py`.
 
 Detector types
```
 V		ICPC
 B		BEGe
 P		PPC
 C		Coax (semi-coax)
``` 

The parameter paths within jsons are defined in `JSON_FIELDS`.
 
*Example*
 
```python
info_table(['mass', 'fwhm_Qbb'], 'legend-detectors/germanium/detectors/', ['B'])
```
 
```
        det_name  order   mass  fwhm_Qbb
    0   B00000A      0  xxx      xxx
    1   B00000B      0  xxx      xxx
    2   B00000C      0  xxx      xxx
    ...
    27  B00091B      0  xxx      xxx
    28  B00091C      0  xxx      xxx
    29  B00091D      0  xxx      xxx
```

Some plotting script examples are provided as well (see below)

## Plot parameter VS detector

The `params_vs_det()` function in `param_vs_det.py` plots given parameter values VS detector names.
Multiple parameters can be plotted when needed e.g. comparing measured depletion voltages and values provided by vendor. The labels and symbols in this case are defined on top of `param_vs_det.py`.
In case of ICPCs (`det_type=['V']`), the detectors are grouped by order (see `plots/det_typeV_depV-depV_man.pdf`).

*Example*

```python
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
``` 

## Detector pie chart

The `det_pie.py` script plots a pie chart of current status of L200 detector production. The function `det_pie()` takes no variable as it plots the mass of all detector types.

Example

```python
>>> det_pie()
    total number of detectors: xxx
    total mass: xxx kg
    ----BEGe (GERDA)
    N detectors - xxx kg
    ----Coax (GERDA)
    N detectors - xxx kg
    ----ICPC (GERDA)
    N detectors - xxx kg
    ----ICPC (new)
    N detectors - xxx kg
    ----PPC (MJD)
    N detectors - xxx kg
    leftover: xxx kg
                   mass    color                             label
    det_type
    BEGe (GERDA)     xx  #2ca02c  BEGe (GERDA)\n30 detectors\nxxkg
    Coax (GERDA)     xx  #9467bd   Coax (GERDA)\n6 detectors\nxxkg
    ICPC (GERDA)     xx  #1f77b4   ICPC (GERDA)\n5 detectors\nxxkg
    ICPC (new)       xx  #07a9ff    ICPC (new)\n42 detectors\nxxkg
    ICPC (planned)   xx  #cccccc              ICPC (planned)\nxxkg
    PPC (MJD)        xx  #ff7f0e     PPC (MJD)\n33 detectors\nxxkg
    Saving as plots/L200_detector_pie.pdf
```
