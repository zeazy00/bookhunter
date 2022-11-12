import requests
import os
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filepath
from urllib.parse import urlparse

def main():
    number_of_books = 10
    os.makedirs("books", exist_ok=True)
    os.makedirs("img", exist_ok=True)
    for book_id in range(1, number_of_books+1):
        url = f"https://tululu.org/b{book_id}/"
        response = requests.get(url, allow_redirects=True)
        response.raise_for_status()
        if check_for_redirect(response.history):
            continue
        else:  
            get_book_with_covers(response, book_id)


def check_for_redirect(history):
    return history


def get_book_with_covers(response, book_id):
    soup = BeautifulSoup(response.text, 'lxml')
    title, _ = soup.find('body').find('table').find('h1').text.split("::")#служебное, удалить после отсладки
    picture_url = soup.find('div', class_='bookimage').find('img')['src']
    print()

    filename = f"{book_id}. {title}"
    download("https://tululu.org/txt.php", filename, params={"id": book_id})

    filename, extension =  os.path.splitext(picture_url.split('/')[-1])
    download(f"https://tululu.org{picture_url}", filename, folder="img", extension=extension)


def download(url, filename, params={}, redirect_check=True, folder='books', extension="txt"):
    response = requests.get(url, params=params, allow_redirects=redirect_check)
    response.raise_for_status()

    if redirect_check and check_for_redirect(response.history):
        return

    print(response.url)

    filepath = os.path.join(folder, sanitize_filepath(filename.strip()))
    with open(f"{filepath}.{extension}", 'wb') as file:
        file.write(response.content)


if __name__ == '__main__':
    main()

