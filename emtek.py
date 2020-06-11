import json, os, re, time

from fake_useragent import UserAgent
from bs4 import BeautifulSoup as bs
from requests import Session


URL = "https://emtek.com/"
session = Session()
ua = UserAgent()

def send_request(link):
	for _ in range(5):
		try:
			response = session.get(link, timeout=(45, 60))
			session.headers.update({'User-Agent': ua.random})
			if response.ok:
				return bs(response.text, features="html.parser")
		except Exception:
			pass
		print("* Retrying Requests")
		
def gather_variations(soup):
	finish_dictionary = {}; lever_list = list()
	option_elements = soup.select(".detailsright .detail_options_row")
	for element in option_elements:
		if element.text.strip() == 'AVAILABLE FINISH OPTIONS':
			elems = element.select('.pthumbnail')[:10]
			for elem in elems:
				image_title = elem.get('data-original-title') 
				image_urls = URL + elem.find('img').get('src')
				finish_dictionary[image_title] = image_urls
		elif element.text == 'AVAILABLE LEVER OPTIONS':
			elems = soup.select('.pthumbnail')[:10]
			for elem in elems:
				image_title = elem.get('data-original-title')
				lever_list.append(image_title)
	return finish_dictionary, lever_list
	
def fetch_data(soup):
	title = soup.select_one(".detailtitle h1").text.replace("\n", " ").strip()

	image_urls = [ URL + elem.get('src') for elem in soup.select("#myCarousel .item img") ]
	variations = gather_variations(soup)
	
	description = soup.select_one('div#description').text.strip()
	specs = soup.select_one('div#specs').text.strip()
	codes = soup.select_one('div#codes').text.strip()

	sku = re.search('(E)?(MP)?\d{3,}', codes)
	if sku:
		sku = sku.group()
	else:
		sku = ""	

	if sku:
		return {'title': title, "image_urls": image_urls, "description": description, "specs": specs, "sku": sku, 'variation': variations}
	else:
		return {'title': title, "image_urls": image_urls, "description": description, "specs": specs, 'variation': variations}

def get_view_all_address(link, num):
	print("\t\t**" + str(num) + '/' + f"{len(all_product_link)} " + link + "**")
	soup = send_request(link)
	try:
		view_all_address = f"{URL}{soup.select('.pagenums a')[-1].get('href')}"
	except IndexError:
		view_all_address =  f"{URL}{soup.select('#catNav')[0].select('li a')[-1].get('href')}"
	return view_all_address

def get_required_information(view_all_address):
	soup = send_request(view_all_address)
	for product in soup.select('.catImage'):
		product = product.find('a').get('href').strip('./')
		try:
			print(URL + product)
			soup = send_request(URL + product)
			data = fetch_data(soup)
			print(data)
		except Exception:
			continue
		yield data

with open('download.txt', 'w') as fp:

	soup = send_request("https://emtek.com/products/all")
	all_product_link = [ f"{URL}{address.get('href')}" for address in soup.select('#services .first')[0].select('a') ]
	for num, link in enumerate(all_product_link[11:12], 1):
		view_all_address = get_view_all_address(link, num)
		values = get_required_information(view_all_address)
		for value in values:
			flat = json.dumps(value)
			print(flat, file=fp, end="\n")

print("Yiips .. Done")
input("Press Enter to quit.")