import requests
from bs4 import BeautifulSoup
import json
from time import sleep

class KodificantScraper:

    BASE_URL = "https://index.kodifikant.ru"

    def __init__(self) -> None:
        self.result = []
        self.subject_links = []
        self.deep_result = []

    def get_soup(self, uri: str = "/ru/") -> BeautifulSoup:
        sleep(1)
        response = requests.get(f"{self.BASE_URL}{uri}")
        return BeautifulSoup(response.text, "lxml")

    def get_info_list(self) -> None:
        '''Get info (code, img, name and administrative center) and create info-dicts for each 
        subject federation on site, then adds them in result list'''
        tables = self.get_soup().find_all('table', class_='dTable1')
        for table in tables:
            for html_tr in table:
                code_tag = html_tr.find_next('td').text
                img_tag = html_tr.find_next('td').find_next('td')
                subject_fed_tag = img_tag.find_next('td').text
                subject_fed_link = f"{self.BASE_URL}{html_tr.find_next('a').get('href')}"
                admin_center_info = None
                if admin_center_tag := img_tag.find_next('td').find_next('td').text:
                    admin_center_link = f"{self.BASE_URL}{html_tr.find_next('a').find_next('a').get('href')}"
                    admin_center_tag = {'text': admin_center_tag, 'link': admin_center_link}
                self.result.append(
                    {
                        'code': int(code_tag),
                        'img': self.BASE_URL + img_tag.find('img').get('src'),
                        'subject_fed': {'text': subject_fed_tag, 'link': subject_fed_link},
                        'admin_c': admin_center_info
                    }
                )
        del self.result[0]

    @staticmethod
    def save_result_in_file(filename, result: list) -> None:
        '''Create one json file for all info about subjects federation'''
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(result, file, indent=4, ensure_ascii=False)

    def get_deep_info_list(self) -> None:
        '''Get info (index, name and link) and create info-dicts for each
        subject federation on site, then adds them in result list'''
        for i in range(len(self.result)):
            subject_fed_link = self.result[i]["subject_fed"]["link"]
            deep_response = requests.get(subject_fed_link)
            soup = BeautifulSoup(deep_response.text, 'lxml')
            name_tag = soup.find('td').find_next('td').text
            index_tag = soup.find('td').find_next('td').find_next('td').find_next('td').text
            self.deep_result.append(
                {
                    'index': index_tag,
                    'name': name_tag,
                    'link': subject_fed_link,
                }
            )

    def save_deep_result_in_file(self, deep_result: list) -> None:
        '''Create json file for each subject federation with info about them'''
        for counter, result in enumerate(deep_result):
            self.save_result_in_file(f'sub_fed_{self.result[counter]["code"]}.json', result)


def main() -> None:
    scraper = KodificantScrapper()
    scraper.get_info_list()
    scraper.save_result_in_file("filename.json", scraper.result)
    scraper.get_deep_info_list()
    scraper.save_deep_result_in_file(scraper.deep_result)


if __name__ == "__main__":
    main()
