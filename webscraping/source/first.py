import bs4
import requests
import sys

from os.path import splitext, join
from os import getcwd


def main():
    response = requests.get('https://imgur.com/')
    soup = bs4.BeautifulSoup(response.text, 'html.parser')

    links = soup.find_all(class_='image-list-link')
    prefix = 'https:'

    for i, el in enumerate(links):
        src = el.find('img')['src']
        base, ext = splitext(src)
        image = requests.get(prefix + base[:-1] + ext)

        with open(join(getcwd(), str(i) + ext), 'wb') as f:
            f.write(image.content)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Exiting...')
        sys.exit(0)
