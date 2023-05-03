import argparse
import logging
import os
import requests
from time import sleep
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filepath
from urllib.parse import urlparse


LOG_LVL = logging.INFO


class RedirectError(Exception):
    def __str__(sell):
        return "were redirected"


def main():
    logging.basicConfig(level=LOG_LVL)
    parser = argparse.ArgumentParser(
        description="Скачивает книги с сайта https://tululu.org/ с [start_id] по [end_id]"
    )
    parser.add_argument('start_id', help='id первой книги', type=int)
    parser.add_argument('end_id', help='id последней книги', type=int)
    args = parser.parse_args()

    os.makedirs("books", exist_ok=True)
    os.makedirs("covers", exist_ok=True)
    os.makedirs("comments", exist_ok=True)
    
    for book_id in range(args.start_id, args.end_id+1):
        status = False
        attempt = 1
        while not status:
            try:
                get_book(book_id)
            except requests.exceptions.ConnectionError:
                logging.warning(f"ConnectionError | TRY: {attempt} | ID: {book_id}")
                attempt += 1
                sleep(5)
            except requests.exceptions.HTTPError:
                logging.warning("HTTPError")
                status = True
            except RedirectError:
                logging.info(f"Redirect | ID: {book_id}")
                status = True
            else:
                status = True


def get_book(book_id):
    url = f"https://tululu.org/b{book_id}/"
    response = requests.get(url, allow_redirects=True)
    response.raise_for_status()
    check_for_redirect(response)
    title, picture_path, comments, genres = parse_book_page(response, book_id)
    filename = f"{book_id}. {title}"

    download("https://tululu.org/txt.php", filename, params={"id": book_id})   
    
    img_name, extension =  os.path.splitext(picture_path.split('/')[-1])
    download(f"https://tululu.org{picture_path}", img_name, folder="covers", extension=extension)

    get_comments(filename, comments)

    genres = [genre.text for genre in genres]
    logging.info(f"{filename}\n\t{genres}")


def parse_book_page(response, book_id):
    soup = BeautifulSoup(response.text, 'lxml')
    title, _ = soup.find('body').find('table').find('h1').text.split("::")
    picture_path = soup.find('div', class_='bookimage').find('img')['src']
    comments = soup.find_all('div', class_="texts")
    genres = soup.find('span', class_="d_book").find_all('a')
    return title, picture_path, comments, genres


def get_comments(filename, comments):
    filepath = os.path.join("comments", sanitize_filepath(filename.strip()))
    if comments:
        with open(f"{filepath}.txt", 'wb') as file:
            for comment in comments:
                comment_text = comment.find('span', class_="black").text
                file.write(bytes(comment_text, encoding = 'utf-8'))
                file.write(bytes("\n\n", encoding = 'utf-8'))


def check_for_redirect(response):
    if response.history:
        raise RedirectError


def download(url, filename, params={}, redirect_check=True, folder='books', extension="txt"):
    response = requests.get(url, params=params, allow_redirects=redirect_check)
    response.raise_for_status()

    if redirect_check:
        check_for_redirect(response)

    filepath = os.path.join(folder, sanitize_filepath(filename.strip()))
    with open(f"{filepath}.{extension}", 'wb') as file:
        file.write(response.content)


if __name__ == '__main__':
    main()

