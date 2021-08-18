import ast
import json
import csv
import pprint
import os
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import urllib.request
from webdriver_manager.chrome import ChromeDriverManager

import utils
import GDriveConnection


results_filename = 'communauto-results'
internal_slots_filename = 'communauto-slots'
liststation_filename = 'ListStations.xml'

url_liststation = 'https://www.reservauto.net/Scripts/Ajax/Stations/ListStations.asp'
url_login = 'https://quebec.client.reservauto.net/legacy/login?locale=fr-CA'
url_reservation = 'https://quebec.client.reservauto.net/bookCar'
# Create the connection to Gdrive if needed (with json file or env var)
gdrive_conn = None
if "gdrive_results" in os.environ.keys():
    secret_name = "gdrive_client_secret"
    if os.path.isfile(f"{secret_name}.json"):
        gdrive_conn = GDriveConnection.GDriveConnection(json_filename=f"{secret_name}.json")
    elif secret_name in os.environ.keys():
        gdrive_conn = GDriveConnection.GDriveConnection(json_content=json.loads(os.environ.get('gdrive_client_secret')))
    else:
        raise Exception(
            f"You should have a {secret_name}.json file or the json content of it as 'gdrive_client_secret' envvar")

results_fileid = None
# Load old results json file locally or through Gdrive connection
if not "gdrive_results" in os.environ.keys():
    if os.path.isfile(f"{results_filename}.json"):
        with open(f"{results_filename}.json") as json_file:
            old_slots = json.load(json_file)
    else:
        old_slots = None
else:
    results_fileid, old_slots = gdrive_conn.get_byte_file(results_filename)
    if old_slots is not None:
        old_slots = json.loads(old_slots)
        print("old slots :")
        print(old_slots)

# Load the csv locally or with Gdrive connection
# contains user needed slots (start and end : year, month, day, hour, minute)
if os.path.isfile(f"{internal_slots_filename}.csv"):
    with open(f"{internal_slots_filename}.csv") as csv_file:
        reader = csv.reader(csv_file)
        # store the headers
        slots_header = next(reader)
        # store the rest into a array
        slots_wanted = list(reader)
else:
    rows = gdrive_conn.get_sheet_file(internal_slots_filename)
    if len(rows) == 0:
        print("Only old slots or no slots to look for. Stop execution here")
        exit()
    slots_header = list(rows[0].keys())
    slots_wanted = [list(row.values()) for row in rows]

slots_wanted = utils.convert_to_dates(slots_wanted)
# do not test for dates already passed
slots_wanted = utils.remove_passed_dates(slots_wanted)


chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("window-size=1920x1480")
chrome_options.add_argument("disable-dev-shm-usage")
driver = webdriver.Chrome(
    chrome_options=chrome_options, executable_path=ChromeDriverManager().install()
)

# update list of stations
# urllib.request.urlretrieve(url_liststation, liststation_filename)

# login
driver.get(url_login)
time.sleep(3)
print('---')

login = driver.find_element_by_id("Username").send_keys(os.environ['communauto_user'])
password = driver.find_element_by_id("Password").send_keys(os.environ['communauto_pwd'])
submit = driver.find_element_by_id("btnlogin").click()

new_slots = {}
# for each slot of the csv file
for slot in slots_wanted:
    str_dateBegin = f"{slot[0].day}/{slot[0].month}/{slot[0].year} {slot[0].hour}:{slot[0].minute}"
    str_dateEnd = f"{slot[1].day}/{slot[1].month}/{slot[1].year} {slot[1].hour}:{slot[1].minute}"
    id_slot = f"{str_dateBegin}->{str_dateEnd}"

    print(f"Look for slot : {id_slot}")

    # fill the form
    driver.get(url_reservation)
    time.sleep(6)
    # go to the reservation that is in an iframe
    driver.switch_to.frame(0)
    driver.find_element_by_id("StartYear").clear()
    driver.find_element_by_id("StartYear").send_keys(slot[0].year)
    driver.find_element_by_id("StartMonth").clear()
    driver.find_element_by_id("StartMonth").send_keys(slot[0].month)
    driver.find_element_by_id("StartDay").clear()
    driver.find_element_by_id("StartDay").send_keys(slot[0].day)
    driver.find_element_by_id("StartHour").send_keys(slot[0].hour)
    driver.find_element_by_id("StartMinute").send_keys(slot[0].minute)
    driver.find_element_by_id("EndYear").clear()
    driver.find_element_by_id("EndYear").send_keys(slot[1].year)
    driver.find_element_by_id("EndMonth").clear()
    driver.find_element_by_id("EndMonth").send_keys(slot[1].month)
    driver.find_element_by_id("EndDay").clear()
    driver.find_element_by_id("EndDay").send_keys(slot[1].day)
    driver.find_element_by_id("EndHour").send_keys(slot[1].hour)
    driver.find_element_by_id("EndMinute").send_keys(slot[1].minute)

    # Select(driver.find_element_by_id("FeeType")).select_by_value('81')  # longue distance plus besoin
    # Select(driver.find_element_by_name("DestinationID")).select_by_value('1')  # longue quebec
    submit = driver.find_element_by_id("Button_Disponibility").click()
    time.sleep(6)
    # scrap the webpage for the content
    soup = BeautifulSoup(driver.page_source, features="lxml")
    soup = soup.find('table')
    soup_stations = soup.select("a[href*=InfoStation]")
    soup_coords = soup.select("a[href*=BillingRulesAcpt]")
    soup_descs = soup.find_all('td', {'align': "center", "width": "420"})[1:]
    assert len(soup_stations) == len(soup_coords) == len(soup_descs)

    # slots to store everything
    slot = {"id": id_slot, "cars": []}
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
        new_slots[id_slot] = slot

driver.quit()
print("new slots :")
print(new_slots)

flag_new, new_slots = utils.compare_results(new_slots, old_slots)

# save the new json file containing most recent slots locally or in Gdrive
if "gdrive_results" in os.environ.keys():
    gdrive_conn.save_byte_file(new_slots, results_fileid, results_filename)
    print(f"Results saved in {results_filename}")
else:
    json.dump(new_slots, json_file, indent=4, separators=(',', ': '))
    print(f"Results saved in {results_filename}.txt")

# send mail if something new happened
if flag_new:
    pprint.pprint(new_slots)
    # if we pass a list (stringyfied), convert it to list again
    to_email = os.environ["communauto_mailto"]
    if '[' in to_email:
        to_email = ast.literal_eval(to_email)
    utils.send_mail(new_slots, to_email)
    print("Mail sent")
else:
    print("No changes occurs")

print("End on script")
