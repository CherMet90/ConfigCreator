import re
import csv
import functions
import os
import colorama
from classes import Port, Vlan
from colorama import Fore, Back, Style

vlanList =[]

colorama.init()
#resultConfigName = 'test-sw01.txt'
#origin = '10.1.6.32.DES-3200-28'

#--- Ф-ция получения списка с метками ---
def dictSearch(dictList, value: str):
    listMatch = []
    for port in dictList:
        if port.service == value:
            listMatch.append(port.number)
    return listMatch


#--- Чтение файла шаблона в объект ----
with open('data/template.txt', 'r') as file:
    filedata = file.read()

#--- Выбор режима работы скрипта ---
mode = input('Введите режим работы скрипта (new/old)\n'
             'new - создание конфигурации "с нуля"\n'
             'old - создание конфигурации на основе имеющегося конфига:\n')
resultConfigName = input('Имя генерируемого конфига (с указанием расширения файла): ')

#--- Режим создания конфига "с нуля" ---
if mode == 'new':

    #--- Удаление звездочек ---
    startMark = filedata.find('---')
    filedataFirstPart = filedata[:startMark]
    filedataSecondPart = filedata[startMark:]
    filedataSecondPart = filedataSecondPart.replace('*','')
    filedata = filedataFirstPart + filedataSecondPart
        
    #--- Вызов функции получения данных из файла конфигурации ---
    origin = 'new'
    a = functions.prepare(origin)
    
#--- Режим создания конфига на основе существующего ---
elif mode == 'old':
    origin = input('Введите имя исходного конфига в папке data (с указанием расширения файла): ')
    a = functions.prepare(origin)

#--- Обработка строк с ** ---
filedata = functions.getMarks(filedata, '**', origin)
functions.controlVlanSearch(a)

#--- Обработка меток в {} ---
switchMarksList = functions.getMarks(filedata, '{}')
for i in switchMarksList:
    filedata = filedata.replace(i, input('Введите данные для ' + i + ': '))
        
#--- Получение данных из ports.csv ---
while True:
    portList = []
    os.startfile(r'data\ports.csv')
    input('\nЗаполните столбец ServiceType (l2, l3, trunk, sw, uplink)'
        '\nПри необходимости можно добавить в список новые порты'
        '\nДля сохранения изменений используйте CTRL+S, от сохранения при закрытии откажитесь'
        '\nНажмите Enter для продолжения... ')
    print('\n')
    with open('data/ports.csv', 'r') as file:
        reader = csv.DictReader(file, delimiter=';')
        for row in reader:
            portList.append(Port(row['Port'], row['Description'], row['ServiceType']))
    
    #--- Обработка метки <ports> ---
    configPorts = []
    critEvent = False
    warnEvent = False
    for i in portList:
        descLen = len(i.description)
        if descLen > 32:
            critEvent = True
            print(Fore.WHITE + Back.RED + 
                'Длина дескриптора порта ' + str(i.number) + ' превышает допустимую! Текущая длина: ' + str(descLen))
        elif descLen > 20:
            warnEvent = True
            print(Fore.BLACK + Back.YELLOW + 
                'Длина дескриптора порта ' + str(i.number) + ' превышает 20 символов. Текущая длина: ' + str(descLen))
        configPorts.append(i.create_port())
    
    if critEvent is True or warnEvent is True:
        print(Style.RESET_ALL)
        print('Максимальная длина: 32 символа (20 - для DGS-1100)')
        
    if critEvent is False:
        break
filedata = filedata.replace('<ports>', "".join(configPorts))

#--- Обработка меток в [] ---
portMarksList = functions.getMarks(filedata, '[]')
for i in portMarksList:
    marksList_splitted = i.split(' ')
    matchedPorts = []
    for j in marksList_splitted:
        matchedPorts.extend(dictSearch(portList, j))
        matchedPorts = [str(k) for k in matchedPorts]
    filedata = filedata.replace('[' + i + ']', ",".join(matchedPorts))
    
#--- Получение данных из vlans.csv ---
while True:
    vlanList = []
    os.startfile(r'data\vlans.csv')
    input('\nПроверьте и при необходимости отредактируйте таблицу vlans'
        '\nДля сохранения изменений используйте CTRL+S, от сохранения при закрытии нужно отказаться'
        '\nНажмите Enter для продолжения... ')
    print('\n')
    with open('data/vlans.csv', 'r') as file:
        reader = csv.DictReader(file, delimiter=';')
        for row in reader:
            vlanList.append(Vlan(row['VlanName'], row['VlanID'], row['untag'], row['tag']))
        
    #--- Обработка метки <vlans> ---
    configVlans = []
    critEvent = False
    warnEvent = False
    for i in vlanList:
        descLen = len(i.name)
        if descLen > 32:
            critEvent = True
            print(Fore.WHITE + Back.RED + 
                'Имя влана ' + str(i.vlan_id) + ' превышает допустимую длину! Текущая длина: ' + str(descLen))
        elif descLen > 20:
            warnEvent = True
            print(Fore.BLACK + Back.YELLOW + 
                'Имя влана ' + str(i.vlan_id) + ' превышает 20 символов. Текущая длина: ' + str(descLen))
        configVlans.append(i.create_vlan())
        
    if critEvent is True or warnEvent is True:
        print(Style.RESET_ALL)
        print('Максимальная длина: 32 символа (20 - для DGS-1100)')
        
    if critEvent is False:
        break
filedata = filedata.replace('<vlans>', "".join(configVlans))
    
#--- Сохранение всех результатов в новый файл и удаление технологических меток ---
filedata = filedata.replace('---', '')
with open('data/' + resultConfigName, 'w') as file:
    file.write(filedata)

os.startfile(r'data\\' + resultConfigName)
