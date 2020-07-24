import json
import csv
import pprint

import mechanize
from bs4 import BeautifulSoup
from http import cookiejar
import os

import utils

results_file = 'results.json'

# Load slots from static csv file or from google drive file
internal_slots_file = 'slots_wanted.csv'
if os.path.isfile(internal_slots_file):
    # load the user needed slots from csv (start and end : year, month, day, hour, minute)
    with open(internal_slots_file) as csv_file:
        reader = csv.reader(csv_file)
        # store the headers
        slots_header = next(reader)
        # store the rest into a array
        slots_wanted = list(reader)
else:
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials

    # use creds to create a client to interact with the Google Drive API
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']

    secret_name = "gdrive_client_secret"
    if os.path.isfile(f"{secret_name}.json"):
        creds = ServiceAccountCredentials.from_json_keyfile_name(f'{secret_name}.json', scope)
    elif secret_name in os.environ.keys():
        print(os.environ[secret_name])
        print("****************************")
        print(json.loads(os.environ[secret_name]))
        creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(os.environ[secret_name]), scope)
    else:
        raise Exception(f"You should have a {secret_name}.json file or the json content of it as envvar")
    client = gspread.authorize(creds)
    # Make sure you use the right name here
    sheet = client.open("communauto-slots").sheet1
    list_of_hashes = sheet.get_all_records()
    slots_header = list(list_of_hashes[0].keys())
    slots_wanted = [list(row.values()) for row in list_of_hashes]
slots_wanted = utils.convert_to_dates(slots_wanted)
# do not test for dates already passed
slots_wanted = utils.remove_passed_dates(slots_wanted)

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
    br.form['Username'] = os.environ['communauto_user']
    br.form['Password'] = os.environ['communauto_pwd']
    br.submit()

    # validate again the form to choose "communauto québec" for accessing the booking
    br.select_form(nr=0)
    br.submit()
slots = {}
if len(slots_wanted) == 0:
    print("Only old slots or no slots to look for")

# for each slot of the csv file
for slot in slots_wanted:
    str_dateBegin = f"{slot[0].day}/{slot[0].month}/{slot[0].year} {slot[0].hour}:{slot[0].minute}"
    str_dateEnd = f"{slot[1].day}/{slot[1].month}/{slot[1].year} {slot[1].hour}:{slot[1].minute}"
    id_slot = f"{str_dateBegin}->{str_dateEnd}"

    # generate url from params
    url_book_slot = url_book_header
    date_url_strs_list = [slot[0].year, slot[0].month, slot[0].day, slot[0].hour, slot[0].minute,
                          slot[1].year, slot[1].month, slot[1].day, slot[1].hour, slot[1].minute]
    for idx, attr in enumerate(slots_header):
        url_book_slot += "&" + attr + "=" + str(date_url_strs_list[idx])
    br.open(url_book_slot)

    print(url_book_slot)
    # scrap the webpage for the content
    soup = BeautifulSoup(br.response().read().decode("utf-8"), features="lxml")
    soup = soup.find('table')
    soup_stations = soup.select("a[href*=InfoStation]")
    soup_coords = soup.select("a[href*=BillingRulesAcpt]")
    soup_descs = soup.find_all('td', {'align': "center", "width": "420"})[1:]
    assert len(soup_stations) == len(soup_coords) == len(soup_descs)

    # slots to store everything
    slot = {"dateBegin": str_dateBegin, "dateEnd": str_dateEnd, "url": url_book_slot, "cars": []}
    # loop through the content to get each row of cars and extract it content
    if len(soup_stations) > 0:
        # loop every 3 rows = every car
        for car_idx in range(0, len(soup_stations)):
            # station name is just text of the html
            station_name = soup_stations[car_idx].text.strip()
            # station id is part of the weblink of a tag, we have to extract it from str partitions
            station_ID = soup_stations[car_idx].attrs['href'].strip()
            station_ID = station_ID.partition("StationID=")[2].partition("\'")[0]
            # get station infos from id
            station_stored_infos = utils.get_station_from_id(station_ID)
            # user coordinates is part of the weblink of a tag, we have to extract it from str partitions
            user_coords = soup_coords[car_idx].attrs['href'].strip()
            user_coords = user_coords.partition("false, ")[2].partition(");")[0].split(",")[0:2]
            # car desc is just text of the html
            car_desc = soup_descs[car_idx].get_text(' ').strip()
            # calculate distance between user coords and station coords from infos
            distance = utils.get_distance(user_coords,
                                          [station_stored_infos['Longitude'], station_stored_infos['Latitude']])
            slot["cars"].append({"Name": station_name, "distance": distance, "description": car_desc})
        slots[id_slot] = slot

flag_new, new_slots = utils.compare_results(slots, results_file)
if flag_new:
    pprint.pprint(new_slots)
    utils.send_mail(new_slots, os.environ["communauto_mailto"])
