import io
import random
import sys
import time

import pandas as pd
from bs4 import BeautifulSoup

from nlp_services import extract_entities, load_nlp_model
from scraping import Scraping
from timed_object import TimedObject
from utils import fetch_and_parse, load_profiles, write_df_to_csv

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
random.seed(12345)


def update_output_df(df, row, affiliations, msg):
    new_row = pd.DataFrame({
        'publisher': [row['publisher']],
        'id': [row['id']],
        'url': [row['url']],
        'affiliations': [affiliations],
        'note': [msg],
    })
    return pd.concat([df, new_row], axis=0, ignore_index=True)


def load_data(filenames):
    dfs = [pd.read_csv(f"{file}", delimiter='\t') for file in filenames]
    return pd.concat(dfs, ignore_index=True)

def initialize_timers(dps, excluded_publishers):
    blocking_dic = {}
    delay_dic = {}
    for domain, attributes in dps.items():
        if attributes['publisher'] not in excluded_publishers:
            blocking_dic[domain] = False
            delay_dic[domain] = TimedObject(attributes['delay_string'], random.randint(3, 7))
    return blocking_dic, delay_dic


def write_df_if_needed(df, filename,output_df_writing_thres):
    if df.shape[0] >= output_df_writing_thres:
        write_df_to_csv(df, filename)
        return pd.DataFrame()
    return df


def main():
    
    # ----------------------------------------------------------------- Testing the html pages stored in text files


    # These lines of code is to test the scraping from files, where the source html code stored in a file, associated with a proper domian
    # for example :
    #       domain = 'ieeexplore.ieee.org'
    #       f = open("pages_examples/ieee2.txt", "r")
    
       
    #scraping = Scraping(profiles_name)
    #msg=''

    #file_text = f.read()
    #file_text = BeautifulSoup(file_text, 'html.parser')  

    #affiliations , msg = scraping.extract_aff(domain,file_text, msg)
    #for index, affiliation in enumerate(affiliations, start=1):
    #    affiliation = str(affiliation).replace('\n',' ')
    #    print(f"{index}) {affiliation}", flush=True)
    #if not affiliations: 
    #    print(msg)
    
    # ----------------------------------------------------------------- URLs from tsv files
    
    profiles_file='profiles.yaml'
    
    output_columns=['publisher','id','url','affiliations','note']
    output_df=pd.DataFrame(columns=output_columns)
    
    output_df_writing_thres = 1
    output_file_name='files/output.csv'
        
    scraping = Scraping(profiles_file)
    dps = scraping.dps

    # File paths
    #files = ['files/top_5_publishers_with_id_url_pairs.tsv', 'files/top_6_to_10_publishers_with_id_url_pairs.tsv', 'files/top_11_to_15_publishers_with_id_url_pairs.tsv', 'files/top_16_to_20_publishers_with_id_url_pairs.tsv']
    files=['files/to_test.tsv']
    
    # Load each file into a DataFrame and append to a list anf combine the dfs in cases needed
    combined_df = load_data(files)
    
    #print(combined_df)

    # List of publishers to exclude
    excluded_publishers = [
        "Oxford University Press (OUP)",
        "JSTOR",
        "Routledge",
        "IOP Publishing",
        "arXiv",
        "American Physical Society (APS)"
    ]

    
    # Filter out rows where the 'publisher' column is in the excluded publishers list
    filtered_df = combined_df[~combined_df['publisher'].isin(excluded_publishers)]
    
    # to delete the unused dfs
    del combined_df
    
    filtered_df = filtered_df.sample(frac=1,random_state=12345).reset_index(drop=True)  # Shuffle the DataFrame
    filtered_df = filtered_df.head(5)  # Select only the first 10 rows
    

    # Display the resulting DataFrame
    #print(filtered_df,flush=True)
    
    # Creating a dictionary from a DataFrame column
    keys_list = filtered_df['id'].tolist()  # Get the list of keys from the column
    
    # Initialize with -1
    checking_dic = {key: -1 for key in keys_list}
    
    blocking_dic, delay_dic = initialize_timers(dps, excluded_publishers)
    
    doi_object=TimedObject('doi.org', random.randint(3, 7))
    #doi_test_time=time.time()
    #no_doi_test_time=time.time()
    ## There is still -1 in the filtered_df
    while -1 in checking_dic.values():
        for index, row in filtered_df.iterrows():
            _publisher, _id, _url = row['publisher'], row['id'], row['url']

            if 'doi.org' in _url:
                if doi_object.is_available():
                    for domain, attributes in dps.items():
                        if str(attributes['delay_string']).lower() in str(_publisher).lower():
                            if delay_dic[domain].is_available() and not blocking_dic[domain] and checking_dic[_id]==-1:
                                #print(checking_dic)
                                # add the delay to the time objects
                                #print('>'*50,' ',time.time()-doi_test_time)
                                #doi_test_time=time.time()
                                
                                
                                doi_delay=random.randint(3, 7)
                                domain_delay=random.randint(3, 7)
                                
                                #print("doi delay: " ,doi_delay, " domain_delay: ",domain_delay,flush=True)
                                
                                doi_object=TimedObject('doi.org', doi_delay)
                                doi_object.use()
                                delay_dic[domain] = TimedObject(attributes['delay_string'], domain_delay)
                                delay_dic[domain].use()
                                
                                checking_dic[_id]=1
                                
                                affiliations=[]
                                success=False
                                msg=''
                                soup=''
                                success, msg, soup, response_url = fetch_and_parse(_url)
                                if success:
                                    affiliations, msg = scraping.extract_aff(response_url, soup,msg)
                                    for index, affiliation in enumerate(affiliations, start=1):
                                        print(f"{index}) {str(affiliation).strip()}", flush=True)
                                else:
                                    print(msg,flush=True)
                                #affs, msg = 
                                if "403" in msg and "wiley" not in response_url:
                                    blocking_dic[domain]= True
                                
                                affiliations = list(affiliations)
                                
                                
                                output_df =  update_output_df(output_df, row, affiliations, msg)
                                    
                                output_df =  write_df_if_needed(output_df, output_file_name,output_df_writing_thres)

                                
                    
                    
    #        # not doi.org url
            else:
                for domain, attributes in dps.items():
                    if str(attributes['delay_string']).lower() in str(_publisher).lower():
                        if delay_dic[domain].is_available() and not blocking_dic[domain] and checking_dic[_id]==-1:


                            #if 'ieee' in domain:
                            #    print('ieeeeeeeeeeeeeeeeeeeeeeee>>>',' ',time.time()-doi_test_time)
                            #    doi_test_time=time.time()
                            #else:
                            #    print('>'*50,' ',time.time()-no_doi_test_time)
                            #    no_doi_test_time=time.time()
                                
                            #print(checking_dic)
                            # add the delay to the time objects
                            domain_delay=random.randint(3, 7)
                            
                            #print(" domain_delay: ",domain_delay,flush=True)
                            
                            delay_dic[domain] = TimedObject(attributes['delay_string'], domain_delay)
                            delay_dic[domain].use()
                            
                            checking_dic[_id]=1
                            
                            affiliations=[]
                            success=False
                            msg=''
                            soup=''
                            success, msg, soup, response_url = fetch_and_parse(_url)
                            if success:
                                affiliations, msg = scraping.extract_aff(response_url, soup,msg)
                                for index, affiliation in enumerate(affiliations, start=1):
                                    print(f"{index}) {str(affiliation).strip()}", flush=True)
                            else:
                                print(msg,flush=True)
                            #affs, msg = 
                            if "403" in msg and "wiley" not in response_url:
                                blocking_dic[domain]= True
                            
                            affiliations = list(affiliations)
                            
                            output_df =  update_output_df(output_df, row, affiliations, msg)
                            
                            output_df =  write_df_if_needed(output_df, output_file_name,output_df_writing_thres)




if __name__ == "__main__":
    main()