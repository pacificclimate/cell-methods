# The functions in this file are helpers for the PCEX backend.

from cf_cell_methods import parse
# Used by the climate explorer backend to filter datasets
# PCEX cares about what the LAST cell method is, as this records the type
# of statistical data used the dataset. Generally users selecting a dataset
# to view are offered the choice of all datasets representing climatological
# means and ensemble means, for whom the last cell method will be a mean 
# calculation. 
# Datasets representing other statistical calculations - percentiles and 
# standards deviations - are present in the database to be used to provide
# additional context to the dataset selected by the user. They are handled
# differently by the PCEX backend.
# Some example final cell methods:
#     * time: mean over days (a climatological mean - user can view this)
#     * time: standard_deviation over days (a climatological SD - used for context)
#     * models: mean (PCIC12 climatologies - user can view this)
#     * models: percentile[n] (hydrology percentile data - used for context)
# Since PCEX treats means over model ensembles and means over time identically, 
# all the backend needs to know is the last cell method - "mean", "standard_deviation",
# "percentile", or other / None. 
def final_operation(cell_method):
    try:
        cm = parse(cell_method)
        method_str = cm[-1].method.name
        #strip percentile bonus information if present
        return method_str.split("[")[0]
    except: # PCEX has noisy data, handle unparsable
        return None