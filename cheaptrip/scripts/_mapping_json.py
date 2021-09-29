

# https://jsoneditoronline.org/#left=local.jojilu&right=local.pimahe
# https://jsoneditoronline.org/#left=local.jojilu&right=local.pimahe
# https://www.rome2rio.com/map/Badrinath/Gokarna#r/Taxi-to-Dehra-Dun-fly-to-Goa-train

'''
todo:

** add car and ferry transits
** need to separete between transit and cars or handled option[8][trans_id][6][4] / [5] if fields are not exists
1. count entry level
2. use param for function:gen_cities_combination_filtered
3. replace boolean from 1 to True
4. seperate extract_transits_from_list-mapping_trips from get_hierarchy_array_info function
5. save search params in logs
6. we may save related search files each time in different directory
7. handle encoding issue in trip Train to Tokyo Narita, fly to Mumbai insdie # logging.info(f"trans_id_dest_code:{trans_id} - {option[8][trans_id][3][5]}")
   check also walk
   currently disable the following:
    # logging.info(f"trans_id_org_code:{trans_id} - {option[8][trans_id][6][4]}")
    # logging.info(f"trans_id_org_zone:{trans_id} - {option[8][trans_id][6][5]}")
    # logging.info(f"dest_id_dest_code:{trans_id} - {option[8][trans_id][7][4]}")
    # logging.info(f"dest_id_dest_zone:{trans_id} - {option[8][trans_id][7][5]}")
8. change looging transit when debug == 1 to array instead fields (save room)


'''

import boto3
import json
from dotenv import load_dotenv
import os
from load_cities import gen_cities_combination
from generate_json import generate_list
import logging
from datetime import *
import time
import geopy.distance

load_dotenv()

# load env. variables
log_dir_path = os.getenv("LOG_PATH")
base_url = os.getenv('BASE_URL')
base_html_path = os.getenv('BASE_HTML_PATH')
base_json_path = os.getenv('BASE_JSON_PATH')
cities_path = os.getenv('CITIES_PATH')
base_json_output_path = os.getenv('BASE_JSON_OUTPUT_PATH')

start_time = time.time()
debug = 0
limit_cities = 2  # total cities to search
limit_combination = 1
filter_diff_lat = 0
filter_diff_lng = 0

trip_dict_map = {}
trip_dict_val = {}
dict_path = {}
trip_dict = {}
trans_dict = {}


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

        # extract destination info
        if option[2][0] == "node":
            dict_option_value["dest"] = option[2][1]
            dict_option_value["dest_lat"] = option[2][2]
            dict_option_value["dest_lng"] = option[2][3]
            dict_option_value["dest_code"] = option[2][4]
            dict_option_value["dest_zone"] = option[2][5]
            dict_option_value["dest_unknown"] = option[2][6]
            dict_option_value["transits"] = " "

        # loop over all transits related to the specific trip option
        dict_transits = {}
        for trans_id, transit in enumerate(option[8]):
            if debug == 1:
                logging.info(f'~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~option{option_id} tranist:#{trans_id} ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

            trans_dict_value = {"trans_id": [], "trans_info": []}

            # loop over specific transit
            dict_trans_value = {}
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

                            # loop over transit price in $ and calculate min and max prices
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

                elif option[8][trans_id][trans_info_id] == "hotel":
                    list_transits_found.append(option[8][trans_id][trans_info_id])

                    dict_trans_value[f"cat"] = option[8][trans_id][0]
                    dict_trans_value[f"org_cat"] = option[8][trans_id][1][0]
                    dict_trans_value[f"org_name"] = option[8][trans_id][1][1]
                    dict_trans_value[f"org_lat"] = option[8][trans_id][1][2]
                    dict_trans_value[f"org_lng"] = option[8][trans_id][1][3]
                    dict_trans_value[f"org_code"] = option[8][trans_id][1][4]
                    dict_trans_value[f"org_zone"] = option[8][trans_id][1][5]

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
    return dict_option


def extract_transits_from_list(trip, check_list, tab, map_path='[2]->[1]', nested=1, path='', rec_limit=8):
    # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    # print(f'trip:{trip}')
    # print(f'check_list:{check_list[:20]}')
    # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')


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
                trip_options_transits_dict = mapping_trips(trip, element, 99)
                logging.info(f'exrtracting transists info for trip: {trip}')

                for trip in trip_options_transits_dict.items():
                    raw_data = json.dumps(trip)
                    encoded_data = bytes(raw_data, 'utf-8')
                    print(raw_data)
                    # print('bbb', trip[0])
                    json_output_file_path = base_json_output_path + '\\' + trip[0] + '.json'
                    with open(json_output_file_path, 'w') as f:
                        f.write(raw_data)

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


def generate_json(cities_path, base_url, base_html_path, base_json_path, limit=10, filtered=1, debug=0):

    # get cities combinations
    # generates only list for cities which are far from each other
    # tp_cities = gen_cities_combination_filtered(cities_path, debug=debug, limit=limit)
    tp_cities = gen_cities_combination(cities_path, debug=debug, limit_cities=limit_cities,
                                                limit_combination=limit_combination, filter_diff_lat=filter_diff_lat, filter_diff_lng=filter_diff_lng)

    print(tp_cities)

    # extract origin cities out of given cities list
    org_list = [city[0][0] for i, city in enumerate(tp_cities)]
    # extract destination cities out of given cities list
    dest_list = [city[1][0] for city in tp_cities]

    ls_cities = list(zip(org_list, dest_list))
    print(ls_cities)

    if debug == 1:
        # logging.info given tuple
        logging.info(ls_cities)
        # logging.info n element from origin cities
        logging.info(org_list[:3])
        # logging.info n element from dest cities
        logging.info(dest_list[:3])

    # loop over cities combination list and parse list of trip data
    for origin, dest in ls_cities:
        # print(type(origin))
        # print(origin)

        trip = str(origin) + '_' + str(dest)
        trip_url = trip.replace('_', '/')

        url = base_url + trip_url
        html_file_path = base_html_path + "/" + trip + ".txt"
        json_file_path = base_json_path + "/" + trip + ".txt"

        if not os.path.isfile(json_file_path):
            # generate and parse list per given org-dest
            generate_list(url, html_file_path, json_file_path, debug)
        elif debug == 1:
            logging.info(f'file {json_file_path} is already exists')

    return ls_cities

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

        json_file_path = base_json_path + r"\\" + trip + ".txt"

        # read list of arrays extracted from html raw data
        try:
            with open(json_file_path, 'rb') as f:
                trip_data = json.load(f)
        except:
            logging.info(f'failed reading {json_file_path}')

        logging.info(f'parsing hierarchy of trip from {origin} to {dest}')

        # map generated list of arrays
        extract_transits_from_list(trip, trip_data, 1)

def main():

    # generate python log + timestamp
    log_file_path = str(log_dir_path) + r'\cheaptrip_python_log_' \
                    + datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + '.txt'

    # set up logging to file
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s.%(msecs)03d %(name)-12s %(module)s %(levelname)-8s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        filename=log_file_path,
                        filemode='w'
                        )

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
    tp_cities = generate_json(cities_path, base_url, base_html_path, base_json_path, 5, 1, debug)

    # extract trip hierarchy analysis info fer json
    extract_trip_transits(tp_cities, base_json_path)

if __name__ == "__main__":
    # calling main function
    main()

    # set logger
    diff_sec = round(time.time() - start_time)
    diff_time = time.strftime("%H:%M:%S", time.gmtime(diff_sec))
    logging.info('\n')
    logging.info(f'--- total python duration: {diff_time} ---')

