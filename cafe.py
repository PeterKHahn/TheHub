import requests
import json
import datetime
import sys



def write_to_file():
    """
    Holds support for Ratty, vdub, ivy, jos, blueroom, and Andrews.
    This will query the Brown Dining json to retrieve the menu for that day and
    storing it in the file, data/food_today.json
    """
    id_list = ['1531', '1532', '1533', '1534', '1535', '1536']
    date = get_date().isoformat()

    result = generate_meals(id_list, date)
    f = open('data/food_today.json', 'w+')

    f.write(json.dumps(result))
    return result

def read_from_file():
    """
    Opens the json file at data/food_today.json and returns it as a json object
    that we can deal with internally.
    """
    f = open('data/food_today.json', 'r+')
    return json.load(f)


def generate_meals(id_list, date):
    """
    Queries the cafebonappetit api to return a list of items for a given date
    and a set of dining ids. This is mostly as a helper for write_to_file,
    which has the list of dining ids.
    """
    address = 'http://legacy.cafebonappetit.com/api/2/menus'

    res = {}
    for dining_id in id_list :
        query = {
            'cafe' : dining_id,
            'date' : date
        }
        response = requests.get(address, params=query)
        cafe_json = json.loads(response.text)
        days = cafe_json['days']
        items = cafe_json['items']

        dining_hall_name = days[0]['cafes'][dining_id]['name']
        res[dining_id] = meals(dining_id, days, items)

    return res



def meals(dining_id, days, items):
    """
    Returns an object. Given a dining_id, returns the object that represents
    the menu for that day.
    """
    res_outer = []
    meals = days[0]['cafes'][dining_id]['dayparts'][0]
    for index, meal in enumerate(meals) :
        res_inner = {}


        bar = meal['stations']

        for food in bar :
            bar_name = food['label']
            food_list = food['items']

            food_res = []

            for food_id in food_list :
                food_name = items[food_id]['label']
                food_res.append(food_name)

            res_inner[bar_name] = food_res

        res_temp = {}
        res_temp['label'] = meal['label']  # breakfast, lunch, dinner
        res_temp['starttime'] = meal['starttime']
        res_temp['endtime'] = meal['endtime']
        res_temp['stations'] = res_inner

        res_outer.append(res_temp)

    return res_outer


def get_date():
    """
    Mostly just a convenient wrapper for datetime.date.today()
    """
    return datetime.date.today()
