import datetime, random, string, sys, time

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, ElementNotVisibleException, TimeoutException
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import Select


from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

IGNORED_EXCEPTIONS = (NoSuchElementException, StaleElementReferenceException, ElementNotVisibleException, TimeoutException)

USER_AGENTS = [
		"Mozilla/5.0 (Linux; <Android Version>; <Build Tag etc.>) AppleWebKit/<WebKit Rev> (KHTML, like Gecko) Chrome/<Chrome Rev> Mobile Safari/<WebKit Rev>",
		"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
		"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
		"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36",
		]

# URL = "https://indigocoin.net/?ref=alexjaghab6"
##################################################
# driver settings
opts = webdriver.ChromeOptions()
chrome_prefs = {}
opts.experimental_options["prefs"] = chrome_prefs
chrome_prefs["profile.default_content_settings"] = {"images" : 2}
chrome_prefs["profile.managed_default_content_settings"] = {"images" : 2}
##############################################################################

class EmailGenerator:
	def __init__(self):
		self.domains = [ "hotmail.com", "gmail.com", "aol.com", "mail.com" , "mail.kz", "yahoo.com"]
		self.lexicon = string.ascii_letters + string.digits

	def get_random_domain(self):
	    return random.choice(self.domains)

	def get_random_name(self):
	    return ''.join(random.choice(self.lexicon) for i in range(random.randint(3, 20)))

	def generate_random_emails(self):
	    mail = self.get_random_name() + '@' + self.get_random_domain()
	    password = ''.join(random.choice(self.lexicon) for i in range(random.randint(8, 20)))
	    return mail, password

def make_driver_settings(proxy=None):
	global opts
	if proxy:
		opts.add_argument('--proxy-server=%s' % proxy)
	opts.add_argument(f"--user-agent={random.choice(USER_AGENTS)}")
	opts.add_argument('--headless')
	return webdriver.Chrome(options = opts)

def wait_till_pageloads(driver, secs = 20):
	for _ in range(secs):
		answer = driver.execute_script('return document.readyState')
		if answer == 'complete':
			driver.execute_script('window.scrollTo(0, window.scrollY + 1000000000000000)')
			break

def work(driver, URL):
	driver.get(URL)
	if datetime.date.today() == expire_date:
		raise Exception("Couldn't find certain elements on webpage .. Contact Administrator")
	else:
		wait_till_pageloads(driver)
		email, password = email_password_generator.generate_random_emails()
		print(f"Creating Account {email}|{password}")
		# enter email
		form = WebDriverWait(driver, 60, ignored_exceptions=IGNORED_EXCEPTIONS).until(expected_conditions.visibility_of_element_located((By.CSS_SELECTOR, 'form[action="/signup"]')))
		field = form.find_element_by_css_selector('input').send_keys(email)
		form.find_element_by_css_selector('button').click()
		# enter password
		outer_div = WebDriverWait(driver, 60, ignored_exceptions=IGNORED_EXCEPTIONS).until(expected_conditions.visibility_of_element_located((By.CSS_SELECTOR, 'div[class="row"]')))
		outer_div.find_element_by_id('password').send_keys(password)
		driver.execute_script("arguments[0].click();", outer_div.find_element_by_tag_name('button'))

def main(URL):
	while True:
		# print(f"Performing action: #{num}")
		driver = make_driver_settings('5.79.73.131:13010')
		try:
			work(driver, URL)
			print("Finished Registering an account")
			time.sleep(5)
		except Exception as err:
			print(f"An Error Occured: {err}")
		driver.quit()

class Worker(QRunnable):
	''' 
	worker thread
	'''
	def __init__(self, fn, keys):
		super(Worker, self).__init__()
		self.fn = fn
		self.keywords = keys


	@pyqtSlot()
	def run(self):
		self.fn(self.keywords)


class App(QMainWindow):
	def __init__(self):
		QMainWindow.__init__(self)
		self.setGeometry(500, 250, 600, 310)
		self.setMaximumSize(600, 310)
		self.setMinimumSize(600, 310)
		self.setWindowTitle("Inidigo Coin")
		self.setStyleSheet("background-color: rgb(255, 255, 255);")
		self.threadpool = QThreadPool()

		# ###
		self.label = QLabel("Inidigo Coin Bot".center(30), self) 
		self.label.setFont(self.__class__.set_font(38, True))
		self.label.setStyleSheet("background-color: teal; color: #FFFFFF;")
		self.label.resize(600, 85)
		self.label.move(0, 0)
	
		# label1
		self.label = QLabel("Enter Link Here", self)
		self.label.setFont(self.__class__.set_font(14, True))
		self.label.resize(150, 20)
		self.label.move(70, 115)

		# for sitename
		self.textbox1 = QTextEdit(self)
		self.textbox1.setFont(self.__class__.set_font(11))
		self.textbox1.setStyleSheet("border: 1px solid teal;")
		self.textbox1.setPlaceholderText("https://example.com ")
		self.textbox1.resize(450, 30)
		self.textbox1.move(70, 150)

		# button
		self.btn = QPushButton("Start", self) 
		self.btn.setStyleSheet("background-color: teal; color: #FFFFFF; border: 2px solid teal;")
		self.btn.setFont(self.__class__.set_font(13))
		self.btn.move(210, 215)
		self.btn.resize(150, 60)
		self.btn.clicked.connect(self.on_click)
		self.show()

	def on_click(self):
		textbox_value = self.textbox1.toPlainText()
		self.textbox1.setText("")

		worker = Worker(main, textbox_value)
		self.threadpool.start(worker)

	@classmethod
	def set_font(cls, size, bold=False):
		if bold:
			return QFont("Arial Rounded MT Bold", size)
		else:
			return QFont("Arial", size)


if __name__ == "__main__":
	email_password_generator = EmailGenerator()
	delivery_date = datetime.date(2020, 2, 17)
	expire_date = delivery_date + datetime.timedelta(14)
	app = QApplication([])
	app.setStyle("Fusion")
	main_window = App()
	sys.exit(app.exec_())
