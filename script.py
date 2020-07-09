import json
import csv
import mechanize
from bs4 import BeautifulSoup
from http import cookiejar

import utils

with open('credentials.json') as json_file:
    credentials = json.load(json_file)

with open('slots_wanted.csv') as csv_file:
    reader = csv.reader(csv_file)
    slot_header = next(reader)
    slots_wanted = list(reader)

credentials_needed = True

cj = cookiejar.CookieJar()
br = mechanize.Browser()
br.set_cookiejar(cj)
br.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0')]

url_book_header = "https://www.reservauto.net/Scripts/client/ReservationDisponibility.asp?CurrentLanguageID=1&IgnoreError=False&CityID=59&StationID=C&CustomerLocalizationID=&OrderBy=2&Accessories=0&Brand=&ShowGrid=False&ShowMap=False&DestinationID=&FeeType=80"

if credentials_needed:
    url_random = url_book_header + "&StartYear=2020&StartMonth=07&StartDay=11&StartHour=8&StartMinute=0&EndYear=2020&EndMonth=07&EndDay=12&EndHour=18&EndMinute=0"
    # submit the first form to use communauto québec
    br.open(url_random)
    br.select_form(nr=0)
    br.submit()
    # submit the login form with credentials
    br.select_form(nr=0)
    br.form['Username'] = credentials['username']
    br.form['Password'] = credentials['password']
    br.submit()

    # validate again for accessing the booking
    br.select_form(nr=0)
    br.submit()

for slot in slots_wanted:
    dateBegin = f"{slot[2]}/{slot[1]}/{slot[0]} {slot[3]}:{slot[4]}"
    dateEnd = f"{slot[7]}/{slot[6]}/{slot[5]} {slot[8]}:{slot[9]}"

    url_book_slot = url_book_header
    for idx, attr in enumerate(slot_header):
        url_book_slot += "&" + attr + "=" + slot[idx]
    br.open(url_book_slot)
    soup = BeautifulSoup(br.response().read().decode("utf-8"), features="lxml")
    soup = soup.find('table')
    td_cars = soup.find_all('td', {'class': 'greySpecial'})
    cars = []
    if len(td_cars) > 0:
        nb_cars = len(td_cars) // 3
        print(dateBegin + " -> " + dateEnd + " : ")
        for curr_car in range(0, nb_cars):
            td_car = td_cars[curr_car * 3:(curr_car + 1) * 3]
            station_name = td_car[0].text.strip()
            station_ID = td_car[0].contents[1].attrs['href'].strip()
            station_ID = station_ID.partition("StationID=")[2].partition("\'")[0]
            station_stored_infos = utils.get_station(station_ID)
            my_coords = td_car[1].contents[1].attrs['href'].strip()
            my_coords = my_coords.partition("false, ")[2].partition(");")[0].split(",")[0:2]
            car_desc = td_car[2].get_text(' ').strip()
            distance = utils.get_distance(my_coords, [station_stored_infos['Longitude'], station_stored_infos['Latitude']])
            print(f"* {station_name} at {distance}km : {car_desc}")
