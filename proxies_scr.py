from email import header
import requests
import requests_html
from lxml.html import fromstring
from bs4 import BeautifulSoup as bs

def get_proxies():
    url = 'https://free-proxy-list.net/'
    response = requests.get(url)
    parser = fromstring(response.text)
    proxies = []
    for i in parser.xpath('//tbody/tr')[:250]:
        if i.xpath('.//td[7][contains(text(),"yes")]'):
            #Grabbing IP and corresponding PORT
            proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
            proxies.append(proxy)
    

    url = 'https://www.proxy-list.download/HTTP'
    r = requests.get(url)
    r.status_code
    soup = bs(r.text, 'html.parser')
    ips_soup = soup.find_all('td')
    ips = []
    ports = []
    for ip in ips_soup:
        a = ip.text.strip()
        if a.count('.') == 3:
            ips.append(a)
        elif a.isdecimal():
            ports.append(a)
        else:
            pass

    more_proxies = []
    for i in  range(0, len(ips)):
        more_proxies.append(ips[i] + ':' + ports[i])


    proxies = proxies + more_proxies

    return proxies





get_proxies()