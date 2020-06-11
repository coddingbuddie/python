import datetime, os, time

import requests
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.support.ui import Select

def link_validity(link):
	if link:
		return True

def return_pdf_link(link):
	response = requests.get(link)
	soup = BeautifulSoup(response.text, features="html.parser")
	pdf_links = soup.select('#attach_docs a')
	scripts = soup.select('script')[-1]
	main_pdf_url = scripts.text.strip().split('function')[2].split('\t')[2].strip().split('=')[-1].strip("';")
	links = [ f"""https://ireps.gov.in{pdf_link.get('onclick').split("'")[1]}""" for pdf_link in pdf_links ]
	links.append(f"https://ireps.gov.in{main_pdf_url}")
	return links

def download_pdf(link, path):
	print('#', link, '-', path)
	filename = os.path.join(path, link.split('/')[-1]) 
	print(f"Downloading {filename}")
	with open(filename, 'wb') as fp:
		res = requests.get(link, stream=True)
		for chunk in res.iter_content(10000):
			if chunk:
				fp.write(chunk)
	print(f'Done Downloading'); print('#' * 90)

def fetch_window_links():
	t = driver.find_element_by_xpath('/html/body/table/tbody/tr[4]/td[2]/table/tbody/tr/td/div/table/tbody/tr[1]/td/table/tbody/tr[2]/td/form/table[3]/tbody/tr[6]')
	rows = t.find_elements_by_tag_name('tr')[1:]
	for row in rows:
		data = row.find_elements_by_tag_name('td')
		tender_number = data[1].text.strip()
		end_date = data[5].text.split()[0].strip()
		href = data[7].find_element_by_css_selector('a').get_attribute('onclick')
		# pointers to the pdf page
		link = href.split(',')[0].split('(')[-1].strip("'")
		yield [tender_number, end_date, link]

def create_upperlevel_folder(date, tender_type):
	# create upper level folder
	upperlevel_folder_name = f"Upload Date {date.replace('/', '-')}"
	os.makedirs(upperlevel_folder_name, exist_ok=True)
	mid_level_directory = os.path.join(upperlevel_folder_name, f"Keyword = {search_criteria}")
	os.makedirs(mid_level_directory, exist_ok=True)
	sub_directory = os.path.join(mid_level_directory, tender_type)
	os.makedirs(sub_directory, exist_ok=True)
	return sub_directory

def sub_level_folder(upperlevel_folder_name, refined_list):
	# create a sub-folders
	tender_number = refined_list[0].replace('-', '')
	due_date = refined_list[1].replace('/', '.')
	folder_path = os.path.join(upperlevel_folder_name, f"{tender_number}_{due_date}")
	os.makedirs(folder_path, exist_ok=True)
	return folder_path
	
def return_date_list():
	'''
	this function requests for two dates and gives all dates that are in between the two input dates.
	'''
	def date_range(start, end):
	    r = (end + datetime.timedelta(days=1) - start).days
	    return [start + datetime.timedelta(days=i) for i in range(r)]
	 
	start_date = input("Enter Starting Date in Format (YYYY/MM/DD): ")
	end_date = input("Enter Ending Date in Format (YYYY/MM/DD): ")
	start_date = [int(num) for num in start_date.split('/')]
	end_date = [int(num) for num in end_date.split('/')]

	start = datetime.date(*start_date)
	end = datetime.date(*end_date)
	date_list = [ date.strftime('%d/%m/%Y') for date in date_range(start, end)]
	return date_list

def initial_steps(search_criteria, tender_type, date):
	driver.get('https://ireps.gov.in/epsn/anonymSearch.do')
	driver.find_element_by_id('custumSearchId').click()
	# select the option Item Description
	Select(driver.find_element_by_css_selector('select[name=searchOption]')).select_by_value('4')
	field = driver.find_element_by_id('searchtext')
	field.send_keys(search_criteria)
	Select(driver.find_element_by_id('railwayZone')).select_by_value('-1')
	Select(driver.find_element_by_css_selector('select[name=selectDate]')).select_by_value('TENDER_PUBLISHING_DATE')
	Select(driver.find_element_by_id('tenderType')).select_by_visible_text(tender_type)
	# set the date
	driver.execute_script(f'document.getElementById("ddmmyyDateformat1").value = "{date}"')
	driver.execute_script(f'document.getElementById("ddmmyyDateformat2").value = "{date}"')

	search_button = driver.find_element_by_css_selector('tr[id=searchButtonBlock] input[type=submit]')
	driver.execute_script("arguments[0].click();", search_button)


# get the date and date range
date_list = return_date_list()
driver = webdriver.Chrome('CDN/Chromedriver.exe')
# driver = webdriver.Chrome('Chromedriver.exe')
driver.implicitly_wait(20)

search_criterion = ['Bearing', 'Bush', 'NTN']
tender_type_options = ['Limited', 'Open']

# tender type
# date = date_list[0]
# search_criteria = search_criterion[0]
# tender_type = tender_type_options[0]

for date in date_list:
	for search_criteria in search_criterion:
		for tender_type in tender_type_options:
			initial_steps(search_criteria, tender_type, date)
			refined_lists = list(fetch_window_links())
			upperlevel_folder_name = create_upperlevel_folder(date, tender_type)
			for refined_list in refined_lists:
				path = sub_level_folder(upperlevel_folder_name, refined_list)
				links = return_pdf_link(f'https://ireps.gov.in{refined_list[-1]}')
				for link in links:
					download_pdf(link, path)


time.sleep(5)
driver.quit()
