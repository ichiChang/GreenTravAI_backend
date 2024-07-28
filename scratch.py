from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json


def scratchEcoSpot():
    chrome_driver_path = r"C:\Users\USER\Desktop\Side project\beauty-master\chromedriver-win64\chromedriver-win64\chromedriver.exe"
    options = Options()
    options.chrome_executable_path = chrome_driver_path

    driver = webdriver.Chrome(options=options)
    driver.get("https://neecs.moenv.gov.tw/Home/PlaceQry")

    try:
        select_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "frontPlaceQryVM_City"))
        )
        select = Select(select_element)
        select.select_by_value("臺北市")

        search_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn.btn-primary"))
        )
        search_button.click()

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "tbody"))
        )

        elements = driver.find_elements(By.TAG_NAME, "tbody")
        result = []
        for element in elements:
            print(element.text)
            result.append(element.text)

        with open("./data/ecoSpots.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=4)

    finally:

        driver.quit()


def scratchSpot():
    pass


def scratchRestaurant():
    pass
