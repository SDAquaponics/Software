#!/usr/bin/python
# Sensor type definitions
SENSOR_TYPE_DISTANCE = 0x00
SENSOR_TYPE_TEMP = 0x01
SENSOR_TYPE_HUMIDITY = 0x02

import decimal
from twisted.internet import protocol, reactor

class Echo(protocol.Protocol):
	def parse_payload(self, payload):
		sensor_dict = {}
		if (ord(payload[0]) == 0x01):
			num_sensors = ord(payload[1])
			print ("Number of sensors: %d" % num_sensors)
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
					print("Wrong sensor type detected")
				start_idx = start_idx + 4  # On to the next sensor value

		else:
			print("Invalid payload type")

		return sensor_dict


	def parseData(self, data):
		magic1, magic2 = ord(data[0]), ord(data[1])
		msg_type = ord(data[2])
		msg_len = ord(data[3])
		payload = data[4 : 4 + msg_len]
		print("magic1 = %d, magic2 = %d, type = %d, len = %d\n" % (magic1, magic2, msg_type, msg_len))
		#for byte in payload:
		#	print ("Byte = 0x%X" % ord(byte))

		all_results = self.parse_payload(payload)
		dist = (all_results['Distance'])
		temp = (all_results['Temperature'])
		print("Sensed Distance = %s, Temp = %s" % (dist, temp))
		return "OK!"

	def dataReceived(self, data):
		response = self.parseData(data)
		self.transport.write(response)

class EchoFactory(protocol.Factory):
	def buildProtocol(self, addr):
		return Echo()



class AQPServer():
	def serve_requests(self):
		reactor.listenTCP(1981, EchoFactory())
		reactor.run()



if __name__ == '__main__':
	aqpserver = AQPServer()
	aqpserver.serve_requests()
