from xml.etree.ElementTree import parse
import math
from datetime import datetime
import os

# for email sending
import sendgrid
from sendgrid.helpers.mail import *


def get_station_from_id(station_id):
    """
    :param station_id: the int of the station to look in the communauto list
    :return: the station dict with all attributes
    """
    document = parse('ListStations.asp.xml')
    station = document.find(f'Station[@StationID="{station_id}"]')
    station.attrib['name'] = station.text
    return station.attrib


def get_distance(coords_1, coords_2):
    """
    Get the geospatial straight distance between two points of coordinates
    :param coords_1: should be list or tuple in format Long, Lat
    :param coords_2: should be list or tuple in format Long, Lat
    :return: a float distance in km
    """
    lat1 = float(coords_1[1])
    long1 = float(coords_1[0])
    lat2 = float(coords_2[1])
    long2 = float(coords_2[0])

    # approximate radius of earth in km
    radius = 6371

    dlat = math.radians(lat2-lat1)
    dlon = math.radians(long2-long1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = radius * c

    return round(distance, 2)


def remove_passed_dates(date_array):
    """
    Remove the dates slots that are older than now
    :param date_array: all the date slots in an array [[datebegin, dateend], ...]
    :return: the same format with rows removed
    """
    now = datetime.today()
    return [date_slot for date_slot in date_array if date_slot[0] >= now]


def convert_to_dates(date_array):
    """
    The csv return an array of string of each part of the date. Reformat them well
    :param date_array: the input array with strings [[yearbegin, monthbegin, daybegin, hourbegin, minutebegin, yearend...]
    :return: array of datetimes [[datebegin, dateend], ...]
    """
    new_array = []
    for date in date_array:
        dt_begin = datetime(int(date[0]), int(date[1]), int(date[2]), int(date[3]), int(date[4]))
        dt_end = datetime(int(date[5]), int(date[6]), int(date[7]), int(date[8]), int(date[9]))
        new_array.append([dt_begin, dt_end])
    return new_array


def compare_results(new_slots, old_slots):
    """
    From the current results and the file where the older results are stored, compare to see if there is new cars
    :param new_slots: the dict of the new results
    :param old_slots: the older dict
    :return: flag if something new, and old slots refreshed with new stuff with tag on what is new
    """
    # flag if something new changed
    new_flag = False
    if old_slots is None:
        print("There is no older slots stored, so this will trigger because everything is new")
        new_flag = True
    else:
        # for each datetime slot in new
        for key in new_slots:
            # match the old one
            if key in old_slots.keys():
                # remove "new" flag, used for mailing purpose and saved
                for car in old_slots[key]["cars"]:
                    car.pop("new", None)
                get_new_slots_diff = [item for item in new_slots[key]['cars'] if item not in old_slots[key]['cars']]
                if len(get_new_slots_diff) > 0:
                    best_new_distance = min([slot['distance'] for slot in get_new_slots_diff])
                    worst_old_distance = max([slot['distance'] for slot in old_slots[key]['cars']])
                    if best_new_distance < worst_old_distance:
                        print(f"New best car found for slot {key}")
                        print(f"{get_new_slots_diff}")
                        for idx, item in enumerate(new_slots[key]["cars"]):
                            if item in get_new_slots_diff:
                                new_slots[key]["cars"][idx]['new'] = True
                        new_flag = True
            else:
                print(f"New datetime slot never searched : {key}")
                new_slots[key]['new'] = True
                new_flag = True

    return new_flag, new_slots


def send_mail(slots, to_email):
    """
    from a specific dict of slots, send an email to the addresses
    :param slots: dict containing all available slots with tags for new ones
    :param to_email: Address or list of address
    :return: status code of email sent
    """

    subject = "New changes in Communauto"

    mail_txt = "<html><head></head><body><h1>These are the currently available cars in Communauto for your researches " \
               ":</h1><br><br><br> "
    for date_slot in slots.keys():
        bold_entire_slot = False
        # add a bold tag for a brand new slot
        if 'new' in slots[date_slot].keys():
            bold_entire_slot = True
            mail_txt += f"<b>"
        mail_txt += f"<a href='{slots[date_slot]['url']}'>For the timeslot {date_slot} :</a><br>"
        for car in slots[date_slot]['cars']:
            # add a bold tag for a brand new car available
            if 'new' in car.keys():
                mail_txt += f"&nbsp;&nbsp;&nbsp; <b>{car['Name']} at {car['distance']}km : {car['description']}</b><br>"
            else:
                mail_txt += f"&nbsp;&nbsp;&nbsp; {car['Name']} at {car['distance']}km : {car['description']}<br>"
        if bold_entire_slot:
            mail_txt += f"</b>"
        mail_txt += "<br>"

    mail_txt += "</body></html>"

    # send mail through SendGrid
    sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email(os.environ.get('communauto_from'))
    content = Content("text/html", mail_txt)
    mail = Mail(from_email=from_email, subject=subject, to_emails=to_email, html_content=content)
    response = sg.client.mail.send.post(request_body=mail.get())
    return response.status_code
