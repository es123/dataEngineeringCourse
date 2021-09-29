# statuses = {
#             'pending' : {'status_for':'all', 'position':1},
#             'cancelled' : {'status_for':'all','position':2},
#             'approved' : {'status_for':'owner', 'position':1},
#             'rejected - owner' : {'status_for':'owner', 'position':2},
#             'accepted' : {'status_for':'dev', 'position':1},
#             'rejected - developer' : {'status_for':'dev', 'position':3},
#             'closed' : {'status_for':'dev', 'position':5},
#             }
#
# for s in sorted(statuses.items(), key=lambda k_v: k_v[1]['position']):
#     print(s)

test_dict = {"0-0": {'cat': 'flight', 'type': 'turquoise', 'org_code': 'CGY', 'org_name': 'Laguindingan', 'unknown': '',
             'org_lat': 8.60815, 'org_lng': 124.4585, 'org_town': 'Northern Mindanao', 'org_country': 'Philippines',
             'org_zone': 'AS', 'dest_code': 'FMA', 'dest_name': 'Formosa', 'dest_lat': -26.21278, 'dest_lng': -58.22806,
             'dist_option_orig_to_transit_orig': 0, 'dist_option_dest_to_transit_dest': 0, 'dist_transit': 18035,
             'dest_town': 'Formosa', 'dest_country': 'Argentina', 'dest_zone': 'SA', 'price_unit': 'ILS',
             'min_price_unit': 2200, 'max_price_unit': 8528.43},
            "1-0": {'cat': 'flight', 'type': 'turquoise', 'org_code': 'CGY', 'org_name': 'Laguindingan', 'unknown': '',
             'org_lat': 8.60815, 'org_lng': 124.4585, 'org_town': 'Northern Mindanao', 'org_country': 'Philippines',
             'org_zone': 'AS', 'dest_code': 'ASU', 'dest_name': 'Asuncion', 'dest_lat': -25.24161,
             'dest_lng': -57.51392, 'dist_option_orig_to_transit_orig': 0, 'dist_option_dest_to_transit_dest': 130,
             'dist_transit': 18152, 'dest_town': 'Departamento Central', 'dest_country': 'Paraguay', 'dest_zone': 'SA',
             'price_unit': 'ILS', 'min_price_unit': 2700, 'max_price_unit': 10634.77},
            "2-0": {'cat': 'flight', 'type': 'turquoise', 'org_code': 'CGY', 'org_name': 'Laguindingan', 'unknown': '',
             'org_lat': 8.60815, 'org_lng': 124.4585, 'org_town': 'Northern Mindanao', 'org_country': 'Philippines',
             'org_zone': 'AS', 'dest_code': 'IGU', 'dest_name': 'Foz do Iguacu', 'dest_lat': -25.59801,
             'dest_lng': -54.48877, 'dist_option_orig_to_transit_orig': 0, 'dist_option_dest_to_transit_dest': 381,
             'dist_transit': 18120, 'dest_town': 'Paraná', 'dest_country': 'Brazil', 'dest_zone': 'SA',
             'price_unit': 'ILS', 'min_price_unit': 2300, 'max_price_unit': 6167.96},
             "1-3": {'cat': 'flight', 'type': 'turquoise', 'org_code': 'DPL', 'org_name': 'Dipolog', 'unknown': '',
             'org_lat': 8.60003, 'org_lng': 123.3437, 'org_town': 'Zamboanga Peninsula', 'org_country': 'Philippines',
             'org_zone': 'AS', 'dest_code': 'ASU', 'dest_name': 'Asuncion', 'dest_lat': -25.24161,
             'dest_lng': -57.51392, 'dist_option_orig_to_transit_orig': 123, 'dist_option_dest_to_transit_dest': 130,
             'dist_transit': 18160, 'dest_town': 'Departamento Central', 'dest_country': 'Paraguay', 'dest_zone': 'SA',
             'price_unit': 'ILS', 'min_price_unit': 2600, 'max_price_unit': 10139.97},
             "1-4": {'cat': 'flight', 'type': 'turquoise', 'org_code': 'OZC', 'org_name': 'Ozamis', 'unknown': '',
             'org_lat': 8.181842, 'org_lng': 123.8438, 'org_town': 'Northern Mindanao', 'org_country': 'Philippines',
             'org_zone': 'AS', 'dest_code': 'ASU', 'dest_name': 'Asuncion', 'dest_lat': -25.24161,
             'dest_lng': -57.51392, 'dist_option_orig_to_transit_orig': 82, 'dist_option_dest_to_transit_dest': 130,
             'dist_transit': 18111, 'dest_town': 'Departamento Central', 'dest_country': 'Paraguay', 'dest_zone': 'SA',
             'price_unit': 'ILS', 'min_price_unit': 2600, 'max_price_unit': 9998.63},
            "1-5": {'cat': 'flight', 'type': 'turquoise', 'org_code': 'PAG', 'org_name': 'Pagadian', 'unknown': '',
             'org_lat': 7.830324, 'org_lng': 123.4618, 'org_town': 'Zamboanga Peninsula', 'org_country': 'Philippines',
             'org_zone': 'AS', 'dest_code': 'ASU', 'dest_name': 'Asuncion', 'dest_lat': -25.24161,
             'dest_lng': -57.51392, 'dist_option_orig_to_transit_orig': 140, 'dist_option_dest_to_transit_dest': 130,
             'dist_transit': 18074, 'dest_town': 'Departamento Central', 'dest_country': 'Paraguay', 'dest_zone': 'SA',
             'price_unit': 'ILS', 'min_price_unit': 2600, 'max_price_unit': 10044.51},
            "1-6": {'cat': 'flight', 'type': 'turquoise', 'org_code': 'BXU', 'org_name': 'Butuan', 'unknown': '',
             'org_lat': 8.9479, 'org_lng': 125.4809, 'org_town': 'Caraga', 'org_country': 'Philippines',
             'org_zone': 'AS', 'dest_code': 'ASU', 'dest_name': 'Asuncion', 'dest_lat': -25.24161,
             'dest_lng': -57.51392, 'dist_option_orig_to_transit_orig': 119, 'dist_option_dest_to_transit_dest': 130,
             'dist_transit': 18174, 'dest_town': 'Departamento Central', 'dest_country': 'Paraguay', 'dest_zone': 'SA',
             'price_unit': 'ILS', 'min_price_unit': 2600, 'max_price_unit': 10024.2}
     }

for s1 in sorted(test_dict.items(), key=lambda k_v: k_v[1]['min_price_unit']):
    print(s1)