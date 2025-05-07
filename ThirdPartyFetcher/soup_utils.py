import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time

def url_to_soup(url: str) -> BeautifulSoup:
    print(f"Fetching {url}")
    options = uc.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--headless=new')

    driver = uc.Chrome(options=options, headless=True)
    driver.get(url)
    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    driver.quit()
    return soup