import re
import requests
from bs4 import BeautifulSoup
import time

def num_phones(soup, url):
    number = str(url.split('_')[-1].split('.')[0])
    expir_hash = soup.select('script[class^="js-user-secure-"]')[0]

    expires_value = expir_hash.get('data-expires')
    hash_value = expir_hash.get('data-hash')

    url = 'https://auto.ria.com/users/phones/'+number
    params = {
        'hash': hash_value,
        'expires': expires_value
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        phone_dict = response.json()
        phones = [el['phoneFormatted'] for el in phone_dict['phones']]
        return phones
    else:
        print('Error during the request:', response.status_code)
        return []

def extract_car_data(car_url):
    response = requests.get(car_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'lxml')

        car_data = {}
        car_title_element = soup.find('h3', class_='auto-content_title')
        car_data['car_title'] = car_title_element.text.split() if car_title_element else ["N/A"]

        price_element = soup.find('span', class_='price_value')
        car_data['price'] = price_element.text.split() if price_element else ["N/A"]

        car_number_element = soup.find('span', class_='state-num ua')
        car_data['car_number'] = (car_number_element.text.strip()
                                  .replace("Ми розпізнали держномер авто на фото та перевірили його за реєстрами МВС",
                                           "")) if car_number_element else "N/A"

        username_element = soup.find('div', class_='seller_info_name')
        car_data['username'] = username_element.text.strip() if username_element else "N/A"

        vin_code_element = soup.find('span', class_='label-vin')
        car_data['vin_code'] = vin_code_element.text if vin_code_element else "N/A"

        image_element = soup.find('img', class_='outline m-auto')
        car_data['image_link'] = image_element.get('src') if image_element else "N/A"

        car_data['phones'] = num_phones(soup, car_url)

        return car_data
    else:
        print(f'Error during the request for {car_url}: {response.status_code}')
        return None


def scrape_page(url, max_pages=10):
    print('Start_______' * 30)
    count = 0
    cars = []

    for page in range(1, max_pages + 1):
        print(f"Processing page {page}")
        response = requests.get(url)
        if response.status_code != 200:
            print(f'Error during the request for {url}: {response.status_code}')
            break

        soup = BeautifulSoup(response.text, 'lxml')
        car_cards = soup.find_all('section', class_='ticket-item')

        for car_card in car_cards:
            url_car = car_card.find('a', class_='m-link-ticket')
            if url_car:
                car_url = url_car.get('href')
                print(f"Processing car: {car_url}")

                car_data = extract_car_data(car_url)
                if car_data:
                    print(car_data)
                    cars.append(car_data)
                    count += 1

        next_page = soup.find("a", class_="page-link js-next")
        if next_page:
            url = next_page['href']
        else:
            break

    print(f"Processed {count} cards")
    return cars

if __name__ == "__main__":
    start_time = time.time()
    url_to_scrape = "https://auto.ria.com/uk/car/used/"
    result_cars = scrape_page(url_to_scrape, max_pages=10)
    end_time = time.time()
    execution_time = end_time - start_time
    print("Execution time:", execution_time, "seconds")
