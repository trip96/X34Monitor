import PySimpleGUI as sg
import minimalmodbus
import datetime
import subprocess
import os
import serial.tools.list_ports


def findComPort():
    comList = serial.tools.list_ports.comports()
    connected = []
    for element in comList:
        connected.append(element.device)
    return connected


def createProjPath():
    if os.path.exists(r'c:\ControllerTests') == False:
        os.mkdir(r'c:\ControllerTests')
    else:
        pass


def writeHeaders(sendDataList, devID):
    try:
        for i in range(len(sendDataList)):
            try:
                f.write(sendDataList[i] + devID + ",")
            except ValueError:
                pass
    except PermissionError:
        print("Could NOT open/write to file. Please check if it is open or being used by another program.")
        exit()


def queryController1(sendDataList, parsedData):

    for i in range(len(sendDataList)):
        try:
            payLoad = instrument1.read_register(int(sendDataList[i], 16), 1)
            print(payLoad)
            parsedData = str(parsedData) + str(payLoad) + ","
        except ValueError:
            print("Hex Parameter: " + sendDataList[i] + " NOT recognized by Controller")
            parsedData = str(parsedData) + "N/A" + ","
            pass
        except IOError:
            parsedData = str(parsedData) + "I/O Err" + ","
            print('I/O error - Device slave ID NOT found')
            pass

    return parsedData


def queryController2(sendDataList, parsedData):

    for i in range(len(sendDataList)):
        try:
            payLoad = instrument2.read_register(int(sendDataList[i], 16), 1)
            print(payLoad)
            parsedData = str(parsedData) + str(payLoad) + ","
        except ValueError:
            print("Hex Parameter: " + sendDataList[i] + " NOT recognized by Controller")
            parsedData = str(parsedData) + "N/A" + ","
            pass
        except IOError:
            parsedData = str(parsedData) + "I/O Err" + ","
            print('I/O error - Device slave ID NOT found')
            pass

    return parsedData


def scheduler(startDate, endDate):

    while True:
        countDown = round((datetime.datetime.now() - datetime.datetime.strptime(startDate,
                                                                          '%Y-%m-%d %H:%M:%S')).total_seconds(), 0)
        if countDown < 0:
            print('Waiting to start in T ' + str(countDown) + ' seconds\n\n')
            if sg.PopupOKCancel('Starting at ' + values['startDate'] + '\n\nStarting in T' + str(countDown) +
                                ' seconds\n\nPress OK to update Countdown\n', auto_close=True,
                                auto_close_duration=int(abs(countDown))) is 'Cancel':
                break
        else:
            pass

        if datetime.datetime.now() > datetime.datetime.strptime(endDate, '%Y-%m-%d %H:%M:%S'):
            jobDone()
            break
        elif datetime.datetime.now() > datetime.datetime.strptime(startDate, '%Y-%m-%d %H:%M:%S'):
            return True


def getMaxScheduleTime():
    maxSchedTime = round(((datetime.datetime.strptime(values['endDate'], '%Y-%m-%d %H:%M:%S') -
                           datetime.datetime.strptime(values['startDate'], '%Y-%m-%d %H:%M:%S')).total_seconds()), 0)
    return maxSchedTime


def jobDone():
    sg.PopupNonBlocking('Test Stopped! \n\nData located in:\nC:/ControllerTests\n')

    # Auto open folder location.

    subprocess.Popen(r'explorer /select,"C:\ControllerTests\"' + projectNameInput +
                     "-" + str(datetime.date.today()) + ".csv")


# GUI Code PySimpleGUI

layout = [[sg.Image('mftlogo.png'), sg.Text('Rev.03')],
          [sg.Text('_' * 100, size=(70, 1))],
          [sg.Text('Project Settings:', size=(30, 2), font=("arial", 12), text_color='Black')],
          [sg.Text('Project Name: '), sg.InputText(key='projectName')],
          [sg.Text('_' * 100, size=(70, 1))],
          [sg.Text('Device Settings:', size=(30, 2), font=("arial", 12), text_color='Black')],
          [sg.Text('COM Port: '), sg.InputCombo(findComPort(), size='80', key='comPort'),
           sg.Text(' Device IDs: '), sg.Checkbox('Device 1', default=True, key='dev1'),
           sg.Checkbox('Device 2', default=False, key='dev2')],
          [sg.Text('Parameters in HEX: '), sg.InputText(key='scanParameters')],
          [sg.Text('Scan Interval in (s):  '), sg.InputText(size='6', key='intervalTime', default_text='1')],
          [sg.Text('_' * 100, size=(70, 1))],
          [sg.Text('Schedule Settings:', size=(30, 2), font=("arial", 12), text_color='Black')],
          [sg.Checkbox('Use Scheduler', default=False, key='useScheduler')],
          [sg.Text('Start Time:', size=(9, 1), auto_size_text=False, justification='left'), sg.Input(key='startDate'),
           sg.CalendarButton('Choose', target='startDate')],
          [sg.Text('End Time: ', size=(9, 1), auto_size_text=False, justification='left'),
           sg.Input(key='endDate'),
           sg.CalendarButton('Choose', target='endDate')],
          [sg.Text('_' * 100, size=(70, 1))],
          [sg.Submit(size='80', button_text='Start'), sg.Quit(size='80')]]


window = sg.Window('X34 Monitor', auto_size_text=True, default_element_size=(40, 1)).Layout(layout)

# GUI While loop for PySimple GUI

while True:
    event, values = window.Read()
    if event is None or event == 'Quit':
        break

    # Modbus RTU COM port and Settings - minimalbodbus package

    comPort = values['comPort']
    instrument1 = minimalmodbus.Instrument(comPort, 1)  # port name, slave address (in decimal)
    instrument1.serial.baudrate = 9600

    instrument2 = minimalmodbus.Instrument(comPort, 2)  # port name, slave address (in decimal)
    instrument2.serial.baudrate = 9600

    showSchedWindow = True

    # MAIN LOOP

    # Inputs from User Populate Variables

    projectNameInput = values['projectName']
    projectName = os.path.join("C:", os.sep, "ControllerTests", projectNameInput +
                               "-" + str(datetime.date.today()) + ".csv")
    intervalTime = values['intervalTime']
    sendData = values['scanParameters']
    sendDataList = sendData.split(",")

    # Check and Create Project Path.

    createProjPath()

    # Start Project File
    # Open CSV File and write Headers

    f = open(projectName, 'a')

    f.write('Date,Time,')

    if values['dev1'] == True:

        writeHeaders(sendDataList, devID='-1')
    else:
        pass

    if values['dev2'] == True:

        writeHeaders(sendDataList, devID='-2')
    else:
        pass

    f.write('\n')

    # Main Algo for repeating data entry into CSV file.

    # Prog Max and Counter set up

    # Progress Window Layout

    # create the window
    if values['useScheduler'] is True:
        layoutProgress = [[sg.Text('Test is Running Until:\n\n' + values['endDate'], font=30, key='testText')],
                          [sg.Image(filename='loading.gif', key='loading')],
                          [sg.Cancel(button_text='   Stop Test   ', )]]

        windowProgress = sg.Window('Testing', auto_close=True,
                                   auto_close_duration=int(getMaxScheduleTime())).Layout(layoutProgress)
        loadingGif = windowProgress.FindElement('loading')
        loadingText = windowProgress.FindElement('testText')

    if values['useScheduler'] is False:
        layoutProgress = [[sg.Text('Test is Running Indefinitely', font=30, key='testText')],
                          [sg.Image(filename='loading.gif', key='loading')],
                          [sg.Cancel(button_text='   Stop Test   ', )]]

        windowProgress = sg.Window('Testing').Layout(layoutProgress)
        loadingGif = windowProgress.FindElement('loading')

    # loop that would normally do something useful

    while (values['useScheduler'] is False or
           scheduler(startDate=values['startDate'], endDate=values['endDate']) is True):

        # Try to open project

        try:
            f = open(projectName, 'a')

        except PermissionError:
            print("Could NOT open/write to file. Please check if it is open or being used by another program.")
            sg.Popup("Could NOT open/write to file. Please check if it is open or being used by another program.")
            break

        # Date Now Entry

        parsedData = str(datetime.date.today().strftime("%y-%m-%d")) + "," + str(
            datetime.datetime.now().time().strftime('%H:%M:%S')) + ","

        print(str(parsedData))

        if values['dev1'] == True:
            parsedData = queryController1(sendDataList, parsedData)

        if values['dev2'] == True:
            parsedData = queryController2(sendDataList, parsedData)

        f.write(parsedData)
        f.write('\n')
        f.close()

        loadingGif.UpdateAnimation(source='loading.gif', time_between_frames=0,)

        event, valuesProgress = windowProgress.Read(timeout=1000*float(values['intervalTime']))
        if event is None or event == '   Stop Test   ' or event == 'Quit':

            jobDone()

            windowProgress.Close()
            break


window.Close()
