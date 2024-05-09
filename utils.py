


import os

import requests
import yaml
from bs4 import BeautifulSoup


def load_profiles(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)


def write_df_to_csv(df,filename):
    
    
    if os.path.exists(filename) and os.path.getsize(filename) > 0:
        mode='a'
        header=False
    else:
        mode='w'
        header=True
            
    df.to_csv(filename, mode=mode,header=header, index=False)

    return 'sucess'



def fetch_and_parse(url):
    
    session = requests.Session()
    # Set headers to mimic a browser
    # You can find a user-agent by searching "what is my user agent" in your browser.
    headers = {
    #'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0',
    #new version (from Lampros)
    #'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0',
    #'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'DNT': '1', # Do Not Track request header
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-User': '?1',
    
    # solved wiley 403 by this
    'Sec-Fetch-Site': 'cross-site',

    }


    # Use the session to get the page content
    response = session.get(url, headers=headers)
    #response = session.get(url)

    success_flag =False
    msg=''
    #response = requests.get(url,headers=headers)
    
    response_text = response.text
    
    if 'application/pdf' in response.headers.get('Content-Type', ''):
        msg="The URL points to a PDF file."
        
    elif response.status_code == 403:
        msg="Received a 403 Forbidden response."
        
        
    elif response.status_code == 200:
        success_flag = True
        response_text = BeautifulSoup(response.text, 'html.parser')  
        #print(str(response_text.encode('charmap', 'ignore').decode('charmap')))
        #exit(0)
    else:
        msg = "Failed to fetch the webpage"
    return success_flag, msg, response_text, response.url




def fetch_and_parse_simple(url):
    msg=""
    response = requests.get(url)
        
    if response.status_code == 200:
        return True, msg ,BeautifulSoup(response.text, 'html.parser'), response.url
    else:
        print("Failed to fetch the webpage")
        return None