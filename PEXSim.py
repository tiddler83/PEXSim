import re


def remove_backslash(e):
    x = e.replace(r'\<', '<')
    x = x.replace(r'\>', '>')
    return x


def remove_forwardslash(e):
    x = e.replace('\\', '')
    return x


def net_related_q(net_name0, net_name1):
    return re.match(conv_net_name(net_name0) + r'_(.+)', net_name1)


def conv_net_name(netName):
    x = netName.split('/')
    if len(x) > 1:
        x[0:-1] = list(map(lambda x: "X" + x, x[0:-1]))
    return '/'.join(x)


def device_related_q(device0, device1):
    return re.match(device0, device1)


def find_all_related_nets(net_name, nets_set):
    res = []
    for e in nets_set:
        if net_related_q(net_name, e):
            res.append(e)
    return res


def splitDeviceAndTerminalName(terminal_name):
    return terminal_name.split(":")


def find_all_related_terminal(terminal_name, device_set):
    [deviceName, terminalName] = splitDeviceAndTerminalName(terminal_name)
    res = []
    for e in device_set:
        if device_related_q(deviceName, e):
            res.append(e + ":" + terminalName)
    return res


def find_all_related_nets_for_aListOfNets(net_list_to_be_probed, net_set):
    res = []
    for e in net_list_to_be_probed:
        f = find_all_related_nets(e, net_set)
        res += f
        net_set -= set(f)
    return res


def find_all_related_terminal_for_aListOfDevices(terminal_list_to_be_probed, device_set):
    res = []
    for e in terminal_list_to_be_probed:
        f = find_all_related_terminal(e, device_set)
        res += f
        device_set -= set(f)
    return res


def extract_all_nets_name_from_netlist(moduleList, PEXNetlistDirPath):
    res = {}
    for e in moduleList:
        file = PEXNetlistDirPath + '/' + e + '.spectre.pex.netlist'
        file = file.replace('//', '/')
        with open(file, 'r') as fh:
            cont = fh.read()
        target = re.compile(r'N_(.+?) ')
        res[e] = re.findall(target, cont)
        res[e] = set(res[e])
        res[e] = set(map(remove_backslash, res[e]))
        res[e] = set(map(remove_forwardslash, res[e]))
    return res


def extract_all_devices_from_netlist(moduleList, PEXNetlistDirPath):
    res = {}
    for e in moduleList:
        file = PEXNetlistDirPath + '/' + e + '.spectre.pex.netlist'
        file = file.replace('//', '/')
        with open(file, 'r') as fh:
            cont = fh.read()
        target = re.compile(r'X(.+?) \(')
        res[e] = target.findall(cont)
        res[e] = set(map(lambda x: "X" + x, res[e]))
        res[e] = set(map(remove_backslash, res[e]))
        res[e] = set(map(remove_forwardslash, res[e]))
    return res


def removeDupInList(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


def split_top_module_name(net):
    x = net.split('/', 2)
    if len(x)>2:
        return (x[1], x[2])
    else:
        return (x[0], x[1])


def split_top_module_name_forTerminal(term):
    x = term.split('/', 1)
    return (x[0], x[1])


def transform_nets_name_into_spectre_netlist_convention(net_name):
    replacements = {'/': r'\\/', '<': r'\\<', '>': r'\\>'}
    return multireplace(net_name, replacements)
    # return net_name.replace('/', r'\/').replace('<', r'\\<').replace('>', r'\\>')


def parse_bus_net_name(bus):
    p = re.compile(r'(.+?)<(\d+):(\d+)')
    s = p.match(bus)
    net_name = s.group(1)
    first_num = int(s.group(2))
    sec_num = int(s.group(3))
    res = []
    for i in range(first_num, sec_num+1):
        a = net_name + "<" + str(i) + ">"
        res.append(a)
    return res


termName = {'D': 'd', 'G': 'g', 'S': 's', 'B': 'b'}


def conv_term_name(term):
    x = term.split('/')
    if len(x) > 3:
        x = [x[1]] + list(map(conv_term_name_helper, x[2:-1])) + [termName.get(x[-1], x[-1])]
        x[1] = "X" + x[1]
        return '/'.join(x[:-1]) + ':' + x[-1]
    elif len(x) == 3:
        return '/' + x[1] + ':' + x[2]


def conv_term_name_helper(name):
    if name.startswith('I'):
        return "X" + name
    elif name.startswith('T'):
        return "M" + name
    elif name.startswith('C'):
        return "C" + name
    elif name.startswith('R'):
        return "R" + name
    elif name.startswith('t'):
        return "D" + name


import fileinput
def modifySaveInOceanScript(vList, iList, oceanScriptFileName):
    pTemp = re.compile(r'temp\((.+?)\)')
    vList1 = list(map(lambda x: "\"" + x + "\" ", vList))
    iList1 = list(map(lambda x: "\"" + x + "\" ", iList))
    saveV = "save( \'v " + "\\\n".join(vList1) + ")"
    saveI = "save( \'i " + "\\\n".join(iList1) + ")"
    ocnOutputV = list(map(lambda x: "ocnxlOutputSignal( " + x + "?plot t ?save t)", vList1))
    ocnOutputV = '\n'.join(ocnOutputV) + '\n'
    ocnOutputI = list(map(lambda x: "ocnxlOutputTerminal( " + x + "?plot t ?save t)", iList1))
    ocnOutputI = '\n'.join(ocnOutputI) + '\n'
    with open(oceanScriptFileName, 'r') as fh:
        cont = fh.read()
    cont = cont.replace('\r', '')
    r = re.compile(r'save\((.+?)\)\n' + r'|' + r'ocnxlOutputSignal\((.+?)\)\n' + r'|' + r'ocnxlOutputTerminal\((.+?)\)\n', re.DOTALL)
    cont = r.sub('', cont, 0)

    cont = cont.split('\n')
    contNew = []
    for line in cont:
        if re.match(pTemp, line):
            contNew.append(saveV + '\n' + saveI + '\n' + line + '\n' + ocnOutputV + ocnOutputI)
        else:
            contNew.append(line)
    with open(oceanScriptFileName, 'w') as fh:
        fh.write('\n'.join(contNew))


def modifyTestBenchNetlistFileNameInOceanScript(testBenchNetlistFileName, oceanScriptFileName):
    for line in fileinput.FileInput(oceanScriptFileName, inplace=1):
        if line.startswith('design('):
            print('design( \"' + testBenchNetlistFileName + '\" )')
        else:
            print(line.rstrip())


def groupNetTermNameAccToInst(net_list):
    res = {}
    for e in net_list:
        if e[0] not in res:
            res[e[0]] = [e[1]]
        else:
            res[e[0]].append(e[1])
    return res


def parseParameterFile(fileName):
    res = dict()
    with open(fileName, 'r') as fh:
        cont = fh.read()
    cont = cont.replace('\r', '')

    p_testBenchNetlist_pathFileName = re.compile(r'testBenchNetlist_pathFileName(\s*){(.*?)}')
    p_oceanScript_toBeModified_pathFileName = re.compile(r'oceanScript_toBeModified_pathFileName(\s*){(.*?)}')
    p_moduleName =  re.compile(r'moduleName(\s*){(.*?)}', re.DOTALL)
    p_PEXNetlistDirPath = re.compile(r'PEXNetlistDirPath(\s*){(.*?)}')
    p_saveV = re.compile(r'saveV(\s*){(.*?)}', re.DOTALL)
    p_saveI = re.compile(r'saveI(\s*){(.*?)}', re.DOTALL)
    p_instance_module_mapping = re.compile(r'instance_module_mapping(\s*){(.*?)}', re.DOTALL)

    res['testBenchNetlist_pathFileName'] = p_testBenchNetlist_pathFileName.search(cont).group(2).strip()

    res['oceanScript_toBeModified_pathFileName'] = p_oceanScript_toBeModified_pathFileName.search(cont).group(2).strip()

    res['moduleName'] = p_moduleName.search(cont).group(2)
    res['moduleName'] = ''.join(res['moduleName'].split()).split(',')

    res['PEXNetlistDirPath'] = p_PEXNetlistDirPath.search(cont).group(2).strip()

    res['instance_module_mapping'] = ''.join(p_instance_module_mapping.search(cont).group(2).split())
    res['instance_module_mapping'] = parseInstanceModuleMapping(res['instance_module_mapping'])

    res['saveV'] = ''.join(p_saveV.search(cont).group(2).split())
    res['saveV'] = parseNetString(res['saveV'])

    res['saveI'] = ''.join(p_saveI.search(cont).group(2).split())
    res['saveI'] = parseTermString(res['saveI'])

    res['saveV'] = list(map(split_top_module_name,  res['saveV']))
    res['saveI'] = list(map(conv_term_name, res['saveI']))
    res['saveI'] = list(map(split_top_module_name_forTerminal, res['saveI']))

    res['saveV'] = groupNetTermNameAccToInst(res['saveV'])
    res['saveI'] = groupNetTermNameAccToInst(res['saveI'])

    return res


def multireplace(string, replacements):
    """
    Given a string and a replacement map, it returns the replaced string.
    :param str string: string to execute replacements on
    :param dict replacements: replacement dictionary {value to find: value to replace}
    :rtype: str
    """
    # Place longer ones first to keep shorter substrings from matching where the longer ones should take place
    # For instance given the replacements {'ab': 'AB', 'abc': 'ABC'} against the string 'hey abc', it should produce
    # 'hey ABC' and not 'hey ABc'
    substrs = sorted(replacements, key=len, reverse=True)

    # Create a big OR regex that matches any of the substrings to replace
    regexp = re.compile('|'.join(map(re.escape, substrs)))

    # For each match, look up the new string in the replacements
    return regexp.sub(lambda match: replacements[match.group(0)], string)


def parseNetString(v):
    v = v.split(',')
    v_ = []
    for e in v:
        if e.find(":") != -1:
            x = parse_bus_net_name(e)
            v_ = v_ + x
        else:
            v_.append(e)
    v_ = removeDupInList(v_)
    return v_


def parseTermString(i):
    i = i.split(',')
    i = removeDupInList(i)
    return i


def parseInstanceModuleMapping(x):
    res = {}
    x = x.split(',')
    for e in x:
        a = e.split(':')
        res[a[0]] = a[1]
    return res


def netsToProbeInSpectreFormat(netsToProbe, allNets, instance_module_mapping):
    saveV = {}
    for (k,v) in netsToProbe.items():
        if k != '':
            saveV[k] = find_all_related_nets_for_aListOfNets(netsToProbe[k], allNets[instance_module_mapping[k]])
            saveV[k] = list(map(transform_nets_name_into_spectre_netlist_convention, saveV[k]))
            saveV[k] = list(map(lambda x: k + ".N_"+x, saveV[k]))
        else:
            saveV[k] = list(map(lambda x: "/" + x, netsToProbe[k]))

    vList = []
    for (k, v) in saveV.items():
        vList = vList + v

    return vList


def termsToProbeInSpectreFormat(termsToProbe, allDevices, instance_module_mapping):
    saveI = {}
    for (k, v) in termsToProbe.items():
        if k != '':
            saveI[k] = find_all_related_terminal_for_aListOfDevices(termsToProbe[k], allDevices[instance_module_mapping[k]])
            saveI[k] = list(map(transform_nets_name_into_spectre_netlist_convention, saveI[k]))
            saveI[k] = list(map(lambda x: k + "." + x, saveI[k]))
        else:
            saveI[k] = list(map(lambda x: "/" + x, termsToProbe[k]))

    iList = []
    for (k, v) in saveI.items():
        iList = iList + v

    return iList


def modifyTestbenchNetlistFile(PEXNetlistDirPath, moduleName, testBenchNetlist_pathFileName):
    includePathName = list(map(lambda x: PEXNetlistDirPath + '/' + x + '.spectre.pex.netlist', moduleName))
    for i in range(len(includePathName)):
        includePathName[i] = includePathName[i].replace('//', '/')

    with open(testBenchNetlist_pathFileName, 'r') as fh:
        cont = fh.read()
    cont = cont.replace('\r', '')

    for i in range(len(includePathName)):
        p = re.compile(r'subckt ' + moduleName[i] + r'(.+?)ends ' + moduleName[i] + r'\n',  re.DOTALL)
        cont = p.sub('include \"' + includePathName[i] + '\"\n', cont,0)

    with open(testBenchNetlist_pathFileName, 'w') as fh:
        fh.write(cont)

