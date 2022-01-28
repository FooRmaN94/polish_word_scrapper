from bs4 import BeautifulSoup
import urllib.request
def get_letters(url):
    html = urllib.request.urlopen(url)
    main_page = BeautifulSoup(html, 'html.parser')
    letters_unwrapped = main_page.find(class_="base-alfa")
    letters_unwrapped = letters_unwrapped.find_all("a")
    letter = []
    for letters in letters_unwrapped:
        letter.append(letters.get_text())
    return letter

letter = get_letters("https://sjp.pwn.pl/sjp/lista/A.html")
print(letter)

