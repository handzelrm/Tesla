from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import re
import csv
from pushbullet import PushBullet
import time


def send_pushbullet(body: str, title: str = 'Python Program Complete') -> None:
    """ Sends a notification to pushbullet

    Args:
        body: text to send in body of message
        title: title of the message

    Returns:
        None
    """
    with open('/media/veracrypt1/pb_api_key.txt', 'r') as f:
        api_key = f.read()
    pb = PushBullet(api_key)
    pb.push_note(title, body)


def check_for_updates():
    fp = webdriver.FirefoxProfile(
        '/home/handzelrm/.mozilla/firefox/i8edqkgd.default-1517000732948')
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(fp, options=options)
    driver.get(
        'https://www.tesla.com/teslaaccount/product-finalize?rn=RN115115977')
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
