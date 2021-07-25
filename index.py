# Imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from requests_html import HTML
import os


def login(driver, username, password):
    print("Logging in")
    username_input = driver.find_element_by_xpath(
        "//input[@name='user_login']")
    username_input.send_keys(username)

    password_input = driver.find_element_by_xpath(
        "//input[@name='user_password']")
    password_input.send_keys(password)

    driver.find_element_by_xpath("//button[@name='submit']").click()


def fetch_items(driver):
    items = []
    print("Starting fetch")
    while True:
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "item-list__link")))
            html = HTML(html=driver.page_source)
            items.extend(html.find(".item-list__tile"))

            WebDriverWait(driver, 10).until(EC.presence_of_element_located(
                (By.CLASS_NAME, "pagination__page-jump")))
            current_page = driver.find_element_by_xpath(
                "//input[@class='pagination__page-jump']").get_attribute("value")
            print("On page", current_page)
            print("Total items scraped", len(items))
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(
                (By.XPATH, "//a[@class='pagination__next']")))
            driver.find_element_by_xpath(
                "//a[@class='pagination__next']").click()
    #         WebDriverWait(driver, 10).until(EC.url_changes(driver.current_url))

        except Exception as e:
            # print(e)
            driver.close()
            break
    print("Done")
    return items


def parse_items(items, base_url):
    final_data = []
    for item in items:
        item_link = base_url + \
            item.find(".item-list__link", first=True).attrs["href"]
        new_price, old_price = item.find(".item-list__price-number")[0].text.strip(
        ), item.find(".item-list__price-number")[1].text.strip()
        availability = item.find(
            ".availability-status-indicator__text", first=True).text.strip()
        obj = {
            "Item Link": item_link,
            "New Price": new_price,
            "Old Price": old_price,
            "Availability": availability
        }
        # print(obj)
        final_data.append(obj)

    return final_data


def save_as_csv(final_data, store):
    df = pd.DataFrame.from_dict(final_data)
    df.to_csv(f"{store}.csv", header=True, index=False)
    print("saved successfully")


def main():
    username = os.environ.get("username")
    password = os.environ.get("password")
    print(username, password)
    base_url = "https://brickseek.com"
    stores = ["2787", "1270"]
    for store in stores:
        print("Store", store)
        url = f"{base_url}/login?redirect_to={base_url}/walmart-clearance-stores?store={store}&zip=15129"
        options = Options()
        options.add_argument("start-maximized")
        options.add_argument("headless")
        # options.add_argument("disable-infobars")
        driver = webdriver.Chrome(
            options=options)
        driver.get(url)
        login(driver, username, password)
        items = fetch_items(driver)
        # print(len(items))
        final_data = parse_items(items, base_url)
        save_as_csv(final_data, store)


if __name__ == "__main__":
    main()
