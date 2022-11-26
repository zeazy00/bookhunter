import requests
import os
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filepath
from urllib.parse import urlparse

from pprint import pprint

def main():
    number_of_books = 10
    os.makedirs("books", exist_ok=True)
    os.makedirs("covers", exist_ok=True)
    os.makedirs("comments", exist_ok=True)
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
    title, _ = soup.find('body').find('table').find('h1').text.split("::")
    picture_url = soup.find('div', class_='bookimage').find('img')['src']

    filename = f"{book_id}. {title}"
    #download("https://tululu.org/txt.php", filename, params={"id": book_id})

    #img_name, extension =  os.path.splitext(picture_url.split('/')[-1])
    #download(f"https://tululu.org{picture_url}", img_name, folder="img", extension=extension)

    comments = soup.find_all('div', class_="texts")#)#.find_all('span', class_="black"))
    filepath = os.path.join("comments", sanitize_filepath(filename.strip()))
    if comments:
        with open(f"{filepath}.txt", 'wb') as file:
            for comment in comments:
                comment_text = comment.find('span', class_="black").text
                file.write(bytes(comment_text, encoding = 'utf-8'))


    genres = soup.find('span', class_="d_book").find_all('a')
    print(filename)
    for genre in genres:
        print("\t", genre.text)
    print()




def download(url, filename, params={}, redirect_check=True, folder='books', extension="txt"):
    response = requests.get(url, params=params, allow_redirects=redirect_check)
    response.raise_for_status()

    if redirect_check and check_for_redirect(response.history):
        return

    print(response.url)

    filepath = os.path.join(folder, sanitize_filepath(filename.strip()))
    with open(f"{filepath}.{extension}", 'wb') as file:
        file.write(response.content)

#def save_comments()

if __name__ == '__main__':
    main()

