import json
import time

from selenium import webdriver
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
from selenium.webdriver.support import expected_conditions as EC

import openpyxl

class Excel:

	def __init__(self):
		self.fp = open('found.csv', 'w')

	@staticmethod
	def load_data():
		workbook = openpyxl.load_workbook('Eco hotels in 9 cities.xlsx')
		return list(workbook.active.values)

	def write_(self, data):
		data[0] = str(data[0])
		self.fp.write(f"{','.join(data)}\n")

	def close(self):
		self.fp.close()


def make_driver_settings():
	opts = webdriver.ChromeOptions()
	chrome_prefs = {}
	opts.experimental_options["prefs"] = chrome_prefs
	chrome_prefs["profile.default_content_settings"] = {"images" : 2}
	chrome_prefs["profile.managed_default_content_settings"] = {"images" : 2}
	# opts.add_argument('--headless')
	driver = webdriver.Chrome(options = opts)
	driver.implicitly_wait(20)
	return driver

excel_instance = Excel()
login_url = 'https://www.hotelbeds.com/login'
lookup_dict = json.load(open('settings.json'))

ignored_exceptions = (NoSuchElementException, StaleElementReferenceException, ElementNotVisibleException, TimeoutException, ElementNotInteractableException)
driver = make_driver_settings()

def initial_steps():
	driver.get(login_url)
	driver.find_element_by_id('username').send_keys('WRADEMACHE')
	driver.find_element_by_id('password').send_keys('Enviro123')
	driver.find_element_by_css_selector('button[type=submit]').click()

	driver.get('https://www.hotelbeds.com/accommodation/productlist')


def logout():
	driver.get('https://www.hotelbeds.com/logout')
	driver.close()


def wait_until_(secs=60):
	for i in range(secs):
		h4 = WebDriverWait(driver, 5, ignored_exceptions=ignored_exceptions).until(EC.visibility_of_element_located((By.ID, 'results-global-view')))
		if h4.text == '375 hotels':
			time.sleep(1)
		else:
			return 'EF'  # EF - Element Found


def main_action(first_time, hotel_data):
	# first_time=True; hotel_data=answer
	if first_time:
		hostel_field, search_button = ['s-hotelname', 'mainsearch']
	else:
		hostel_field, search_button = ['ref-hotelname', 'ref-hotelname-filter-button']
		driver.get('https://www.hotelbeds.com/accommodation/productlist/search')
	selection_object = Select(driver.find_element_by_id('s-country'))
	selection_object.select_by_visible_text(hotel_data[3])
	driver.find_element_by_id(hostel_field).send_keys(hotel_data[1])
	selection_object_2 = Select(WebDriverWait(driver, 15, ignored_exceptions=ignored_exceptions).until(EC.presence_of_element_located((By.ID, 's-destination'))))
	for key in lookup_dict.keys():
		if hotel_data[2] in key:
			try:
				selection_object_2.select_by_value(lookup_dict[key])
			except ignored_exceptions:
				pass
	driver.find_element_by_id(search_button).click()
	time.sleep(3)

	hotel_data[0] = str(hotel_data[0])
	try:
		wait_until_()		
		h4 = WebDriverWait(driver, 5, ignored_exceptions=ignored_exceptions).until(EC.visibility_of_element_located((By.ID, 'results-global-view')))		
		# h4 = driver.find_element_by_id('results-global-view')
		if h4.text == '0 hotels':
			print(f"{num} Entry Not Found...")
			fp.write(f"{','.join(hotel_data)}\n")
		else:
			print(num, hotel_data)
			return hotel_data
	except ignored_exceptions:
		print(f"{num} Entry Not Found...")
		fp.write(f"{','.join(hotel_data)}\n")

initial_steps()
fp = open('not_found.csv', 'w')
found = 0
for num, data in enumerate(excel_instance.load_data()):
	if num == 0:
		first_time = True
	else:
		first_time = False
	modified_data = main_action(first_time, list(data))
	if modified_data:
		excel_instance.write_(modified_data)
		found += 1
	time.sleep(.1)

excel_instance.close()
fp.close()
logout()