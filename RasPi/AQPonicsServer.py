#!/usr/bin/python
# Sensor type definitions
SENSOR_TYPE_DISTANCE = 0x00
SENSOR_TYPE_TEMP = 0x01
SENSOR_TYPE_HUMIDITY = 0x02

from decimal import Decimal
import time
import gspread
import random
import plotly.plotly as py # plotly library
import json
import datetime
import xively

XIVELY_API_KEY = "soua9TLw1W7TpvAMwNrIl5AxpEfeCO8T83BpMz3dfJe7FYa4"
XIVELY_FEED_ID = 584440607

from twisted.internet import protocol, reactor

haveEndRow = False
endRow = 0

class Echo(protocol.Protocol):
	def parse_payload(self, payload):
		sensor_dict = {}
		if (ord(payload[0]) == 0x01):
			num_sensors = ord(payload[1])
			#print ("Number of sensors: %d" % num_sensors)
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

	def update_xively(self, ts, level, temp):
		api = xively.XivelyAPIClient(XIVELY_API_KEY)
		feed = api.feeds.get(XIVELY_FEED_ID)
		now=datetime.datetime.utcnow()
		feed.datastreams = [
			xively.Datastream(id='water_level', current_value=level, at=now),
			xively.Datastream(id='temperature', current_value=temp, at=now)
		]
		feed.update()

	def update_webpage(self, ts, level, temp):
		file = open("/home/pi/Software/RasPi/webdata/index.html", 'w')
		filedata = '''
		<html>
		Timestamp = %s<BR>
		Level = %s<BR>
		Temperature = %s<BR>
		</html>
		''' % (ts, level, temp)
		file.write(filedata)
		file.close()


	def update_plotly(self, level, temp):
		with open('./config.json') as config_file:
			plotly_user_config = json.load(config_file)
			py.sign_in(plotly_user_config["plotly_username"], plotly_user_config["plotly_api_key"])
		
		url = py.plot([
    			{
		        'x': [], 'y': [], 'type': 'bar',
		        'stream': {
				'token': plotly_user_config['plotly_streaming_tokens'][0],
				'maxpoints': 200
        		}
 		}], filename='Raspberry Pi Streaming water level and temperature')
		#print "View your streaming graph here: ", url
		
		#Update the stream now
		stream = py.Stream(plotly_user_config['plotly_streaming_tokens'][0])
		stream.open()
		print("level = %s" % level)
		stream.write({'x': datetime.datetime.now(), 'y': level})

	def update_google_spreadsheet(self, ts, level, temp):
		gc = gspread.login('henrysaquaponics', 'aquaponicsinc')
		sp = gc.open("AQPonicsDataLog")
		wks = sp.worksheet("Data")
		global haveEndRow, endRow


		if haveEndRow == False:
			#print ("Getting row end\n")
			haveEndRow = True
			all = wks.get_all_values()
			endRow = len(all) + 1
		#else:
		#	print("Already have row end...\n")

		beg = 'A%d' % endRow
		end = 'E%d' % endRow
		cell_list = wks.range('%s:%s' % (beg, end))
		endRow = endRow + 1  #For next time


		# Add jitter so that the graph comes out nicely
		jitter1 = random.randrange(-400, 400)
		jitter2 = random.randrange(-400, 400)


		# Update the running list of readings
		cell_list[0].value = ts
		cell_list[1].value = level
		cell_list[2].value = temp
		cell_list[3].value = "%s" % (Decimal(level) + (jitter1/100))
		cell_list[4].value = "%s" % (Decimal(temp) + (jitter2/100))

		#print ("Updating spreadsheet...")
		#print ("data=%s, Jitter1 = %f, Jitter2 = %f" % (cell_list[0].value , jitter1, jitter2))
		wks.update_cells(cell_list)

		#Update the current value
		curr_cells = wks.range('A3:C3')
		curr_cells[0].value = ts
		curr_cells[1].value = level
		curr_cells[2].value = temp
		wks.update_cells(curr_cells)


	def parseData(self, data):
		magic1, magic2 = ord(data[0]), ord(data[1])
		msg_type = ord(data[2])
		msg_len = ord(data[3])
		payload = data[4 : 4 + msg_len]
		#print("magic1 = %d, magic2 = %d, type = %d, len = %d\n" % (magic1, magic2, msg_type, msg_len))
		#for byte in payload:
		#	print ("Byte = 0x%X" % ord(byte))

		all_results = self.parse_payload(payload)
		dist = (all_results['Distance'])
		temp = (all_results['Temperature'])
		#print("Sensed Distance = %s, Temp = %s" % (dist, temp))

		#Get timestamp
		ts = time.strftime("%m-%d-%Y %H:%M:%S")

		# Now update Google Spreadsheet
		self.update_google_spreadsheet(ts, dist, temp)

		#Update the webpage
		self.update_webpage(ts, level, temp)

		#Update Xively
		self.update_xively(ts, level, temp)

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
