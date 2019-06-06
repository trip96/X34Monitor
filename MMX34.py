import minimalmodbus
import time
import datetime
import subprocess
import os

# Logo w00t w00t

logoAscii = '''
...................................................................................................................... 
....ODDDDD................................................................~DDDD....................NDDD...............
. DN:MNNN:NN..............................................................DDDD.....................NDDD...............
.DN...^.^..DD:...DDD?NDDDN MDDD8.. DDD~ DDD.DDDDD .IDDD . DDD8. NDDDDN7 .DDDDDD..=DDDDD...7DDN,DD.DDDDDDN.DDD...DDDD..
DM.,..# #. .DN ..DDDNDDDDDDDDDDDD. DDD~ DDDNDDDDDN.IDDD . DDD8.NDD=.NDND DNDDD8.DDDDNNDDD.7DDNDDD.DDDDD8D DDD8..DDD ..
NNNNDDNNDDDDND:..DDDD..DDDD..$DDN..DDD~ DDDN..DNDD IDDD . DDD8 DDDDDM,. ..DDDD.DDDD...DDN+7DDDN....DDDD.. :NDN.DDDD... 
NND.N.DD.=,DMD...DDDD. DDDN..~DDD..DDD~.DDDD..DDDD.IDDD ..DDD8. 7DDDDDDD  DDDD.DDDD...DDDD7DDD.....DDDD....DDD8DDD....
7D...DDDODN.DN...DDDD. DDDN..~DDD. DDD~ DDDD..DDDD..DDDN?DDDD8:DDD..?DDD  DDDD.IDDD...DDN.7DDN.....DDDDDO.  NDDDN8....
.DDN..ND~MD8N....DDDN. DDDN..~DDD. DDD~ DDDD..DDDD..DDDDDNDDD8.NDDNDNDD7 .DDDD. ODDDDNDD~.7DDN.. ..+DDDDN.  DDDDD.....  
...DNDDDDDDI..............................................................................................~$NDDN,.....
..........................................................................................................+NDDDN......
......................................................................................................................
         
'''

# Logo Print anitmation

for char in logoAscii:
    time.sleep(0.001)
    print(char, end='', flush=True)

# Disclaimer

print('Welcome to Minus Forty Technologies Controller Monitoring Program Developed by '
      'Travis Scola and Jordan MacKinnon. ')

print('\r\n\nTo exit press CRTL+C\n\n')

# Communications Setup for Controller

comPort = input("Enter COM port for attached device: ")
instrument = minimalmodbus.Instrument(comPort, 1)  # port name, slave address (in decimal)
instrument.serial.baudrate = 9600

# MAIN LOOP

while True:

    # Inputs from User

    projectNameInput = input('Enter new project Name: ')

    projectName = os.path.join("C:", os.sep, "ControllerTests", projectNameInput +
                               "-" + str(datetime.date.today()) + ".csv")
    if os.path.exists(r'c:\ControllerTests') == False:
        os.mkdir(r'c:\ControllerTests')
    else:
        pass
    intervalTime = input('Enter time interval in seconds: ')

    sendData = input('Enter parameter values to monitor (HEX) separated by commas: ')

    sendDataList = sendData.split(",")

    # Auto open folder location.

    subprocess.Popen(r'explorer /select,"C:\ControllerTests\"' + projectNameInput +
                               "-" + str(datetime.date.today()) + ".csv")

    # Start Project File

    try:

        f = open(projectName, 'a')
        f.write('Date,Time,')
        for i in range(len(sendDataList)):
            try:
                f.write(sendDataList[i] + ",")
            except ValueError:
                pass
        f.write('\n')

    except PermissionError:
        print("Could NOT open/write to file. Please check if it is open or being used by another program.")
        exit()

    # Main Algo for repeating data entry into CSV file.

    while True:

        parsedData = str(datetime.date.today().strftime("%y-%m-%d")) + "," + str(
            datetime.datetime.now().time()) + ","

        print("Datetime is: " + parsedData)

        try:

            f = open(projectName, 'a')

        except PermissionError:
            print("Could NOT open/write to file. Please check if it is open or being used by another program.")
            exit()

        for i in range(len(sendDataList)):
            try:
                payLoad = instrument.read_register(int(sendDataList[i], 16), 1)
                print(payLoad)
                parsedData = str(parsedData) + str(payLoad) + ","
            except ValueError:
                print("Hex Parameter: " + sendDataList[i] + " NOT recognized by Controller")
                parsedData = str(parsedData) + "N/A" + ","
                pass

        f.write(parsedData)
        f.write('\n')
        f.close()
        time.sleep(float(intervalTime))

