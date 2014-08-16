#! /usr/bin/python

# Import dependencies
import serial, sys, sendmail, decimal
import socket

HOST = "192.168.1.2"
PORT = 1981

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


def aqp_get_sensor_values(port):
	results = {}
	nw_packet = ""
	port.write(ATMEGA_REQ_SENSOR_VALUES)
	myprint("Sent serial data to AT, waiting for response now...")

	magic = port.read(2)
	nw_packet = nw_packet + magic

	if ord(magic[0]) == 0xA9 and ord(magic[1]) == 0xBD:
		myprint("Magic numbers in response alright\n")

		msg_type = port.read(1)
		nw_packet = nw_packet + msg_type

		if (ord(msg_type) == 0x01): # Check for response

			msg_len = port.read(1)
			nw_packet = nw_packet + msg_len

			myprint ("Payload size is: %d" % ord(msg_len))

			payload = port.read(ord(msg_len))
			nw_packet = nw_packet + payload

			ck1_ck2 = port.read(2)
			nw_packet = nw_packet + ck1_ck2

			myprint ("Ck1 = %X, Ck2 = %X" % (ord(ck1_ck2[0]), ord(ck1_ck2[1])))
		else:
			myprint("Invalid response packet\n")
	else:
		myprint ("Bad Magic, aborting...%X, %X\n" %(ord(magic[0]), ord(magic[1])))

	return nw_packet


def init_serial_port():
	ser = serial.Serial(AT_PORT, AT_BAUD)
	return ser

if __name__ == "__main__":
	ser = init_serial_port()
	nw_packet = aqp_get_sensor_values(ser)
	# Send the network packet to the AQPServer running on the RasPI
	client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client_sock.connect((HOST, PORT))
	#print ord(nw_packet[0]), ord(nw_packet[1]), ord(nw_packet[2]), ord(nw_packet[3])
	client_sock.send(nw_packet)
	resp = client_sock.recv(1024)
	client_sock.close()
	myprint("Response from Server: %s\n" % resp)


