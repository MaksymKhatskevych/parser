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

def scrape_page(url, max_pages=10):
    print('Start_______' * 30)
    count = 0
    cars = []

    for page in range(1, max_pages+1):
        print(f"Processing page {page}")
        response = requests.get(url)
        html_doc = response.text
        soup = BeautifulSoup(html_doc, 'lxml')

        car_cards = soup.find_all('section', class_='ticket-item')

        for car_card in car_cards:
            car_data = {}
            url_car = car_card.find('a', class_='m-link-ticket')
            if url_car:
                car_url = url_car.get('href')
                print(f"Processing car: {car_url}")

                car_response = requests.get(car_url)
                car_html_doc = car_response.text
                car_soup = BeautifulSoup(car_html_doc, 'lxml')

                car_title = car_soup.find('h3', class_='auto-content_title')
                if car_title:
                    car_data['car_title'] = car_title.text.split()

                price = car_soup.find('span', class_='price_value')
                if price:
                    car_data['price'] = price.text.split()

                car_number_element = car_soup.find('span', class_='state-num ua')
                if car_number_element:
                    car_number_text = car_number_element.text.strip().replace("Ми розпізнали держномер авто на фото та перевірили його за реєстрами МВС", "")
                    car_data['car_number'] = car_number_text.strip()

                seller_info_area = car_soup.find('div', class_='seller_info_area')
                if seller_info_area:
                    username = seller_info_area.find('div', class_='seller_info_name')
                    if username:
                        car_data['username'] = username.text.strip()
                    else:
                        car_data['username'] = "N/A"
                else:
                    car_data['username'] = "N/A"

                vin_code = car_soup.find('span', class_='label-vin')
                if vin_code:
                    car_data['vin_code'] = vin_code.text

                image = car_soup.find('img', class_='outline m-auto')
                if image:
                    image_link = image.get('src')
                    if image_link:
                        car_data['image_link'] = image_link

                phones = num_phones(car_soup, car_url)
                car_data['phones'] = phones

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
