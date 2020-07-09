from xml.etree.ElementTree import parse
import math


def get_station(station_id):
    document = parse('ListStations.asp.xml')
    station = document.find(f'Station[@StationID="{station_id}"]')
    station.attrib['name'] = station.text
    return station.attrib


def get_distance(coords_1, coords_2):
    """
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
