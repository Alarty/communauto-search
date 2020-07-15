import json
import csv
import mechanize
from bs4 import BeautifulSoup
from http import cookiejar

import utils

# get username and password for the login page
with open('credentials.json') as json_file:
    credentials = json.load(json_file)

# load the user needed slots from csv (start and end : year, month, day, hour, minute)
with open('slots_wanted.csv') as csv_file:
    reader = csv.reader(csv_file)
    # store the headers
    slot_header = next(reader)
    # store the rest into a array
    slots_wanted = list(reader)

credentials_needed = True

# create the fake browser
cj = cookiejar.CookieJar()
br = mechanize.Browser()
br.set_cookiejar(cj)
br.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0')]

# start of a URL with parameters except date ones
url_book_header = "https://www.reservauto.net/Scripts/client/ReservationDisponibility.asp?CurrentLanguageID=1&IgnoreError=False&CityID=59&StationID=C&CustomerLocalizationID=&OrderBy=2&Accessories=0&Brand=&ShowGrid=False&ShowMap=False&DestinationID=&FeeType=80"

if credentials_needed:
    url_random = url_book_header + "&StartYear=2020&StartMonth=07&StartDay=11&StartHour=8&StartMinute=0&EndYear=2020&EndMonth=07&EndDay=12&EndHour=18&EndMinute=0"
    # submit the first form to choose "communauto québec"
    br.open(url_random)
    br.select_form(nr=0)
    br.submit()
    # submit the login form with user credentials
    br.select_form(nr=0)
    br.form['Username'] = credentials['username']
    br.form['Password'] = credentials['password']
    br.submit()

    # validate again the form to choose "communauto québec" for accessing the booking
    br.select_form(nr=0)
    br.submit()

# for each slot of the csv file
for slot in slots_wanted:
    str_dateBegin = f"{slot[2]}/{slot[1]}/{slot[0]} {slot[3]}:{slot[4]}"
    str_dateEnd = f"{slot[7]}/{slot[6]}/{slot[5]} {slot[8]}:{slot[9]}"

    # generate url from params
    url_book_slot = url_book_header
    for idx, attr in enumerate(slot_header):
        url_book_slot += "&" + attr + "=" + slot[idx]
    br.open(url_book_slot)

    #scrap the webpage for the content
    soup = BeautifulSoup(br.response().read().decode("utf-8"), features="lxml")
    soup = soup.find('table')
    td_cars = soup.find_all('td', {'class': 'greySpecial'})
    # loop through the content to get each row of cars and extract it content
    cars = []
    if len(td_cars) > 0:
        nb_cars = len(td_cars) // 3
        print(str_dateBegin + " -> " + str_dateEnd + " : ")
        # loop every 3 rows = every car
        for curr_car in range(0, nb_cars):
            td_car = td_cars[curr_car * 3:(curr_car + 1) * 3]
            # station name is just text of the html
            station_name = td_car[0].text.strip()
            # station id is part of the weblink of a tag, we have to extract it from str partitions
            station_ID = td_car[0].contents[1].attrs['href'].strip()
            station_ID = station_ID.partition("StationID=")[2].partition("\'")[0]
            # get station infos from id
            station_stored_infos = utils.get_station_from_id(station_ID)
            # user coordinates is part of the weblink of a tag, we have to extract it from str partitions
            user_coords = td_car[1].contents[1].attrs['href'].strip()
            user_coords = user_coords.partition("false, ")[2].partition(");")[0].split(",")[0:2]
            # car desc is just text of the html
            car_desc = td_car[2].get_text(' ').strip()
            # calculate distance between user coords and station coords from infos
            distance = utils.get_distance(user_coords, [station_stored_infos['Longitude'], station_stored_infos['Latitude']])
            print(f"* {station_name} at {distance}km : {car_desc}")
