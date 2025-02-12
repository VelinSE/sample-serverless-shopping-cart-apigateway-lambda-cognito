import json
import os 

dir_path = os.path.dirname(os.path.realpath(__file__))

def get_product_ids():
    with open(f"{dir_path}/product_list.json", "r") as product_list:
        product_list = json.load(product_list)

    return [prod["productId"] for prod in product_list]