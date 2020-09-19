import os
import sys
import requests as req
import wget
from bs4 import BeautifulSoup as soup
import json
from tqdm import tqdm

config = json.load(open('config.json'))

chapter_name_html = '<h3>{}</h3>'

img_in = '<img src="images/{}.jpg" alt="page{}" style="display:block;width:50%">'

html_in = '<!DOCTYPE html><head><link rel="stylesheet" href="/cdn-cgi/styles/main.css" type="text/css" /></head><body><center>{}</center></body></html>'


def banner():
    # App banner
    banner_ascii = '''
    ,ggg, ,ggg,_,ggg,                                                     ,ggg,          ,gg
    dP""Y8dP""Y88P""Y8b                                                   dP"""Y8,      ,dP' 
    Yb, `88'  `88'  `88                                                   Yb,_  "8b,   d8"   
    `"  88    88    88                                                    `""    Y8,,8P'    
        88    88    88                                                            Y88"      
        88    88    88    ,gggg,gg   ,ggg,,ggg,     ,gggg,gg    ,gggg,gg         ,888b      
        88    88    88   dP"  "Y8I  ,8" "8P" "8,   dP"  "Y8I   dP"  "Y8I        d8" "8b,    
        88    88    88  i8'    ,8I  I8   8I   8I  i8'    ,8I  i8'    ,8I      ,8P'    Y8,   
        88    88    Y8,,d8,   ,d8b,,dP   8I   Yb,,d8,   ,d8I ,d8,   ,d8b,    d8"       "Yb, 
        88    88    `Y8P"Y8888P"`Y88P'   8I   `Y8P"Y8888P"888P"Y8888P"`Y8  ,8P'          "Y8
                                                        ,d8I'                               
                                                    ,dP'8I                                
                                                    ,8"  8I                                
                                                    I8   8I                                
                                                    `8, ,8I                                
                                                    `Y8P"                                 
    '''
    return banner_ascii


def chk_dir():
    os.chdir(config['download_location'])
    directories = os.listdir()

    if 'MangaX' not in directories:
        os.mkdir(config['download_location'] + '\\MangaX')
        os.chdir("D:\\Downloads\\MangaX")
    else:
        os.chdir("D:\\Downloads\\MangaX")


def parse_name(name):
    name_to_return = name
    allowed_characters = "QWERTYUIOPLKJHGFDSAZXCVBNMqwertyuioplkjhgfdsazxcvbnm-_1234567890."
    for x in name_to_return:
        if x in allowed_characters:
            continue
        if x == '&':
            name_to_return = name_to_return.replace(x, 'and')
        name_to_return = name_to_return.replace(x, ' ')
    return name_to_return


def manga_dir(manga):
    name = manga['Name']
    directory = config['download_location'] + '\\MangaX' + '\\{}'.format(name)
    if os.getcwd() != 'D:\\Downloads\\MangaX':
        os.chdir(config['download_location'] + '\\MangaX')
    if name not in os.listdir():
        os.mkdir(directory)
        os.chdir(directory)
    else:
        os.chdir(directory)


def get_search_result(genre):
    manga_list = []
    index = 0
    search_url = config['urls']['search_url'].format(genre).replace(' ', '_')

    uClient = req.get(search_url)
    client_html = uClient.text
    client_soup = soup(client_html, 'lxml')
    homepage_items = client_soup.findAll(
        "div", {"class": "search-story-item"})
    # print(len(homepage_items))

    for homepage_item in homepage_items:
        try:
            manga_name = parse_name(homepage_item.div.h3.a.text)
            manga_link = homepage_item.div.h3.a["href"]

            manga_list.append(
                {"Name": manga_name, "Link": manga_link})

            index = index + 1
            if index == 10:
                break
        except UnboundLocalError:
            print("local variable 'index' referenced before assignment")
        except:
            print('An error occoured')

    return manga_list


def get_chapters(manga):
    chapter_list = []

    uClient = req.get(manga['Link'])
    client_html = uClient.text
    client_soup = soup(client_html, 'lxml')

    chapters = client_soup.findAll("li", {"class": "a-h"})

    start = 0
    stop = 10
    index = 0

    while index < len(chapters):
        chapter_list.clear()
        for chapter in range(start, stop):
            index += 1
            try:
                chapter_list.append({
                    'chapter_name': chapters[chapter].a.text,
                    'chapter_link': chapters[chapter].a['href']
                })
            except:
                print('an error occoured')
                break
        start += 10
        stop += 10
        yield chapter_list


def download_chapters(manga_chapters, choice):
    try:
        if '-' in choice:
            choices = choice.split('-')
            for i in range(int(choices[0]), int(choices[1])+1):
                chapter = manga_chapters[int(i)-1]
                directory = os.getcwd() + '\\' + \
                    parse_name(chapter['chapter_name'])
                if parse_name(chapter['chapter_name']) not in os.listdir():
                    os.mkdir(directory)
                os.chdir(directory)
                download(chapter)
                os.chdir('..')
        else:
            choices = choice.split(',')
            for i in choices:
                chapter = manga_chapters[int(i)-1]
                directory = os.getcwd() + '\\' + \
                    parse_name(chapter['chapter_name'])
                if parse_name(chapter['chapter_name']) not in os.listdir():
                    os.mkdir(directory)
                os.chdir(directory)
                download(chapter)
                os.chdir('..')
    except:
        return False
    return True


def download(chapter):
    link = chapter['chapter_link']
    pages = []

    uClient = req.get(link)
    client_html = uClient.text
    client_soup = soup(client_html, 'lxml')
    pages_container = client_soup.find(
        "div", {"class": "container-chapter-reader"})

    pages = pages_container.findAll('img')
    directory = os.getcwd() + '\\images'
    if 'images' not in os.listdir():
        os.mkdir(directory)
    os.chdir(directory)
    print('\nDownloading {}: \n'.format(chapter['chapter_name']))
    for i in tqdm(range(0, len(pages))):
        headers = {
            'referer': link
        }
        r = req.get(pages[i]['src'], stream=True, headers=headers)
        downloaded_file = open("{}.jpg".format(i), "wb")
        for chunk in r.iter_content(chunk_size=256):
            if chunk:
                downloaded_file.write(chunk)
    os.chdir('..')

    read_html = open("Read.html", "w")
    chapters_html = chapter_name_html.format(chapter['chapter_name']).upper()
    for i in range(0, len(pages)):
        chapters_html += img_in.format(i, i)
    chapters_html += chapter_name_html.format(chapter['chapter_name']).upper()
    read_html.write(html_in.format(chapters_html))


try:
    if __name__ == "__main__":
        print(banner())
        print("\nAll manga are gotten from www.manganelo.com/\nAnd saved to MangaX in your downloads folder.")
        # check_update()

        chk_dir()

        manga_name = None
        manga_chapters = []

        if len(sys.argv) == 2:
            manga_name = sys.argv[1]
        else:
            manga_name = input("\nWhat manga do you wanna download today::: ")
        search_result = get_search_result(manga_name)

        if len(search_result) == 0:
            print('MangaX found no results for "{}"'.format(manga_name))
            exit()

        print("\nSearch results for", manga_name)
        for i, j in enumerate(search_result):
            print(i + 1, " - " + j["Name"])
        choice = int(input("\nWhich one? Enter the number of your choice::: "))

        manga = search_result[choice - 1]
        manga_name = manga['Name']
        manga_dir(manga)
        chapter_gen = get_chapters(manga)

        more = True

        print("\nChapters for", manga_name)
        index = 1
        while more:
            try:
                chapters = next(chapter_gen)
                for chapter in chapters:
                    print(index, " - " + chapter["chapter_name"])
                    index += 1
                manga_chapters += chapters
                more = True if input(
                    "\nMore Chapters? (y/n)::: ").lower() == 'y' else False
            except:
                print('Oops! No more chapters!')
                break

        choice = input(
            "\nWhich one? Enter the number of your choice.\nEnter multiple choices seperated by commas (,)\nEg. 1,4,6,7,8::: ")

        success = download_chapters(manga_chapters, choice)

        if success:
            print('\nDone!')
        else:
            print('\nAn error occoured')

        exit()
except:
    exit()
