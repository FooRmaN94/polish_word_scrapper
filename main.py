import random

from bs4 import BeautifulSoup
import urllib.request


def get_pages(page):
    html = urllib.request.urlopen(page)
    page = BeautifulSoup(html, 'html.parser')
    pagination = page.find(class_="pagination")
    pagination = pagination.find_all("li")
    max = int(pagination[len(pagination)-2].get_text())+1
    return range(1, max, 1)


def get_letters(url):
    html = urllib.request.urlopen(url)
    main_page = BeautifulSoup(html, 'html.parser')
    letters_unwrapped = main_page.find(class_="base-alfa")
    letters_unwrapped = letters_unwrapped.find_all("a")
    letter = []
    for letters in letters_unwrapped:
        letter.append(letters.get_text())
    return letter


def get_words(url, list):
    page = urllib.request.urlopen(url)
    print("tryinng to get url: ", url)
    html = BeautifulSoup(page, 'html.parser')
    table = html.find_all(class_="lista")
    for row in table:
        words_unwrapped=row.find_all("a")
        for word in words_unwrapped:
            text = word.get_text()
            text = text.replace("\xa0", " ")
            list.append(text)


def return_random_list():
    list= []
    for x in range(1, random.randrange(1, 10)):
        list.append(x)
    return list


def get_all_worlds_from_letter(letter):
    url = "https://sjp.pwn.pl/sjp/lista/"+letter+".html"
    numbers = get_pages(url)
    list = []
#    for number in numbers:
#        url = "https://sjp.pwn.pl/sjp/lista/"+letter+":"+str(number)+".html"
    for number in numbers:
        url = "https://sjp.pwn.pl/sjp/lista/" + letter + ";" + str(number) + ".html"
        get_words(url, list)
    return list