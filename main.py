import random
import os
from bs4 import BeautifulSoup
import urllib.request
import sqlite3


def get_pages(page):
    html = urllib.request.urlopen(page)
    page = BeautifulSoup(html, 'html.parser')
    pagination = page.find(class_="pagination")
    pagination = pagination.find_all("li")
    max = int(pagination[len(pagination) - 2].get_text()) + 1
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


def insert_into_table(word, cursor):
    cursor.execute(f'''INSERT INTO Words(first, second, third, fourth, fifth, word) VALUES ("{word[0]}","{word[1]}",
    "{word[2]}","{word[3]}","{word[4]}","{word}")''')


def get_words(url, list):
    page = urllib.request.urlopen(url)
    print("tryinng to get url: ", url)
    html = BeautifulSoup(page, 'html.parser')
    table = html.find_all(class_="lista")
    for row in table:
        words_unwrapped = row.find_all("a")
        for word in words_unwrapped:
            text = word.get_text()
            text = text.replace("\xa0", " ")
            list.append(text)


def return_random_list():
    list = []
    for x in range(1, random.randrange(1, 10)):
        list.append(x)
    return list


def get_all_worlds_from_letter(letter):
    url = "https://sjp.pwn.pl/sjp/lista/" + letter + ".html"
    numbers = get_pages(url)
    list = []
    for number in numbers:
        url = "https://sjp.pwn.pl/sjp/lista/" + letter + ";" + str(number) + ".html"
        get_words(url, list)
    return list


def read_all_files():
    db = "words.db"
    if os.path.isfile(db):
        print("wszystko w gicie")
        con = sqlite3.connect(db)
        cursor = con.cursor()
        print(cursor.fetchall())
        files = []
        i = 0
        for x in os.listdir():
            if x.endswith(".txt"):
                files.append(x)
                with open(x, 'r') as r:
                    data = r.read()
            text = data.split(", ")
            for word in text:
                word = word.replace("[", "")
                word = word.replace("]", "")
                word = word.replace("'", "")
                if len(word) == 5:
                    if word.find("  ") == -1 and word.find("-") == -1 and word.find(" ") == -1 and word.find("-") == -1:
                        insert_into_table(word.lower(), cursor)
        con.commit()
        con.close()
    else:
        print("Nie ma takiej bazy")

def read_database():
    db = "words.db"
    con = sqlite3.connect(db)
    cursor = con.cursor()
    cursor.execute('''Select word from Words where first LIKE("A")''')
    print(cursor.fetchall())
    con.close()

def make_query(word, missplaced):
    query = "Select DISTINCT word from words where"
    columns = ["first", "second", "third", "fourth", "fifth"]
    for i, position in enumerate(word):
        if i == 0:
            query += "("
        else:
            query += " and ("

        for j, letter in enumerate(position):
            if j == 0:
                query += columns[i] + "='" +letter+ "'"
            else:
                query += " or " + columns[i] + "= '" +letter+ "'"
        query += ")"
    for i, item in enumerate(missplaced):
        query += " and word like \"%" + item + "%\""
    db = "words.db"
    con = sqlite3.connect(db)
    cursor = con.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    con.close()
    return data


def delete_from_list(list, letter, all=False):
    if all:
        list.clear()
        list.append(letter)
    else:
        for i in range(0,  len(list)):
            if list[i] == letter:
                list.pop(i)
                return


def missplaced_check(missplaced, word, actual_letter=None):
    letters = []
    index_to_delete =[]
    if(actual_letter != None):
        letters.append(actual_letter)
    for letter in word:
        if len(letter) == 1:
            letters.append(letter)
    for k, lett in enumerate(missplaced):
        for item in letters:
            if lett == item:
                if (actual_letter == None):
                    index_to_delete.append(k)
                else:
                    return
    if (actual_letter != None):
        missplaced.append(actual_letter)
    else:
        index_to_delete.reverse()
        for item in index_to_delete:
            missplaced.pop(item)


def letter_state(missplaced, word, letter, position):
    while True:
        print("na pozycji ", (position+1), " wystepuje litera ",letter,"?\n")
        x = input("0 - nie ma litery\n1 - jest ale na innej pozycji\n2 - jest!\n")
        x = int(x)
        if x == 0:
            for i, row in enumerate(word):
                delete_from_list(word[i], letter)
            break
        elif x == 1:
            delete_from_list(word[position], letter)
            missplaced_check(missplaced, word, letter)
            break
        elif x == 2:
            delete_from_list(word[position], letter, True)
            break
        print(word)
    return word


def count_apperances(letters):
    probabilities = []
    db = "words.db"
    con = sqlite3.connect(db)
    cursor = con.cursor()
    query = "Select distinct Count() from words"
    cursor.execute(query)
    row_count = cursor.fetchone()[0]
    for current_position, position in enumerate(letters):
        table = []
        for letter in position:
            table.append(count_letter_apperances(letter, row_count, current_position, cursor))
        probabilities.append(table.copy())
    return probabilities


def count_letter_apperances(letter, row_count, position, cursor):
    columns = ['first', 'second', 'third', 'fourth', 'fifth']
    query = "Select distinct Count() from words where " + columns[position] + " ='"+letter+"'"
    cursor.execute(query)
    result = cursor.fetchone()[0]
    percent = float(result) / float(row_count)
    return letter, percent

def calculate_score(letter, prob):
    for item in prob:
        if letter == item[0]:
            return item[1]

def show_most_possible(prob, words, limit_to_single_letters = False):
    word_list = []
    for word in words:
        word = word[0]
        score = calculate_score(word[0], prob[0]) + calculate_score(word[1], prob[1]) + calculate_score(word[2], prob[2]) + calculate_score(word[3], prob[3]) + calculate_score(word[4], prob[4])
        result = (word, score)
        word_list.append(result)
        word_list = sorted(word_list, key=lambda sort: sort[1], reverse=True)
        if limit_to_single_letters:
            to_delete =  []
            for i, word in enumerate(word_list):
                for char in word[0]:
                    if word[0].count(char) > 1:
                        to_delete.append(i)
                        break
            for i in sorted(to_delete, reverse=True):
                word_list.pop(i)
    return word_list

def main():
    #play = False
    play = True
    missplaced = []
    letters = ["a", "ą", "b", "c", "ć", "d", "e", "ę", "f", "g", "h", "i", "j", "k", "l", "ł", "m", "n", "ń", "o", "ó",
               "p", "r", "s", "ś", "t", "u", "w", "y", "z", "ż", "ź"]
    guessed = [letters.copy(), letters.copy(), letters.copy(), letters.copy(), letters.copy()]
    if play:
        chances = 5
        for _ in range(0, chances):
            if _==0:
                print("best to use:  kobea")
            else:
                score = show_most_possible(count_apperances(guessed), make_query(guessed, missplaced))
                score = sorted(score, key=lambda s: s[1], reverse=True)
                print("best to use: ", score[:10])
            a = input("Podaj 5 literowe slowo\n")
            a = a.lower()
            for i, letter in enumerate(a):
                guessed = letter_state(missplaced, guessed, letter, i)
            missplaced_check(missplaced, guessed)
            response = (make_query(guessed, missplaced))
            print("found ", len(response), " matches")
            print(response)
            prob = count_apperances(guessed)
    else:
        print('x')
if __name__ == "__main__":
    main()
