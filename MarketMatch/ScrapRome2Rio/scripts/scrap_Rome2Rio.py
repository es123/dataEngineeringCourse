"""
need to add support for specific trip
added in batches for huge ammount of data
"""

# import modules
import boto3
import datetime as dt
import json
from dotenv import load_dotenv
import os
from load_cities import gen_cities_combination
from extract_json import extract_json_from_html
import logging
from datetime import *
import time
from send_event_kinesis import send_event
import geopy.distance

start_time = time.time()


# settings
debug = 0
limit_cities = 5  # limit cities to search
limit_combination = 9999 # limit cities combination
limit_trip_options = 9999 # limit trip options 
limit_generate_json = 9999 # limit total no. og json files to be generated
filter_diff_lat = 0 # filter abdolute of coordinate latitude diff
filter_diff_lng = 0 # filter abdolute of coordinates length diff

# declare objects for later use
trip_dict_map = {}
trip_dict_val = {}
dict_path = {}
dict_hierarchy_analysis = {}
trip_dict = {}
trans_dict = {}

table = 'r2rTripsGenerator'
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(table) 
cur_date = dt.datetime.utcnow().isoformat()
stream = 'stream_r2rTrips_generator_kinesis_dynamodb'
pk = 'trip'    
sk = 'entity_id'


def common_entries(*dcts):
    '''
    zip 2 dictionaries
    :return tuple
    :*dcts multiple dictionaries
    '''
    if not dcts:
        return
    for i in sorted(set(dcts[0]).intersection(*dcts[1:])):
        yield (i,) + tuple(d[i] for d in dcts)

def append_dicts(dict_name, key, value):
    try:
        dict_name[key] = value
    except:
        logging.error(f'failed to add {key} json')

def mapping_trips(trip, trip_list, limit_trip_options):
    '''
    append given mapping values to 2 dictionaries
    according to mapping conditions
    '''

    # dictionaries for verify that all transists types added
    list_transits_other = []
    list_transits_found = []
    list_transits_all = []
    dict_option = {trip+'#0': {}}

    # loop over Trip options transits
    for option_id, option in enumerate(trip_list):
        dict_option_value = {}

        # limit total transits per trip option
        if option_id > limit_trip_options - 1:
            break

        dict_option_value["option_id"] = option_id
        dict_option_value["option"] = option[3]
        if debug == 1:
            logging.info(f'~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            logging.info(f'~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~trip option{option_id}:# {dict_option_value["option"]}~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            logging.info(f'~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            logging.info('\n')

        # extract origin info
        if option[1][0] == "node":
            dict_option_value["org"] = option[1][1]
            dict_option_value["org_lat"] = option[1][2]
            dict_option_value["org_lng"] = option[1][3]
            dict_option_value["org_code"] = option[1][4]
            dict_option_value["org_zone"] = option[1][5]
            dict_option_value["org_unknown"] = option[1][6]
            origin_coord = (option[1][2], option[1][3])

        # extract destination info
        if option[2][0] == "node":
            dict_option_value["dest"] = option[2][1]
            dict_option_value["dest_lat"] = option[2][2]
            dict_option_value["dest_lng"] = option[2][3]
            dict_option_value["dest_code"] = option[2][4]
            dict_option_value["dest_zone"] = option[2][5]
            dict_option_value["dest_unknown"] = option[2][6]
            dict_option_value["transits"] = " "
            dest_coord = (option[2][2], option[2][3])
            
            dict_option_value["dist_trip"] = round(geopy.distance.geodesic(origin_coord, dest_coord).km)

        # loop over all transits related to the specific trip option
        dict_transits = {}
        dict_flights = {}
        for trans_id, transit in enumerate(option[8]):
            if debug == 1:
                logging.info(f'~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~option{option_id} tranist:#{trans_id} ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

            trans_dict_value = {"trans_id": [], "trans_info": []}

            # loop over specific transit
            dict_trans_value = {}
            dict_flights_value = {}
            for trans_info_id, trans_info in enumerate(option[8][trans_id]):
                # in case entry ins not an array add it into list_transits_all dictionary
                if not isinstance(option[8][trans_id][trans_info_id], list):
                    list_transits_all.append(option[8][trans_id][trans_info_id])
                # loop over transit types and extract related data
                if option[8][trans_id][trans_info_id] in ["transit", "car"]:
                    list_transits_found.append(option[8][trans_id][trans_info_id])

                    dict_trans_value[f"cat"] = option[8][trans_id][0]
                    dict_trans_value[f"name"] = option[8][trans_id][1]
                    dict_trans_value[f"type"] = option[8][trans_id][2]
                    dict_trans_value[f"duration"] = option[8][trans_id][3]
                    # dict_trans_value[f"max_price_local"] = option[8][trans_id][4]
                    # dict_trans_value[f"min_price_local"] = option[8][trans_id][5]

                    dict_trans_value[f"org_cat"] = option[8][trans_id][6][0]
                    dict_trans_value[f"org_name"] = option[8][trans_id][6][1]
                    dict_trans_value[f"org_lat"] = option[8][trans_id][6][2]
                    dict_trans_value[f"org_lng"] = option[8][trans_id][6][3]
                    dict_trans_value[f"dest_cat"] = option[8][trans_id][7][0]
                    dict_trans_value[f"dest_name"] = option[8][trans_id][7][1]
                    dict_trans_value[f"dest_lat"] = option[8][trans_id][7][2]
                    dict_trans_value[f"dest_lng"] = option[8][trans_id][7][3]
                    dict_trans_value["dist_option_orig_to_transit_orig"] = round(geopy.distance.\
                        geodesic((dict_option_value["org_lat"], dict_option_value["org_lng"]), (option[8][trans_id][6][2], option[8][trans_id][6][3])).km)
                    dict_trans_value["dist_option_dest_to_transit_dest"] = round(geopy.distance.\
                        geodesic((dict_option_value["dest_lat"], dict_option_value["dest_lng"]), (option[8][trans_id][7][2], option[8][trans_id][7][3])).km)
                    dict_trans_value["dist_transit"] = round(geopy.distance. \
                        geodesic((option[8][trans_id][6][2], option[8][trans_id][6][3]),
                                 (option[8][trans_id][7][2], option[8][trans_id][7][3])).km)
                    # loop over transit price in $ and calculate min and max prices
                    for ls_price_id, ls_price in enumerate(option[8][trans_id][13]):
                        if ls_price_id == 0:
                            price_unit = ls_price[1]
                            min_price_unit = ls_price[0]
                            max_price_unit = ls_price[2]
                        else:
                            if ls_price[0] < min_price_unit:
                                min_price_unit = ls_price[0]
                            if ls_price[2] > max_price_unit:
                                max_price_unit = ls_price[2]
                    dict_trans_value[f"price_unit"] = price_unit
                    dict_trans_value[f"min_price_unit"] = min_price_unit
                    dict_trans_value[f"max_price_unit"] = max_price_unit

                    append_dicts(dict_transits, "" + str(trans_id) + "", dict_trans_value)
                elif option[8][trans_id][trans_info_id] == "walk":
                    list_transits_found.append(option[8][trans_id][trans_info_id])

                    dict_trans_value[f"cat"] = option[8][trans_id][0]
                    dict_trans_value[f"name"] = option[8][trans_id][1]
                    dict_trans_value[f"type"] = option[8][trans_id][2]
                    dict_trans_value[f"duration"] = option[8][trans_id][3]  # need to verify attribute is correct
                    # dict_trans_value[f"max_price_local"] = option[8][trans_id][4]  # need to verify attribute is correct
                    # dict_trans_value[f"min_price_local"] = option[8][trans_id][5]  # need to verify attribute is correct
                    dict_trans_value[f"org_cat"] = option[8][trans_id][6][0]
                    dict_trans_value[f"org_name"] = option[8][trans_id][6][1]
                    dict_trans_value[f"org_lat"] = option[8][trans_id][6][2]
                    dict_trans_value[f"org_lng"] = option[8][trans_id][6][3]
                    dict_trans_value[f"dest_cat"] = option[8][trans_id][7][0]
                    dict_trans_value[f"dest_name"] = option[8][trans_id][7][1]
                    dict_trans_value[f"dest_lat"] = option[8][trans_id][7][2]
                    dict_trans_value[f"dest_lng"] = option[8][trans_id][7][3]
                    dict_trans_value["dist_option_orig_to_transit_orig"] = round(geopy.distance.\
                        geodesic((dict_option_value["org_lat"], dict_option_value["org_lng"]), (option[8][trans_id][6][2], option[8][trans_id][6][3])).km)
                    dict_trans_value["dist_option_dest_to_transit_dest"] = round(geopy.distance.\
                        geodesic((dict_option_value["dest_lat"], dict_option_value["dest_lng"]), (option[8][trans_id][7][2], option[8][trans_id][7][3])).km)
                    dict_trans_value["dist_transit"] = round(geopy.distance.\
                        geodesic((option[8][trans_id][6][2], option[8][trans_id][6][3]),
                                 (option[8][trans_id][7][2], option[8][trans_id][7][3])).km)

                    append_dicts(dict_transits, "" + str(trans_id) + "", dict_trans_value)

                elif option[8][trans_id][trans_info_id] == "flight":
                    for fl_id, fl_info in enumerate(option[8][trans_id]):
                        if fl_id in (2, 3):
                            list_transits_found.append(option[8][trans_id][trans_info_id])

                            dict_trans_value[f"cat"] = option[8][trans_id][0]
                            dict_trans_value[f"type"] = option[8][trans_id][1]
                            dict_trans_value[f"org_code"] = option[8][trans_id][2][0]
                            dict_trans_value[f"org_name"] = option[8][trans_id][2][1]
                            dict_trans_value[f"unknown"] = option[8][trans_id][2][2]
                            dict_trans_value[f"org_lat"] = option[8][trans_id][2][3]
                            dict_trans_value[f"org_lng"] = option[8][trans_id][2][4]
                            dict_trans_value[f"org_town"] = option[8][trans_id][2][5]
                            dict_trans_value[f"org_country"] = option[8][trans_id][2][6]
                            dict_trans_value[f"org_zone"] = option[8][trans_id][2][7]

                            dict_trans_value[f"dest_code"] = option[8][trans_id][3][0]
                            dict_trans_value[f"dest_name"] = option[8][trans_id][3][1]
                            dict_trans_value[f"unknown"] = option[8][trans_id][3][2]
                            dict_trans_value[f"dest_lat"] = option[8][trans_id][3][3]
                            dict_trans_value[f"dest_lng"] = option[8][trans_id][3][4]
                            dict_trans_value["dist_option_orig_to_transit_orig"] = round(geopy.distance. \
                            geodesic((dict_option_value["org_lat"], dict_option_value["org_lng"]),
                                         (option[8][trans_id][2][3], option[8][trans_id][2][4])).km)
                            dict_trans_value["dist_option_dest_to_transit_dest"] = round(geopy.distance. \
                            geodesic((dict_option_value["dest_lat"], dict_option_value["dest_lng"]),
                                         (option[8][trans_id][3][3], option[8][trans_id][3][4])).km)
                            dict_trans_value["dist_transit"] = round(geopy.distance. \
                                geodesic((option[8][trans_id][2][3], option[8][trans_id][2][4]), (option[8][trans_id][3][3], option[8][trans_id][3][4])).km)
                            dict_trans_value[f"dest_town"] = option[8][trans_id][3][5]
                            dict_trans_value[f"dest_country"] = option[8][trans_id][3][6]
                            dict_trans_value[f"dest_zone"] = option[8][trans_id][3][7]

                            # loop over transit price in and calculate min and max prices
                            for ls_price_id, ls_price in enumerate(option[8][trans_id][11]):
                                if ls_price_id == 0:
                                    price_unit = ls_price[1]
                                    min_price_unit = ls_price[0]
                                    max_price_unit = ls_price[2]
                                else:
                                    if ls_price[0] < min_price_unit:
                                        min_price_unit = ls_price[0]
                                    if ls_price[2] > max_price_unit:
                                        max_price_unit = ls_price[2]
                            dict_trans_value[f"price_unit"] = price_unit
                            dict_trans_value[f"min_price_unit"] = min_price_unit
                            dict_trans_value[f"max_price_unit"] = max_price_unit

                            append_dicts(dict_transits, "" + str(trans_id) + "", dict_trans_value)
                            
                            dict_flights_value["departure"]=option[8][trans_id][2][1]
                            dict_flights_value["arrivel"]=option[8][trans_id][3][1]
                            dict_flights_value["min_price_unit"]=min_price_unit
                            dict_flights_value["price_unit"]=price_unit
                            
                            append_dicts(dict_flights, "" + str(trans_id) + "", dict_flights_value)

                elif option[8][trans_id][trans_info_id] == "hotel":
                    list_transits_found.append(option[8][trans_id][trans_info_id])

                    dict_trans_value[f"cat"] = option[8][trans_id][0]
                    dict_trans_value[f"org_cat"] = option[8][trans_id][1][0]
                    dict_trans_value[f"org_name"] = option[8][trans_id][1][1]
                    dict_trans_value[f"org_lat"] = option[8][trans_id][1][2]
                    dict_trans_value[f"org_lng"] = option[8][trans_id][1][3]
                    # if len(option[8][trans_id][1][4]):
                    #     dict_trans_value[f"org_code"] = option[8][trans_id][1][4]
                    # if len(option[8][trans_id][1][5]):
                    #     dict_trans_value[f"org_zone"] = option[8][trans_id][1][5]

                    append_dicts(dict_transits, "" + str(trans_id) + "", dict_trans_value)

                elif option[8][trans_id][trans_info_id] == "car":
                    list_transits_found.append(option[8][trans_id][trans_info_id])

                    dict_trans_value[f"name"] = option[8][trans_id][1]
                    dict_trans_value[f"type"] = option[8][trans_id][2]
                    dict_trans_value[f"duration"] = option[8][trans_id][3]
                    # dict_trans_value[f"max_price_local"] = option[8][trans_id][4]
                    # dict_trans_value[f"min_price_local"] = option[8][trans_id][5]

                    dict_trans_value[f"org"] = option[1][1]
                    dict_trans_value[f"org_lat"] = option[1][2]
                    dict_trans_value[f"org_lng"] = option[1][3]
                    dict_trans_value[f"org_code"] = option[1][4]
                    dict_trans_value[f"org_zone"] = option[1][5]
                    dict_trans_value[f"org_unknown"] = option[1][6]

                    dict_trans_value[f"dest"] = option[2][1]
                    dict_trans_value[f"dest_lat"] = option[2][2]
                    dict_trans_value[f"dest_lng"] = option[3][3]
                    dict_trans_value["dist_option_orig_to_transit_orig"] = round(geopy.distance.\
                        geodesic((dict_option_value["org_lat"], dict_option_value["org_lng"]), (option[1][2], option[1][3])).km)
                    dict_trans_value["dist_option_dest_to_transit_dest"] = round(geopy.distance.\
                        geodesic((dict_option_value["dest_lat"], dict_option_value["dest_lng"]), (option[2][2], option[3][3])).km)
                    dict_trans_value["dist_orig_transit_dest_transit"] = round(geopy.distance.\
                        geodesic((option[1][2], option[1][3]), (option[2][2], option[3][3])).km)

                    dict_trans_value[f"dest_code"] = option[4][4]
                    dict_trans_value[f"dest_zone"] = option[5][5]
                    dict_trans_value[f"dest_unknown"] = option[2][6]

                    append_dicts(dict_transits, "" + str(trans_id) + "", dict_trans_value)

            # append option information to dict_option dictionary
            append_dicts(dict_option, "" + trip+'#'+str(option_id) + "", dict_option_value)
            dict_option["" + trip+'#'+str(option_id) + ""]['transits'] = dict_transits
            # dict_option["" + trip+'#'+str(option_id) + ""]['flights'] = dict_flights
    return dict_option




def extract_transits_from_list(trip, check_list, tab, map_path='[2]->[1]', nested=1, path='', rec_limit=8):
    '''
    recrusive function to extract list of lists
    '''
    n = 0
    n += 1

    # logging.info header of new array
    if n == 1:
        if debug == 1:
            logging.info('~' * 50 + ' ' + f'array#{nested} : {len(check_list)} elements' + ' ' + '~' * 50)
    try:
        # logging.info array elements
        counter_total_extraxted = 0
        for i, element in enumerate(check_list):
            if nested == 1:
                full_path = f'{path}{[i]}'
            else:
                full_path = f'{path}->{[i]}'

            # logging.info full path + element value
            if debug == 1:
                if isinstance(element, list):
                    logging.info('~!' * tab + full_path + ':' + 'see below array info')
                else:
                    logging.info('~!' * tab + ' ' + full_path + ':' + str(element))

            # append all full path + element
            append_dicts(dict_path, full_path, element)

            if full_path == map_path:
                if debug == 1:
                    logging.info(f"loop inside extract_transits_from_list {str(i)}")
                # map trip options transits options
                trip_options_transits_dict = mapping_trips(trip, element, limit_trip_options)
                logging.info(f'exrtracting transists info for trip: {trip}')
                for transists in trip_options_transits_dict.items():
                    counter_total_extraxted += 1
                    if debug == 1:
                        logging.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~transists~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                        logging.info(transists)                    
         
                    trip_org = transists[0]
                    logging.info(f'extracing and loading data for trip {trip_org}')
                    origin = trip_org[:str.find(trip_org, '#')][:trip.find('_')]
                    dest = trip[trip.find('_')+1:]
                    entity_id = 'DEST#'+dest+'#OPTION'+trip_org[str.find(trip_org, '#')+1:]
                    info = transists[1]

                    raw_data = json.dumps(info)
                    encoded_data = bytes(raw_data, 'utf-8')
                    
                    item = {
                            pk: origin,
                            sk: entity_id,
                            'timestamp': cur_date,
                            'info_transits': info
                            }
                            
                    send_event(table, stream, pk, sk, item, debug=debug)
                
                logging.info(f'total of {counter_total_extraxted} items were extracted and loaded for trip {origin}-{dest}')    

   
            # call the function again in case list type been found
            if isinstance(element, list):
                extract_transits_from_list(trip, element, tab + 2, map_path, nested+1, full_path)
                if debug == 1:
                    logging.info('\n')
            # terminate recrusive according to given limit
            if nested > rec_limit:
                break
    except:
        raise("error occured")


def generate_trip_json(cities_path, base_url, base_html_path, base_json_path, limit_generate_json = 100, ebug=0):    
    """
    generate cities combination for all involved cities
    """  
    tp_cities = gen_cities_combination(cities_path, debug=debug, limit_cities=limit_cities,
                                       limit_combination=limit_combination, filter_diff_lat=filter_diff_lat, filter_diff_lng=filter_diff_lng)
                                           

    # extract origin cities out of given cities list
    org_list = [city[0][0] for i, city in enumerate(tp_cities)]
    # extract destination cities out of given cities list
    dest_list = [city[1][0] for city in tp_cities]

    # zipping origin and destination lists
    ls_cities = list(zip(org_list, dest_list))
    if debug == 1:
        # logging.info given tuple
        logging.info(ls_cities)
        # logging.info n element from origin cities
        logging.info(org_list[:3])
        # logging.info n element from dest cities
        logging.info(dest_list[:3])

    # loop over cities combination list and parse list of trip data
    for origin, dest in ls_cities:
        trip = str(origin) + '_' + str(dest)
        trip_url = trip.replace('_', '/')

        url = base_url + trip_url
        html_file_path = base_html_path + "/" + trip + ".txt"
        json_file_path = base_json_path + "/" + trip + ".txt"

        if not os.path.isfile(json_file_path):
            # generate and parse list per given org-dest
            extract_json_from_html(trip, url, html_file_path, json_file_path, debug)
            # generate_list(trip, url, html_file_path, json_file_path, s3bucket, debug)
        elif debug == 1:
            logging.info(f'file {json_file_path} is already exists')

    return ls_cities


def get_hierarchy_array_info(trip, dict_path, max_depth_str = '[1]->[1]->[1]->[1]->[1]->[1]'):
    """
    loop over given cities (origin, dest)
    read related json file
    parse json using extract_transits_from_list function

    :param cities:
    :param base_json_path:
    :return:
    """
   
    logging.info(f'parsing hierarchy of trip {trip}')

    # logging.info mapped array
    if debug == 1:
        logging.info(list(common_entries(trip_dict_map, trip_dict_val)))

    total_entries = 0
    total_arrays = 0
    arrays_element = 0
    total_arrays_elements = 0
    empty = 0
    total_empties = 0
    max_depth = len(max_depth_str)

    # loop over trip path dictionary to gather statiststics such (for given max nested depth)
    # total_entries - total fields other than arrays
    # total_arrays - total array fields
    # arrays_element - total elemets in arrayas fields
    # total_empties - total empties fields
    dict_sum_value = {"total_entries": []}
    
    for key in dict_path.keys():
        if len(key) <= max_depth:
            if isinstance(dict_path[key], list):
                total_arrays += 1
                arrays_element = len(dict_path[key])
                total_arrays_elements += arrays_element
                if debug == 1:
                    logging.info(key +
                          f' running total arrays: {total_arrays} - contains {arrays_element} - total array elements by current line: {total_arrays_elements}')
            else:
                total_entries += 1
                if len(str(dict_path[key])) == 0:
                    empty += 1
                    total_empties += empty
                if debug == 1:
                    logging.info(key +
                          f' running total entries: {total_entries} - current empties {empty} total empties {total_empties}')

    dict_sum_value["total_entries"] = total_entries
    dict_sum_value["total_arrays"] = total_arrays
    dict_sum_value["arrays_element"] = arrays_element
    dict_sum_value["total_empties"] = total_empties

    append_dicts(dict_hierarchy_analysis, trip, dict_sum_value)

    return dict_hierarchy_analysis


def extract_trip_transits(cities, base_json_path):
    """
    loop over given cities (origin, dest)
    read related json file
    parse json using extract_transits_from_list function

    :param cities:
    :param base_json_path:
    :return:
    """
    
    for origin, dest in cities:
        trip = origin + '_' + dest
        trip_url = trip.replace('_', '/')

        json_file_path = base_json_path + r"/" + trip + ".txt"

        # read list of arrays extracted from html raw data
        try:
            with open(json_file_path, 'rb') as f:
                trip_data = json.load(f)
        except:
            logging.info(f'failed reading {json_file_path}')

        logging.info(f'parsing hierarchy of trip from {origin} to {dest}')

        # map generated list of arrays
        extract_transits_from_list(trip, trip_data, 1)

        dict_hierarchy_analysis1 = get_hierarchy_array_info(trip, dict_path)

    return dict_hierarchy_analysis1


def main():

    load_dotenv()
    
    # load env. variables
    log_dir_path = os.getenv("LOG_DIR_PATH")
    base_url = os.getenv('BASE_URL')
    base_html_path = os.getenv('BASE_HTML_PATH')
    base_json_path = os.getenv('BASE_JSON_PATH')
    cities_path = os.getenv('CITIES_PATH')
    base_json_output_path = os.getenv('BASE_JSON_OUTPUT_PATH')
    

    # generate python log + timestamp
    log_file_path = str(log_dir_path) + r'/r2rTrips_python_log_' \
                    + datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + '.txt'

    # set up logging to file
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s.%(msecs)03d %(name)-12s %(module)s %(levelname)-8s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        filename=log_file_path,
                        filemode='w'
                        )

                    
    logging.info(f'logging into {log_file_path}')

    # define a console Handler which writes messages to the sys.stderr
    console = logging.StreamHandler()
    # set console handler level
    console.setLevel(logging.INFO)
    # set a format which is simpler for console use
    formatter = logging.Formatter('%(asctime)s %(name)-12s: %(module)s %(levelname)-8s %(message)s')
    # define miliseconds format
    formatter.default_msec_format = '%s.%03d'
    # tell the handler to use this format
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)

    logging.info(f'logging to : {log_file_path}')
    logging.info('\n')

    # load cities
    # generate cities combination
    # generate json
    tp_cities = generate_trip_json(cities_path, base_url, base_html_path, base_json_path, limit_generate_json, debug)
    
    # extract all trip options transits
    # extract_trip_transits(tp_cities, base_json_path)

    # extract trip hierarchy analysis info fer json
    dict_hierarchy_analysis1 = extract_trip_transits(tp_cities, base_json_path)

    for trip, analysis in dict_hierarchy_analysis1.items():
        
        origin = trip[:trip.find('_')]
        dest = trip[trip.find('_')+1:]
        entity_id = 'STATS#'+dest
        info = analysis
        
        raw_data = json.dumps(info)
        encoded_data = bytes(raw_data, 'utf-8')
        
        item = {
                pk: origin,
                sk: entity_id,
                'timestamp': cur_date,
                'total_entries': analysis['total_entries'],
                'total_arrays': analysis['total_arrays'],
                'arrays_element': analysis['arrays_element'],
                'total_empties': analysis['total_empties'],
                'info': info
                }

        send_event(table, stream, pk, sk, item, debug=debug)


if __name__ == "__main__":
    # calling main function
    main()

    diff_sec = round(time.time() - start_time)
    diff_time = time.strftime("%H:%M:%S", time.gmtime(diff_sec))
    logging.info('\n')
    logging.info(f'--- total python duration: {diff_time} ---')
    
    


