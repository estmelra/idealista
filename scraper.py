from re import search
import  requests
from bs4 import BeautifulSoup as bs
import random
import time
import pandas as pd
import proxies_scr


# To avoid having our ip blocked by  idealista there are two things we need to do:
# First  is to send headers  with our request. headers tell idealista some information about where we are coming from.
# Second we need to rotate IP adress so that it is not allways the same. We will use a csv of free proxies I found on the internet.

search_limit = 1500


# We need to send headers so that idealista recognises us as a person and not a bot
headers = {
    'accept': '*/*',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'es,es-ES;q=0.9,en;q=0.8,fr;q=0.7',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'referer': 'https://www.idealista.com/en/areas/venta-viviendas/?shape=%28%28ez_%7EEn%7Bse%40_bCceIniKcdFpvAfiEa%7EI%7E_J%29%29',
    #'sec-ch-ua': " Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98",
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': 'macO',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.109 Safari/537.36',
    'x-newrelic-id': 'VQIGUlZbGwIBXFhWBQEDVw==',
    'x-requested-with': 'XMLHttpRequest'
}

# Looking  for proxies
print('Selecting working proxies.')
working_proxies = []
tested_proxies = []
round = 1
n_prox = 7

while len(working_proxies) < n_prox:
    print(f'Round {round} of proxy scrapping.')
    print(f'{len(tested_proxies)} proxies tested')
    print(f'{len(working_proxies)} proxies found')
    proxies = proxies_scr.get_proxies()
    for prox in proxies:
        if prox not in working_proxies and prox not in tested_proxies:
            if len(working_proxies) >= n_prox:
                break
            else:

                try:
                    url = 'https://www.idealista.com/'
                    proxy = 'http://' + prox
                    r = requests.get(url, headers=headers, proxies={'http': proxy, 'https': proxy},  timeout=10)
                    if r.status_code == 200:
                        working_proxies.append(prox)
                        break
                        
                    else:
                        tested_proxies.append(prox)
                except:
                    tested_proxies.append(prox)

    if len(working_proxies) < n_prox:
        time.sleep(20)

    round = round + 1
    

print(f'{len(working_proxies)} proxies found plus local one.')
working_proxies.append('') # to add local IP
print('working proxies are:')
print(working_proxies)


print('Finding houses ids')
x = 1 # for pagination
ids = []
while True:
    if len(ids) >= search_limit:
        print(f'{len(ids)} ids scraped')
        print('Limit reached')
        break

    url = f'https://www.idealista.com/en/areas/venta-viviendas/pagina-{x}?shape=%28%28ez_%7EEn%7Bse%40_bCceIniKcdFpvAfiEa%7EI%7E_J%29%29'
    random_index_prox = random.randint(0, len(working_proxies)-1)
    prox = working_proxies[random_index_prox]
    if prox != '':
        proxy = 'http://' + prox
    else:
        proxy = ''

    try:
        r = requests.get(url, headers=headers, proxies={'http': proxy, 'https': proxy},  timeout=10)
        print('IP: ' + proxy + f' -- status code: {r.status_code}')
        soup = bs(r.text, 'html.parser')
        selected_page = soup.find('main', {'class':'listing-items'}).find('div', {'class':'pagination'}).find('li', {'class':'selected'}).text

        if x == int(selected_page):
            articles = soup.find('main', {'class':'listing-items'}).find_all('article')
        else:
            break
                
        homes_ids = [article.get('data-adid') for article in articles]
                
        for id in homes_ids:
            if id:
                ids.append(id)
                
        x = x + 1
        print('IP seems to work')
        print(f'{len(ids)} ids scraped')

    except:
        #print('IP: ' + proxy +  ' -- failed, trying a new one.')
        #time.sleep(random.randint(1, 5)*random.random()) # to avoid getting blocked

        pass

if len(ids) > search_limit:
    ids = ids[0:search_limit]

# Getting all info from individual houses
print('Finding houses info')
raw_data = pd.DataFrame()

for id in ids:
    house_url = f'https://www.idealista.com/en/inmueble/{id}/'
    keep_searching_proxi = True

    while keep_searching_proxi:
        random_index_prox = random.randint(0, len(working_proxies)-1)
        prox = working_proxies[random_index_prox]
        if prox != '':
            proxy = 'http://' + prox
        else:
            proxy = ''

        try:
            r = requests.get(house_url, headers=headers, proxies={'http': proxy, 'https': proxy},  timeout=10)
            
            if r.status_code == 404:
                print('ID: ' + id +  ' -- Remmoved from idealista.')
                keep_searching_proxi = False
            
            elif r.status_code == 200:
                tries = 0
                while tries < 10:
                    try:
                        print('IP:' +  proxy + ' -- seems to work')
                        soup = bs(r.text, 'html.parser')
                        tittle = soup.find('span', {'class':'main-info__title-main'}).text
                        city = soup.find('span', {'class':'main-info__title-minor'}).text
                        price_act = soup.find('span', {'class':'info-data-price'}).find('span', {'class':'txt-bold'}).text

                        try:
                            price_first = soup.find('span', {'class':'pricedown'}).find('span', {'class':'pricedown_price'}).text
                        except:
                            price_first = price_act

                        details_1 = soup.find('div', {'class':'details-property-feature-one'}).find_all('div', {'class':'details-property_features'})
                        details_1_desc = []
                        for ul in details_1:
                            lis = ul.findAll('li')
                            for li in lis:
                                details_1_desc.append(li.text.strip())

                        details_2 = soup.find('div', {'class':'details-property-feature-two'}).find_all('div', {'class':'details-property_features'})
                        details_2_desc = []
                        for ul in details_2:
                            lis = ul.findAll('li')
                            for li in lis:
                                details_2_desc.append(li.text.strip())

                        details_3 = soup.find('div', {'class':'details-property-feature-three'}).find_all('div', {'class':'details-property_features'})
                        details_3_desc = []
                        for ul in details_3:
                            lis = ul.findAll('li')
                            for li in lis:
                                details_3_desc.append(li.text.strip())

                        advertiser = soup.find('div', {'class':'professional-name'}).find('div', {'class':'name'}).text.strip()

                        line = {
                            'house_id': id,
                            'tittle': tittle,
                            'city': city,
                            'price_act': price_act,
                            'price_first': price_first,
                            'details_1_desc': details_1_desc,
                            'details_2_desc': details_2_desc,
                            'details_3_desc': details_3_desc,
                            'advertiser' : advertiser
                        }

                        raw_data = raw_data.append(line, ignore_index=True)
                        #time.sleep(random.randint(1, 3)*random.random()) # to avoid getting blocked
                        to_go = len(ids) - ids.index(id)
                        print(f'remaining houses to scrap: {to_go}')
                        keep_searching_proxi = False
                        tries = tries + 10
                    except Exception as e: 
                        print('Estatus code 200 but not working')
                        print(e)
                        tries = tries + 1
                        keep_searching_proxi = False
            
            else:
                print('IP: ' + proxy +  f' -- failed due a status code {r.status_code}, trying a new one.')
                pass


        except:
            print('IP: ' + proxy +  ' -- failed, trying a new one. General error')
            #time.sleep(random.randint(1, 5)*random.random()) 
            pass



       
# Saving data
print('Saving data')
raw_data.to_csv('data/raw_data.csv')

print('End')

