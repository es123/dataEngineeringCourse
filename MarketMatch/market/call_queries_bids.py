import queries_bids as qry
import json

gen_items = qry.scan_users("CUST#")
ls_items = list(gen_items)

for item in ls_items:
  dict_item = json.loads(item)
  print(dict_item)
  print(dict_item["user_name"])
  print(dict_item["update_date"])
  
print('BIDS ~' *150)  
  
  
gen_items = qry.scan_users("BID#")
ls_items = list(gen_items)
print(ls_items)
for item in ls_items:
  dict_item = json.loads(item)
  print(dict_item)
  print(dict_item["user_name"])
  print(dict_item["update_date"])
  
print('~' *150) 


gen_items = qry.scan_users("OFFER#")
ls_items = list(gen_items)

for item in ls_items:
  dict_item = json.loads(item)
  print(dict_item)
  print(dict_item["user_name"])
  print(dict_item["update_date"])
