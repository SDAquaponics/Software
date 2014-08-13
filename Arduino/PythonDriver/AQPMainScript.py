#! /usr/bin/python

# Import dependencies
import serial, sys, sendmail, decimal
DEBUG = False;

# Serial port settings
AT_PORT = "/dev/ttyATH0"
AT_BAUD = 115200


# Serial packet structure
MAGIC_1 = 0xA9
MAGIC_2 = 0xBD
MSG_TYPE_REQUEST = 0x00
MSFG_TYPE_RESPONSE = 0x01
MSG_LEN_READ_SENSOR_VALUES = 0x01
OPAQUE_DATA_REQ = 0x00
EOD = 0xCB
CK_1 = 0xFD
CK_2 = 0xFF

ATMEGA_REQ_SENSOR_VALUES = [MAGIC_1, \
                            MAGIC_2, \
                            MSG_TYPE_REQUEST, \
                            MSG_LEN_READ_SENSOR_VALUES, \
                            OPAQUE_DATA_REQ,\
                            EOD,\
                            CK_1,\
                            CK_2]


# Sensor type definitions
SENSOR_TYPE_DISTANCE = 0x00
SENSOR_TYPE_TEMP = 0x01
SENSOR_TYPE_HUMIDITY = 0x02

CRITICAL_DISTANCE = 1.5
MSG_COUNTER = 0


def myprint(arg):
    if DEBUG:
        print(arg)
    else:
        None


def parse_payload(payload):
    sensor_dict = {}
    if (ord(payload[0]) == 0x01):
        num_sensors = ord(payload[1])
        myprint ("Number of sensors: %d" % num_sensors)
        start_idx = 2
        for idx in range(0, num_sensors):
            sensor_data = payload[start_idx: start_idx + 4]
            sensor_type = ord(sensor_data[0])
            sensor_status = ord(sensor_data[1])
            sensor_val = sensor_data[2:]
            value = "%s.%s" % (ord(sensor_val[0]), ord(sensor_val[1]))
            if (sensor_type == SENSOR_TYPE_DISTANCE):
                sensor_dict['Distance'] = value
            elif (sensor_type == SENSOR_TYPE_TEMP):
                sensor_dict['Temperature'] = value
            elif (sensor_type == SENSOR_TYPE_HUMIDITY):
                sensor_dict['Humidity'] = value
            else:
                myprint("Wrong sensor type detected")
            start_idx = start_idx + 4  # On to the next sensor value

    else:
        myprint("Invalid payload type")

    return sensor_dict



def aqp_get_sensor_values(port):
    results = {}
    port.write(ATMEGA_REQ_SENSOR_VALUES)
    myprint("Sent serial data to AT, waiting for response now...")
    magic = port.read(2)
    if ord(magic[0]) == 0xA9 and ord(magic[1]) == 0xBD:
        myprint("Magic numbers in response alright\n")
        msg_type = ord(port.read(1))
        if (msg_type == 0x01): # Check for response
            msg_len = ord(port.read(1))
            myprint ("Payload size is: %d" % msg_len)
            payload = port.read(msg_len)
            results = parse_payload(payload)
            ck1 = port.read(1)
            ck2 = port.read(1)
            myprint ("Ck1 = %X, Ck2 = %X" % (ord(ck1), ord(ck2)))
        else:
            myprint("Invalid response packet\n")
    else:
        myprint ("Bad Magic, aborting...%X, %X\n" %(ord(magic[0]), ord(magic[1])))

    return results


def init_serial_port():
    ser = serial.Serial(AT_PORT, AT_BAUD)
    return ser

if __name__ == "__main__":
    msg = '''Aquaponics pod reporting, water level beyond critical value!!:
=========================================================
'''
    ser = init_serial_port()
    all_results = aqp_get_sensor_values(ser)
    dec_dist = decimal.Decimal(all_results['Distance'])
    if dec_dist > CRITICAL_DISTANCE:
        for sensor, reading in all_results.items():
            msg = msg + ("%s sensor reading: %s\n" % (sensor, reading))
        msg = msg + "=======================================================\n"

        myprint(msg)
        fromaddr = 'henrysaquaponics@gmail.com'
        toaddr = 'seemanta@gmail.com'
        toaddr2 = 'hfinkelstein@gmail.com'
        subject="Aquaponics pod water level beyond critical value!!"
        mailer = sendmail.mailerClass('henrysaquaponics', 'aquaponicsinc', fromaddr)
        #mailer.send(toaddr, subject, msg)
        #mailer.send(toaddr2, subject, msg)
        myprint("Email sent!")
    else:
        myprint("Nothing to report, level = %s" % (dec_dist))

#     if aqp_check_sensor_state():
#         aqp_notify_raspi()
#     else:
#         sensor_values = aqp_get_sensor_values()
#
#     ota_packet = aqp_pack_sensor_values(sensor_values)
#     aqp_send_sensor_packet(ota_packet)
#
#
#
# def check_wifi_connectivity():
#     return True
#
#
# def check_atmega_connectivity():
#     return True




# if __name__ == "__main__":
#     if check_wifi_connectivity():
#         print ("Wifi is good\n")
#     else:
#         print("Wifi is bad!\n")
#
#     if check_atmega_connectivity():
#         print ("Atmega processor is good\n")
#     else:
#         print ("Atmega is bad!\n")


"""
msg='''
    Aquaponics pod reporting in with the following stats:

    ========================
    Pod water level = 3 ft
    Pod temp = 75 deg F
    ========================
    '''
"""