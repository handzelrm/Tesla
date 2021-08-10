from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import re
import csv
from pushbullet import PushBullet
import time
import pickle


def send_pushbullet(body: str, title: str = 'Python Program Complete') -> None:
    """ Sends a notification to pushbullet. Can just hardcode in API key on local computer.

    Args:
        body: text to send in body of message
        title: title of the message

    Returns:
        None
    """
    # using pickled data
    with open('user_data.pkl', 'rb') as f:
        user_data = pickle.load(f)

    # loading api_key from file
    with open(user_data['pushbullet_path'], 'r') as f:
        api_key = f.read()
    pb = PushBullet(api_key)
    pb.push_note(title, body)


def check_for_updates():
    """ Checks for Tesla account estimated deliveries and for VIN in source code.
    Used pickled data to hide account information. These values can be changed
    and hard coded to on local computers.

    Args:
        None

    Returns:
        None
    """
    # Using data pickled from another file. Do not need to use if just
    # inserting firefox profile path and tesla account URL
    with open('user_data.pkl', 'rb') as f:
        user_data = pickle.load(f)
    # fp = webdriver.FirefoxProfile('***INSERT PATH TO FIREFOX PROFILE***')
    fp = webdriver.FirefoxProfile(
        user_data['firefox_profile'])  # using pickled data

    options = Options()
    options.headless = True

    driver = webdriver.Firefox(fp, options=options)
    # driver.get('https://www.tesla.com/teslaaccount/product-finalize?rn=***INSERT RN***')
    driver.get(user_data['tesla_account_url'])  # using pickled data

    edd = driver.find_element_by_class_name('tds-text--h6').text
    source = driver.page_source
    re_vin = re.compile('\"isNotMatchedToRa00Vin\":([a-zA-Z]*)')
    try:
        vin_not_matched = re_vin.search(source).group(1)
    except AttributeError:
        send_pushbullet(body='Need to log back in.', title='Login')

    if vin_not_matched == 'true':
        vin = False
    else:
        send_pushbullet(body="Tesla Matched a VIN!", title="VIN!")

    with open('./EDD.csv', 'r') as f:
        new_edd = False
        try:
            last_edd = f.readlines()[-1].strip()
            if edd != last_edd:
                new_edd = True
        except IndexError:
            new_edd = True
            last_edd = None
    if new_edd:
        send_pushbullet(
            body=f"{edd}", title="New EDD!")
        with open('./EDD.csv', 'a') as f:
            f.write(edd)
            f.write('\n')
    driver.quit()


while True:
    check_for_updates()
    time.sleep(300)
