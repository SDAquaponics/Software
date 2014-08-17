#!/usr/bin/python

import gspread, time


class gspreadUploader():
	def __init__(self, user, pwd):
		self.user = user
		self.pwd = pwd



	def login(self):
		self.gc = gspread.login(user, pwd)


	def openSpreadSheet(self, sheetname):
		pass


	def upload(self, temp, distance):
		sp = gc.open("AQPonicsDataLog")
		pass






if __name__ == '__main__':
	gc = gspread.login('henrysaquaponics', 'aquaponicsinc')
	sp = gc.open("AQPonicsDataLog")
	wks = sp.worksheet("Sheet1")


	all = wks.get_all_values()
	end_row = len(all) + 1
	beg = 'A%d' % end_row
	end = 'C%d' % end_row
	cell_list = wks.range('%s:%s' % (beg, end))

	cell_list[0].value = time.strftime("%I:%M:%S%p")
	cell_list[1].value = 25
	cell_list[2].value = 38

	wks.update_cells(cell_list)











