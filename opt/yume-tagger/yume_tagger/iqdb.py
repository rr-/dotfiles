import re
import urllib.parse
import requests
from bs4 import BeautifulSoup


IQDB_URL = 'https://iqdb.org/'


class IqdbError(RuntimeError):
    pass


class NothingFoundIqdbError(IqdbError):
    pass


class UploadTooBigIqdbError(IqdbError):
    pass


def _query(path):
    data = {'service': list(range(100))}  # all services, present and future
    if path.startswith('http'):
        data['url'] = path
        response = requests.post(IQDB_URL, data=data)
    else:
        with open(path, 'rb') as handle:
            response = requests.post(
                IQDB_URL, files={'file': handle}, data=data
            )
    return response.text


class IqdbResult:
    def __init__(self, url, thumbnail_url):
        self.url = url
        self.thumbnail_url = thumbnail_url
        self.width = None
        self.height = None
        self.similarity = 0
        self.main = True


class IqdbResultList(list):
    def __init__(self):
        super().__init__()
        self.input_width = None
        self.input_height = None


def search(path):
    response = _query(path)
    soup = BeautifulSoup(response, 'html.parser')
    results = IqdbResultList()
    if 'too large' in response.lower():
        raise UploadTooBigIqdbError('Image is too large for IQDB to handle')
    if 'no relevant matches' in response.lower():
        raise NothingFoundIqdbError('Image not found on IQDB')

    for i, parent in enumerate(['#pages', '#more1']):
        for table_element in soup.select('%s table' % parent):
            a_elements = table_element.select('a')

            thumbnail_url = urllib.parse.urljoin(
                IQDB_URL, table_element.select('.image img')[0]['src']
            )

            similarity = None
            width = None
            height = None
            for row_element in table_element.select('tr'):
                text = row_element.text
                match = re.search(r'(\d+)% similarity', text)
                if match:
                    similarity = float(match.group(1)) / 100
                match = re.search(r'(\d+)[x×](\d+)', text)
                if match:
                    width = int(match.group(1))
                    height = int(match.group(2))

            if not a_elements:
                results.input_width = width
                results.input_height = height
                continue

            for a_element in a_elements:
                url = a_element['href']
                if url.startswith('//'):
                    url = 'http:' + url
                result = IqdbResult(url, thumbnail_url)
                result.similarity = similarity
                result.width = width
                result.height = height
                result.main = i == 0
                results.append(result)

    return results
