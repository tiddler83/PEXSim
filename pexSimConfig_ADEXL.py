import sys
import os
sys.path.append(os.getcwd())
from PEXSim import *

# par = parseParameterFileForADEXL('parameterFileForPEXSimADEXL.txt')
par = parseParameterFileForADEXL(sys.argv[1])

allNets = extract_all_nets_name_from_netlist(par['moduleName'], par['PEXNetlistDirPath'])
allDevices = extract_all_devices_from_netlist(par['moduleName'], par['PEXNetlistDirPath'])


vList = netsToProbeInSpectreFormatForADEXL(par['saveV'], allNets, par['instance_module_mapping'])
iList = termsToProbeInSpectreFormatForADEXL(par['saveI'], allDevices, par['instance_module_mapping'])

createSavescs(vList, iList, par['savescsPath'])