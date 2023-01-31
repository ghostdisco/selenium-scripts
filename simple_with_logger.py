import logging, sys, time
from dataclasses import dataclass
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.remote.remote_connection import LOGGER as gecko_logger
from webdriver_manager.chrome import ChromeDriverManager

query = input('Query: ')

# config
@dataclass
class Config:

    #logging
    log_level: int = 1 # 0 = error only, 1 = info, 2 = debug

    #browser
    interactive: bool = False
    browser_width: int = 1024
    browser_height: int = 800
    element_timeout: int = 10

config = Config()


# logging
am_debugging = bool(sys.gettrace())
log_level = { 0: logging.ERROR, 1: logging.INFO, 2: logging.DEBUG }[config.log_level]
logging.Formatter.converter = time.localtime if am_debugging else time.gmtime
logging.basicConfig(filename='simple-selenium.log', level=log_level, format='%(asctime)s %(name)s %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

gecko_logger.setLevel(log_level)
logging.getLogger("requests").setLevel(log_level)
logging.getLogger("urllib3").setLevel(log_level)


# browser options
browser_options = webdriver.ChromeOptions()
if not config.interactive:
    browser_options.headless = True
    browser_options.add_argument('--disable-notifications')
    browser_options.add_argument('disable-infobars')
    assert browser_options.headless


# initialize driver
driver = webdriver.Chrome(
    service=ChromeService(ChromeDriverManager().install()),
    options=browser_options
)


# browser settings
driver.set_window_size(width=config.browser_width, height=config.browser_height)
driver.implicitly_wait(config.element_timeout)


logger.info(f"Browser Initialized - {'Interactive' if config.interactive else 'Headless'} - {config.browser_width}x{config.browser_height}")
logger.info(f'ID: {driver.session_id}')


# load website
driver.get('https://google.com')

# enter query
try:
    search_box = driver.find_element(By.NAME, 'q')
    search_box.send_keys(query)


# NoSuchElementException catches errors when an element is not found
except NoSuchElementException as e:
    logger.error(f'element not found: {e}')

# Exception catches any other errors that may occur
except Exception as e:
    logger.error(f'an error occurred while getting the query box: {e}')


# submit query
try:
    submit_button = driver.find_element(By.NAME, 'btnK')
    submit_button.click()


except NoSuchElementException as e:
    logger.error(f'element not found: {e}')
except Exception as e:
    logger.error(f'an error occurred while getting the submit button: {e}')


# get first result
try:
    # this div contains all the results
    results_container = driver.find_element(By.ID, 'rso')

    # text (non-video/image) results have are assigned the 'g' classname
    results = results_container.find_elements(By.CLASS_NAME, 'g')

    # the results are stored in a list, grab the first element in the list
    first_result = results[0]

    # google results classnames and ids are randon strings, using xpath to specify the child item we want

    # grab the title container element
    title = first_result.find_element(By.XPATH, './div/div/div/a')

    # get the text from the title container
    title_text = title.find_element(By.XPATH, './h3').text

    # the url is stored as an 'href' attribute of the title element
    link = title.get_attribute('href')

    # once again, the description is hard to parse using classname/id so we're using xpath
    desc = first_result.find_element(By.XPATH, './div/div[2]/div').text
    
    # print result
    print(f'\n\n--=={{{{  Top Search Result  }}}}==--')
    print(f'Query: {query}')
    print(f'Title: {title_text}')
    print(f'Link: {link}')
    print(f'Description: {desc}\n')


except NoSuchElementException as e:
    logger.error(f'element not found: {e}')
except Exception as e:
    logger.error(f'an error occurred while retrieving search results: {e}')

time.sleep(5)
logger.info('DONE!')
