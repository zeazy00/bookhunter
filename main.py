import requests
import os


url = "https://tululu.org/txt.php"
params = {
    'id': 0
}
os.makedirs("books", exist_ok=True)
for i in range(10):
    params['id'] = i+1

    response = requests.get(url, params=params)
    response.raise_for_status()
    if response.url != "https://tululu.org/":
        print(response.url)
        filename = f'books\\book{i+1}.txt'
        with open(filename, 'wb') as file:
            file.write(response.content)