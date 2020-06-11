import json, random, os, time

import requests
from selenium import webdriver

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
from selenium.webdriver.support import expected_conditions as EC

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from pydrive.files import FileNotDownloadableError

import pickle
import os.path
from googleapiclient import errors
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# load credentials file and access them
answer = json.load(open('keys.json', 'r'))
USERNAME, PASSWORD = answer['SureKoala']
email, password = answer['DropShipZone']

USER_AGENTS = [
            "Mozilla/5.0 (Linux; <Android Version>; <Build Tag etc.>) AppleWebKit/<WebKit Rev> (KHTML, like Gecko) Chrome/<Chrome Rev> Mobile Safari/<WebKit Rev>",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36",
            "Mozilla/5.0 (Windows NT 5.1; rv:52.0) Gecko/20100101 Firefox/52.0",
           ]

IGNORED_EXCEPTIONS = (NoSuchElementException, StaleElementReferenceException, ElementNotVisibleException, TimeoutException)

class SureKoala:
	@classmethod
	def make_driver_settings(cls, driver_path=r"..\CDN\chromedriver.exe"):
		opts = webdriver.ChromeOptions()
		# chrome_prefs = {}
		# opts.experimental_options["prefs"] = chrome_prefs
		# chrome_prefs["profile.default_content_settings"] = {"images" : 2}
		# chrome_prefs["profile.managed_default_content_settings"] = {"images" : 2}
		# opts.add_argument('--headless')
		driver = webdriver.Chrome(driver_path, options = opts)
		driver.implicitly_wait(30)
		return driver

	@classmethod
	def logout(cls, driver):
		# logout procedure
		button = driver.find_element_by_id('netoToolbar').find_element_by_css_selector('a[class=sign-out-link]')
		driver.get(button.get_attribute('href'))
		time.sleep(5)
		driver.close()

	@classmethod
	def initial_steps(cls, driver, USERNAME=USERNAME, PASSWORD=PASSWORD):
		# login prodedures
		driver.get("https://www.surekoala.com.au/_cpanel")
		driver.find_element_by_id('username').send_keys(USERNAME)
		driver.find_element_by_id('password').send_keys(PASSWORD)
		driver.find_element_by_css_selector('button[type="submit"]').click()
		# if driver.current_url != "https://www.surekoala.com.au/_cpanel":
		driver.get('https://www.surekoala.com.au/_cpanel/dsimport?limitmod=DS_inventory&limittmp=n')

	@classmethod
	def main_actions(cls, driver):
		tags = driver.find_elements_by_tag_name('tbody tr')
		tags[4].find_element_by_id('chkbox2').click()
		#####
		# upload neto csv
		neto_csv = os.path.abspath('neto.csv')
		tags[5].find_element_by_css_selector('[type="file"]').send_keys(neto_csv)
		time.sleep(1)
		driver.execute_script('javascript:doAction("run");')
		driver.switch_to.alert.accept()
		# next_link = driver.find_element_by_css_selector('div[class="netoPage--content--page currentTkn--dsimport"] a').get_attribute('href')
		link = WebDriverWait(driver, 480, ignored_exceptions=IGNORED_EXCEPTIONS).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[class="netoPage--content--page currentTkn--dsimport"] a')))
		next_link = link.get_attribute('href')
		driver.get(next_link)
		driver.find_element_by_css_selector('input[type="checkbox"]').click()
		driver.execute_script("javascript:doActionSingle('run','0');")

	@classmethod
	def nucleus(cls):
		driver = cls.make_driver_settings()
		cls.initial_steps(driver)
		cls.main_actions(driver)
		cls.logout(driver)


class DropShipZone:
	@classmethod
	def initial_requests(cls, session, payload, POST_LOGIN_URL):
		# cookies = dict(cookies_are='working')
		post = session.post(POST_LOGIN_URL, headers={'User-agent': random.choice(USER_AGENTS)}, cookies=dict(cookies_are='working'), data=payload, timeout=(30, 60), verify=False)
		post = session.post('https://www.dropshipzone.com.au/rsds/download/skus/', headers={'User-agent': random.choice(USER_AGENTS)}, cookies=session.cookies, data=payload, timeout=(30, 60), verify=False)
		return session
	
	@classmethod
	def download_file(cls, session, REQUEST_URL):
		# download csv file
		r = session.get(REQUEST_URL, headers={'User-agent': random.choice(USER_AGENTS)}, stream=True, cookies=dict(session.cookies), timeout=(30, 60), verify=requests.certs.where())
		filename = r.headers['Content-Disposition'].split('=')[-1].strip()
		with open(filename, 'wb') as file:
			print(f"[DropShipZone Bot] Downloading {filename} .. This file is quite large and might take a little while to finish downloading.")
			for chunk in r.iter_content(10000, decode_unicode=True):
				file.write(chunk)
		print(f"[DropShipZone Bot] Done Downloading {filename} ...")

	@classmethod
	def nucleus(cls):
		POST_LOGIN_URL = 'https://www.dropshipzone.com.au/customer/account/loginPost/referer/aHR0cHM6Ly93d3cuZHJvcHNoaXB6b25lLmNvbS5hdS8_X19fU0lEPVU,/'
		REQUEST_URL = 'https://www.dropshipzone.com.au/rsdropship/download/downloadSkuList/'
		payload = {
			'login[username]': email,
			'login[password]': password,
		}

		print("[DropShipZone Bot] Attempting to login to Account")
		session = requests.Session()
		print("[DropShipZone Bot] Login Successful")
		session = cls.initial_requests(session, payload, POST_LOGIN_URL)
		print("[DropShipZone Bot] File Download Initiated")
		cls.download_file(session, REQUEST_URL)


class GWorker:
	@classmethod
	def download_(cls, drive):
		pm = 'application/vnd.google-apps.spreadsheet'
		try:
			file_list =  drive.ListFile({'q': "'1z6YjW4IYMakiNtnd9JB8qK-GPMS_yth1' in parents and trashed=false"}).GetList()
			for file in file_list:
				if file['title'] == "FileForNeto":
					file1 = drive.CreateFile({'id': file['id']})
					file1.GetContentFile('neto.csv', mimetype=pm)
					break
		except FileNotDownloadableError:
			print("[Google Bot] To Commence Download of neto.csv")
			file1['exportLinks'][pm] = file1.get('exportLinks').get('text/csv')
			file1.GetContentFile('neto.csv', mimetype=pm)
			print("[Google Bot] Neto File Successfully Downloaded...")

	@classmethod
	def upload_(cls, drive):
		file_list =  drive.ListFile({'q': "'1L7gWhf0Jhim4XvP1BMpIPblJ5zCl-5fJ' in parents and trashed=false"}).GetList()
		for file in file_list:
			if file['title'] == 'sku_list Upload Here':
				file2 = drive.CreateFile({'id': file['id']})
				print("[Google Bot] To Commence Upload of sku_list.csv")
				file2.SetContentFile('sku_list.csv')
				file2.Upload()
				print("[Google Bot] SKU File Successfully uploaded...")

	@classmethod
	def nucleus(cls):
		gauth = GoogleAuth()
		# Create local webserver and auto handles authentication.
		gauth.LocalWebserverAuth()
		drive = GoogleDrive(gauth)

		print("[Google Bot] Drive Successfully Engaged")
		cls.upload_(drive)
		cls.download_(drive)

class FilterSheet:
	@classmethod
	def get_scripts_service(cls):
		SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']
		creds = None
		if os.path.exists('token.pickle'):
			with open('token.pickle', 'rb') as token:
				creds = pickle.load(token)
		if not creds or not creds.valid:
			if creds and creds.expired and creds.refresh_token:
				creds.refresh(Request())
			else:
				flow = InstalledAppFlow.from_client_secrets_file(
					'client_secrets.json', SCOPES) 
				creds = flow.run_local_server(port=0)
			with open('token.pickle', 'wb') as token:
				pickle.dump(creds, token)

		return build('script', 'v1', credentials=creds)

	@classmethod
	def action(cls):
		service = cls.get_scripts_service()
		API_ID = "MgWJvW4FegI-NDpFLP44x-vLSJHYMIpDM" 
		request = {"function": "filterSheet"} 
		try:
			response = service.scripts().run(body=request, scriptId=API_ID).execute()
			print(response)
		except errors.HttpError as error:
			# The API encountered a problem.
			print(error.content)


if __name__ == "__main__":
	# create a dropshipzone instance
	# prepare the sku_list.csv and the neto.csv files
	dropshipzone_instance = DropShipZone()
	dropshipzone_instance.nucleus()

	# upload the sku_list file and download the neto file
	googledriver_instance = GWorker()
	googledriver_instance.nucleus()
	
	# # filter object instance
	filter_object = FilterSheet()
	filter_object.action()

	cms_worker_instance = SureKoala()
	cms_worker_instance.nucleus()

	# print("Woohooo .. JOB DONE!!!")



