import re

from bs4 import BeautifulSoup
from lxml import html

import udfs
from utils import load_profiles


class Scraping:
    def __init__(self, config_file):
        self.dps = load_profiles(config_file)

    def extract_aff(self, response_url, soup, msg):
        affs_arr = set()
        aff_flag = False
        domain_ = ''
        
        for domain, attributes in self.dps.items():
            if domain in response_url:
                domain_ = domain
                
                if 'regex' in attributes:
                    affs_arr.update(self._regex_extraction(str(soup), domain))
                    
                if 'xpath' in attributes:
                    affs_arr.update(self._xpath_extraction(html.fromstring(str(soup)), domain))
                    
                if affs_arr and not aff_flag:
                    aff_flag = True
        if not affs_arr:
            aff_flag = True
            msg += f"Could not find the affiliation in the page of {response_url} "
            
        if not aff_flag:
            msg += "Not in the response_url"
            
        return affs_arr, msg

    def _regex_extraction(self, html_tree, domain):
        found_affs = set()
        msg = ''
        regex = self.dps[domain]['regex']
        match = re.search(regex, html_tree, re.DOTALL)
        
        if match:
            udf_name = self.dps[domain].get('udf')
            if udf_name:
                # Get the function object by its name from the udfs module
                udf_function = getattr(udfs, udf_name, None)
                if udf_function:
                    # Call the function with data
                    return udf_function(match)
                else:
                    print(f"No function named {udf_name} found.")
        return found_affs

    def _xpath_extraction(self, html_tree, domain):
        found_affs = set()
        xpath = self.dps[domain]['xpath']
        found_affs.update(set(html_tree.xpath(xpath)))
        return found_affs


# Example usage:
if __name__ == "__main__":
    scraping_tool = Scraping('profiles.yaml')
    # example_url and example_soup need to be defined or loaded here
    # msg initially should be an empty string or predefined message
    response_url = "https://example.com"
    soup = BeautifulSoup("<html></html>", 'html.parser')  # Dummy soup object for the sake of example
    msg = ""
    affiliations, message = scraping_tool.extract
