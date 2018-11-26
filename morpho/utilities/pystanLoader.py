'''
Definitions for interfacing with pyStan IO
Authors: M. Guigue
Date: 06/26/18
'''

from morpho.utilities import morphologging
logger = morphologging.getLogger(__name__)


def extract_data_from_outputdata(conf, theOutput):
    # Extract the data into a dictionary
    logger.debug("Extracting samples from pyStan output")
    theOutputDiagnostics = theOutput.get_sampler_params(inc_warmup=True)
    diagnosticVariableName = ['accept_stat__', 'stepsize__',
                              'n_leapfrog__', 'treedepth__', 'divergent__', 'energy__']
    theOutputData = theOutput.extract(permuted=False, inc_warmup=True)

    logger.debug("Transformation into a dict")
    nEventsPerChain = len(theOutputData)
    # get the variables in the Stan4Model
    flatnames = theOutput.flatnames
    # add the diagnostic variable names
    flatnames.extend(diagnosticVariableName)
    # make list of desired variables
    desired_var = []
    for a_name in flatnames:
        for a_key in conf['interestParams']:
            # this means the desired var is a list
            if a_name.startswith(a_key+'[') or a_name == a_key:
                desired_var.append(a_name)

    # Clustering the data together
    theOutputDataDict = {}
    for key in desired_var:
        theOutputDataDict.update({str(key): []})
    for key in diagnosticVariableName:
        theOutputDataDict.update({str(key): []})
    theOutputDataDict.update({"lp_prob": []})
    theOutputDataDict.update({"delta_energy__": []})
    theOutputDataDict.update({"is_sample": []})

    for iChain in range(0, conf['chains']):
        for iEvents in range(0, nEventsPerChain):
            for iKey, key in enumerate(flatnames):
                if key in diagnosticVariableName:
                    theOutputDataDict[str(key)].append(
                        theOutputDiagnostics[iChain][key][iEvents])
                else:
                    if key in desired_var:
                        theOutputDataDict[str(key)].append(
                            theOutputData[iEvents][iChain][iKey])
            if iEvents is not 0:
                theOutputDataDict["delta_energy__"].append(
                    theOutputDiagnostics[iChain]['energy__'][iEvents]-theOutputDiagnostics[iChain]['energy__'][iEvents-1])
            else:
                theOutputDataDict["delta_energy__"].append(0)
            theOutputDataDict["lp_prob"].append(
                theOutputData[iEvents][iChain][len(theOutput.flatnames)])
            theOutputDataDict["is_sample"].append(
                0 if iEvents < conf['warmup'] else 1)

    # Add all stan summaries in output dictionary
    mean = {}
    se_mean = {}
    sd = {}
    n_eff = {}
    Rhat = {}
    for iKey, key in enumerate(flatnames):
        if key in desired_var:
            mean[str(key)] = theOutput.summary(pars=str(key))['summary'][0][0]
            se_mean[str(key)] = theOutput.summary(pars=str(key))['summary'][0][1]
            sd[str(key)] = theOutput.summary(pars=str(key))['summary'][0][2]
            n_eff[str(key)] = theOutput.summary(pars=str(key))['summary'][0][8]
            Rhat[str(key)] = theOutput.summary(pars=str(key))['summary'][0][9]

    theOutputDataDict["mean"] = mean
    theOutputDataDict["se_mean"] = se_mean
    theOutputDataDict["sd"] = sd
    theOutputDataDict["n_eff"] = n_eff
    theOutputDataDict["Rhat"] = Rhat

    return theOutputDataDict
