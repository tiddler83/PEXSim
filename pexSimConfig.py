import sys
import os
sys.path.append(os.getcwd())
from PEXSim import *

par = parseParameterFile('parameterFileForPEXSim_top13_tb')
# par = parseParameterFile(sys.argv[1])

allNets = extract_all_nets_name_from_netlist(par['moduleName'], par['PEXNetlistDirPath'])
allDevices = extract_all_devices_from_netlist(par['moduleName'], par['PEXNetlistDirPath'])


vList = netsToProbeInSpectreFormat(par['saveV'], allNets, par['instance_module_mapping'])
iList = termsToProbeInSpectreFormat(par['saveI'], allDevices, par['instance_module_mapping'])

#
# modifyTestbenchNetlistFile(par['PEXNetlistDirPath'], par['moduleName'], par['testBenchNetlist_pathFileName'])
# modifySaveInOceanScript(vList, iList, par['oceanScript_toBeModified_pathFileName'])
# modifyTestBenchNetlistFileNameInOceanScript(par['testBenchNetlist_pathFileName'], par['oceanScript_toBeModified_pathFileName'])