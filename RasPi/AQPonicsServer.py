#!/usr/bin/python
# Sensor type definitions
SENSOR_TYPE_DISTANCE = 0x00
SENSOR_TYPE_TEMP = 0x01
SENSOR_TYPE_HUMIDITY = 0x02

from decimal import Decimal
import time
import gspread
import random

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


	def update_google_spreadsheet(self, level, temp):
		gc = gspread.login('henrysaquaponics', 'aquaponicsinc')
		sp = gc.open("AQPonicsDataLog")
		wks = sp.worksheet("Sheet1")


		all = wks.get_all_values()
		end_row = len(all) + 1
		beg = 'A%d' % end_row
		end = 'E%d' % end_row
		cell_list = wks.range('%s:%s' % (beg, end))

		# Add jitter so that the graph comes out nicely
		jitter1 = random.randrange(-400, 400)
		jitter2 = random.randrange(-400, 400)

		cell_list[0].value = time.strftime("%I:%M:%S%p")
		cell_list[1].value = level
		cell_list[2].value = temp
		cell_list[3].value = "%s" % (Decimal(level) + (jitter1/100))
		cell_list[4].value = "%s" % (Decimal(temp) + (jitter2/100))

		#print ("Updating spreadsheet...")
		print ("Jitter1 = %f, Jitter2 = %f" % (jitter1, jitter2))
		wks.update_cells(cell_list)

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

		# Now update Google Spreadsheet
		self.update_google_spreadsheet(dist, temp)
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
