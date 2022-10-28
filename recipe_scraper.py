from bs4 import BeautifulSoup
from typing import Optional
import json
import requests
import re
import time

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager


def get_recipe_json(url: str) -> Optional[dict]:
    parser = "html.parser"
    req = requests.get(url)
    soup = BeautifulSoup(req.text, parser)
    script = soup.find("script", {"type": "application/ld+json"})
    if script and script.contents:
        try:
            parsed = json.loads(script.contents[0])
            # print(json.dumps(parsed, indent=4))  # pretty print json file
            return parsed
        except json.JSONDecodeError:
            return None
    return None


def setup_webdriver() -> webdriver.Firefox:
    ff_options = Options()
    ff_options.add_argument('--headless')
    service = Service(GeckoDriverManager().install())
    driver = webdriver.Firefox(
        options=ff_options,
        service=service,
    )
    return driver


def scrape_recipes_google(ingredients: list, cuisine: str) -> dict:

    driver = setup_webdriver()

    ingredients_str = '+'.join(ingredients)
    if cuisine == 'Any':
        driver.get(f'https://www.google.com/search?q={ingredients_str}+vegetarian+recipe&hl=en-US')
    else:
        driver.get(f'https://www.google.com/search?q={ingredients_str}+{cuisine}+vegetarian+recipe&hl=en-US')

    # buffer for everything to load
    time.sleep(5)

    results_dict = {
        'title': [],
        'link': [],
        'image': [],
        'source': [],
        'total_time': [],
        'ingredients': [],
        'ratings': [],
        'reviews': []
    }

    link = None

    while True:
        show_more_button = driver.find_element(By.XPATH, '//div[@aria-label="Show more" and @role="button"]')
        print(show_more_button)  # just for debug
        # TODO: fix, show more is always there, need another condition
        time.sleep(1)
        try:
            WebDriverWait(driver, 5).until(EC.element_to_be_clickable(show_more_button)).click()
        except TimeoutException:
            break

        # if show_more_button element becomes False, break the loop
        if not show_more_button:
            break

    for index, result in enumerate(driver.find_elements(By.CSS_SELECTOR, '.YwonT')):
        try:
            title = result.find_element(By.CSS_SELECTOR, '.hfac6d').text
        except NoSuchElementException:
            title = None

        results_dict['title'].append(title)

        link = result.find_element(By.CSS_SELECTOR, '.YwonT .v1uiFd a').get_attribute('href')
        results_dict['link'].append(link)

        image = result.find_element(By.CSS_SELECTOR, '.YwonT .v1uiFd img').get_attribute('src')
        results_dict['image'].append(image)

        source = result.find_element(By.CSS_SELECTOR, '.KuNgxf').text
        results_dict['source'].append(source)

        try:
            total_time = result.find_element(By.CSS_SELECTOR, '.wHYlTd').text
        except NoSuchElementException:
            total_time = None

        results_dict['total_time'].append(total_time)

        try:
            # stays the list if need to extract certain ingredient
            ingredients = result.find_element(By.CSS_SELECTOR, '.LDr9cf').text.split(',')
        except NoSuchElementException:
            ingredients = None

        results_dict['ingredients'].append(ingredients)

        try:
            ratings = result.find_element(By.CSS_SELECTOR, '.YDIN4c').text
        except NoSuchElementException:
            ratings = None

        results_dict['ratings'].append(ratings)

        try:
            reviews = result.find_element(By.CSS_SELECTOR, '.HypWnf').text.replace('(', '').replace(')', '')
        except NoSuchElementException:
            reviews = None

        results_dict['reviews'].append(reviews)

        # print(f'{index + 1}\n{title}\n{link}\n{source}\n{total_time}\n{ingredients}\n{rating}\n{reviews}\n')

    driver.quit()

    return results_dict


def scrape_recipes_bing(ingredients: list, cuisine: str, limit: int) -> dict:

    driver = setup_webdriver()

    ingredients_str = '+'.join(ingredients)
    if cuisine == 'Any':
        driver.get(f'https://www.bing.com/search?q={ingredients_str}+vegetarian+recipe&hl=en-US')
    else:
        driver.get(f'https://www.bing.com/search?q={ingredients_str}+{cuisine}+vegetarian+recipe&hl=en-US')

    time.sleep(5)

    results_dict = {
        'title': [],
        'link': [],
        'image': [],
        'source': [],
        'total_time': [],
        'calories': [],
        'servings': [],
        'ratings': [],
        'reviews': []
    }

    # On FF, Bing throws up banner to add Bing extension to browser, we need to find it and click 'Maybe Later'
    try:
        maybe_later_text = driver.find_element(By.XPATH, '//span[@id="bnp_hfly_cta2"]')
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable(maybe_later_text)).click()
    except NoSuchElementException:
        print("Banner not found, skipping...")

    see_more_button = driver.find_element(By.XPATH, '//a[@title="See more" and @role="button"]')
    print(see_more_button)  # just for debug
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable(see_more_button)).click()

    reached_end = False
    max_retries = 10
    old_count = len(driver.find_elements(By.XPATH, '//div[@class="wfrGridCell" and @role="button"]'))

    def scroll_and_find():
        driver.execute_script('window.scrollBy(0,250)')  # scroll by 20 on each iteration
        time.sleep(0.5)
        count = len(driver.find_elements(By.XPATH, '//div[@class="wfrGridCell" and @role="button"]'))

        return count

    while not reached_end:
        #driver.find_element(By.CSS_SELECTOR, "body").send_keys(Keys.END)
        new_count = scroll_and_find()
        print(new_count)
        if new_count > limit:
            break

        if new_count == old_count:
            # Make sure there's really no new elements
            for i in range(max_retries):
                new_count = scroll_and_find()
                if new_count == old_count and i == max_retries-1:
                    reached_end = True
                    break
        else:
            old_count = new_count

    for index, result in enumerate(driver.find_elements(By.CSS_SELECTOR, '.wfrGridCell')):
        try:
            # TODO: Figure out why some titles are cut off
            title = result.find_element(By.CSS_SELECTOR, '.rwtitle').text
            # title = result.find_element(By.XPATH, "//div[@class='rwtitle']//strong").text
        except NoSuchElementException:
            title = None
        results_dict['title'].append(title)

        try:
            link = result.find_element(By.CSS_SELECTOR,
                                       '.wfrGridCell .b_responsiveWaterfallItemCard'
                                       ).get_attribute('data-prmurl')
        except NoSuchElementException:
            link = None
        results_dict['link'].append(link)

        try:
            image = result.find_element(By.CSS_SELECTOR, '.rwimage img').get_attribute('src')
        except NoSuchElementException:
            image = None
        results_dict['image'].append(image)

        try:
            tags = result.find_element(By.CSS_SELECTOR, '.rwtags').text.split('\n')
        except NoSuchElementException:
            tags = None

        tags_len = len(tags)
        source = tags[0] if tags_len > 0 else None
        reviews = tags[1] if tags_len > 1 and 'reviews' in tags[1] else None

        results_dict['source'].append(source)
        results_dict['reviews'].append(reviews)

        total_time = calories = servings = None
        if tags_len > 1:
            for elem in tags[-1].split('·'):
                if 'min' in elem:
                    total_time = elem.strip()
                if 'cals' in elem:
                    calories = elem.strip()
                if 'servs' in elem:
                    servings = elem.strip()

        results_dict['total_time'].append(total_time)
        results_dict['calories'].append(calories)
        results_dict['servings'].append(servings)

        try:
            # Displays as "Star Rating: 4.5 out of 5"
            ratings = result.find_element(By.CSS_SELECTOR, '.rwtags .csrc').get_attribute('aria-label').split()[2]
        except NoSuchElementException:
            ratings = None

        results_dict['ratings'].append(ratings)

        if index+1 == limit:
            break

       # print(f'{index + 1}\n{title}\n{link}\n{source}\n{reviews}\n{total_time}\n{calories}\n{servings}\n{rating}\n')

    # driver.quit()

    return results_dict


if __name__ == '__main__':
    pass
    # test_app()

