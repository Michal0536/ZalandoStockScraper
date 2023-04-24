from random_user_agent.params import SoftwareName, HardwareType
from random_user_agent.user_agent import UserAgent
import requests
import json
from bs4 import BeautifulSoup
import discord
import random

software_names = [SoftwareName.CHROME.value]
hardware_type = [HardwareType.MOBILE__PHONE]
user_agent_rotator = UserAgent(software_names=software_names, hardware_type=hardware_type)

headers = {
        'User-Agent': user_agent_rotator.get_random_user_agent(),
        'accept': 'text/html,application/xhtml+xml,application/json,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'pl,pl;q=0.9,en;q=0.8'}   



def get_proxy():
    x = open("proxy.txt" , 'r')        
    proxy = {
        'https' : "",
        'http':""
    }
    proxy_lista =[]
    for line in x:
        proxy_lista.append(line[:-1])

    element = random.choice(proxy_lista)
    ip = element.split(":")[0]
    port = element.split(":")[1]
    login = element.split(":")[2]
    passwd = element.split(":")[3]

    https_proxy_format = "https://" +login+":"+passwd+"@"+ip+":"+port
    http_proxy_format = "http://" +login+":"+passwd+"@"+ip+":"+port
    proxy['https'] = https_proxy_format 
    proxy['http'] = http_proxy_format

    return proxy


def scraper(url):
    total_stock = 0
    product_page = requests.get(url=url, headers = headers, timeout=10, proxies=get_proxy() )

    if product_page.status_code == 200:
        soup = BeautifulSoup(product_page.content, 'html.parser')
        all_data = str(soup.select_one('script[type="application/ld+json"]')).replace('&quot;','"').replace('<script type="application/ld+json">' , "").replace('</script>',"")
        jsonData = json.loads(all_data)
        all_offers = jsonData['offers']
        zdjecie = jsonData['image'][0]
        tytul = jsonData["manufacturer"] + ' ' + jsonData["name"]

        stockk = []
        size_pids = []
        size_pids2 = []

        for items in all_offers:
            size_pids.append(items['sku']+"\n")
            size_pids2.append(items['sku'])

        flare_pids = ""
        for pid in size_pids2:
            flare_pids += pid + ","
        flare_pids = flare_pids[:-1]

        #STOCK
        all_data_main = str(soup.find_all("script" , {"class":"re-1-14"})[0]).replace(r'<script class="re-1-14" data-re-asset="" type="application/json">',"").replace(r'</script>',"")
        jsonDatax = json.loads(all_data_main)
        v = jsonDatax['graphqlCache']
        #NEW KEY CHECKER
        # for keyx,valuex in v.items():
        #     if "context" in str(keyx) or "context" in str(valuex):
        #         print(keyx)
        #     else:
        #         pass

        size_key = '4319f815175526e9048e98dbb2403c392a462b85e0a65d65ef212a9224be5836'
        keys =[]
        for key,value in v.items():
            if size_key in key:
                zguba = key
                keys.append(zguba)
        key_with_stock = keys[0]
        knock_knock = v[key_with_stock]['data']['context']

        global_pid = str(knock_knock['entity_id']).split("::")[1]
        stock = knock_knock['simples']    

        for items in stock:
            eu_size = items['size']
            ilosc = items['offer']["stock"]['quantity']

            if ilosc == "OUT_OF_STOCK":
                ilosc = "OOS"
                eu_size = f":red_circle: {eu_size}"
            if ilosc == "ONE":
                eu_size = f":orange_circle: {eu_size}"
                total_stock =total_stock+1
            if ilosc == "TWO":
                eu_size = f":orange_circle: {eu_size}"
                total_stock =total_stock+ 2
            if ilosc == "MANY":
                eu_size = f":green_circle: {eu_size}"
                total_stock =total_stock+ 3        

            stockk.append(f"{eu_size} [" + ilosc + "]"  + "\n")
        return zalando_webhook(global_pid, stockk, size_pids, flare_pids,url, zdjecie, tytul, total_stock)
    
    if product_page.status_code == 404:
        return product_error()

    else:
        print("Site Connection Error")



def zalando_webhook(global_sku, stockk, size_pids, flare_pids,url,zdjecie, tytul, total_stock):
        embed = discord.Embed(title=f'{tytul}', color=0x50d68d, url=url)
        embed.set_thumbnail(url=f'{zdjecie}')
        embed.add_field(name='Global PID', value=f'{global_sku}', inline="false") 
        embed.add_field(name='Total Stock', value=f'At least {total_stock}', inline="false")
        embed.add_field(name='SIZES' , value=f'{" ".join(stockk)}', inline="true")
        embed.add_field(name='PIDS' , value=f'{" ".join(size_pids)}', inline="true")
        embed.add_field(name='Flare | SoleT format', value=f'```{flare_pids}```',inline='false')
        embed.set_footer(text='by Michał#0536')
        

        return embed

def product_error():
    embed=discord.Embed(title="Error", description="Brak danych o produkcie", color = 15158332)
    embed.set_footer(text='by Michał#0536')

    print("Product error")
    return embed