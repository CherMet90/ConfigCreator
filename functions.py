import re
import csv
import os
from classes import Port, Vlan


def prepare(origin):
    portList = []
    portKeys = ['Port', 'Description', 'ServiceType']
    vlanList = []
    vlanKeys = ['VlanName', 'VlanID', 'untag', 'tag']
    
    if origin is not 'new':
        with open('data/' + origin, 'r') as file:
            for line in file:
                matchSingle = re.search(
                    r'config ports (?P<port>\d*).* state enable.*description "*(?P<desc>|[^\"\n\$]*)("|$)', line)
                matchSome = re.search(
                    r'config ports \d,(?P<port>\d*).*state enable.*description "*(?P<desc>|[^\"\n\$]*)("|$)', line)
                matchRange = re.search(
                    r'config ports (?P<startRange>\d*)-(?P<endRange>\d*).*state enable.*description "*(?P<desc>|[^\"\n\$]*)("|$)',
                    line)
    
                matchCreate = re.match(r'create vlan "*(?P<name>|[^\"\n\$]*)"* tag (?P<id>\d*)', line)
                matchUntag = re.match(r'config vlan \S+ add untag\S*(?P<ports> \S+)', line)
                matchTag = re.match(r'config vlan \S+ add tag\S*(?P<ports> \S+)', line)
                try:
                    #--- Порты ---
                    if matchSingle is not None and matchRange is None:
                        portList.append(Port(matchSingle.group('port'), matchSingle.group('desc')))
                    if matchSome is not None:
                        portList.append(Port(matchSome.group('port'), matchSome.group('desc')))
                    if matchRange is not None:
                        for i in range(int(matchRange.group('startRange')), int(matchRange.group('endRange')) + 1):
                            portList.append(Port(i, matchSingle.group('desc')))
    
                    # --- Вланы ---
                    if matchCreate is not None:
                        vlanList.append(Vlan(matchCreate.group('name'), matchCreate.group('id')))
                    if matchUntag is not None:
                        vlanList[-1].add_untag(matchUntag.group('ports'))
    
                    if matchTag is not None:
                        vlanList[-1].add_tag(matchTag.group('ports'))
                except AttributeError:
                    pass

    with open('data/ports.csv', 'w', newline='') as file:
        writer = csv.DictWriter(file, delimiter=';', fieldnames=portKeys)
        writer.writeheader()
        for i in portList:
            writer.writerow({portKeys[0]: i.number, portKeys[1]: i.description, portKeys[2]: i.service})

    with open('data/vlans.csv', 'w', newline='') as file:
        writer = csv.DictWriter(file, delimiter=';', fieldnames=vlanKeys)
        writer.writeheader()
        for i in vlanList:
            writer.writerow({vlanKeys[0]: i.name, vlanKeys[1]: i.vlan_id, vlanKeys[2]: i.untagged, vlanKeys[3]: i.tagged})

def getMarks(template, mark, origin=''):
    if mark == '[]':
        SquareBracketList_dupl = re.findall(r'\[(.*?)\]', template)
        SquareBracketList = list(set(SquareBracketList_dupl))
        return SquareBracketList
    if mark == '{}':
        CurlyBracketList_dupl = re.findall(r'({.*?})', template)
        CurlyBracketList = list(set(CurlyBracketList_dupl))
        return CurlyBracketList
    if mark == '**':
        for lineTemplate in template.split('\n'):
            match = re.search(r'\*(?P<cmd>.*?)\*', lineTemplate)
            if match is not None:
                with open('data/' + origin, 'r') as cfg:
                    counter = 0
                    for lineCFG in cfg:
                        if lineCFG.startswith(match.group('cmd')):
                            print(lineCFG)
                            template = template.replace(lineTemplate, lineCFG)
                            counter += 1
                    if counter == 0:
                        template = template.replace(lineTemplate, '\n')
                            
                
        return template
                    
    
'''        
prepare('10.1.6.32.DES-3200-28')
os.startfile(r'vlans.csv')
input()
'''
