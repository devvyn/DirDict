from os import getcwd

import requests
from bs4 import BeautifulSoup

from storage.file_system import FileSystemStorage


class IndeedJobSearchScraper:
    base_href = 'https://www.indeed.ca'
    default_search_url = '/jobs?q=software+developer&l=Saskatoon%2C+SK&radius=25&limit=5'

    def do_it(self):
        base_href = self.base_href
        search_url = self.default_search_url
        search_result_selector = '.result a[data-tn-element="jobTitle"]'

        # if cache_miss:
        cache = FileSystemStorage()
        # @todo provide URL for requestes.get()
        search_response = cache.get(base_href + search_url) or requests.get()

        # save to file, keep in memory

        search_response_text = search_response.text
        search_response_parser = BeautifulSoup(search_response_text, 'html5lib')
        search_response_elements = search_response_parser.select(search_result_selector)

        for element in search_response_elements:
            print(f'[{element.text}]({element.get("href")})')

        # job_page_summary_element = {'id': 'job_summary'}


if __name__ == '__main__':
    # IndeedJobSearchScraper().do_it()
    print(getcwd())
