import requests
import json
import pydot




def main():
    #base_url = https://api.yelp.com/v3/businesses/search
    print('')
    print('')
    '''
    Client ID
    R7wo-Wg0yj0VWC11sNuuiw
    API Key
    57OAm-5UsIYJZXj0wqIcQPPORFgwyuP5Zt7uUdPXRVzRwHancNZ8z-AaSXRtHuaDzDk_6A79UvdMooMvexSLP0PZvi6DYpnOKgnpG57y4c-peTjiGsqQnFKN8Xc0ZHYx
    '''
    # Define the API Key, define the Endpoint and define the Header
    API_KEY = '57OAm-5UsIYJZXj0wqIcQPPORFgwyuP5Zt7uUdPXRVzRwHancNZ8z-AaSXRtHuaDzDk_6A79UvdMooMvexSLP0PZvi6DYpnOKgnpG57y4c-peTjiGsqQnFKN8Xc0ZHYx'
    ENDPOINT = 'https://api.yelp.com/v3/businesses/search'
    HEADERS = {'Authorization': 'bearer %s' % API_KEY}
    #cuisine #
    term_list = []
    radius_list = []
    price_list = []
    rating_list = []
    review_count_list = []
    while True:
        term = input('Please enter the search term:')
        radius = input('Please enter the radius in meters:')
        price = int(input('Please enter the desirable price, 1 for %, 2 for $$, three for $$$ and 4 for $$$$:'))
        rating = input('Please enter the rating:')
        review_count= input('Please enter the mininum review count:')

        if term not in term_list or radius not in radius_list or price not in price_list or rating not in rating_list or review_count not in review_count_list:
            term_list.append(term)
            radius_list.append(radius)
            price_list.append(price)
            rating_list.append(rating)
            review_count_list.append(review_count)
            json_cache=f'data_term={term}_radius={radius}_price={price}_rating={rating}_and_review_count={review_count}.json'
            data = fetch_data(update=True, term=term, radius=radius,price=price, rating=rating, review_count=review_count, json_cache=json_cache, url=ENDPOINT, headers=HEADERS, api_key=API_KEY)
        else:
            json_cache = f'data_term={term}_radius={radius}_price={price}_rating={rating}_and_review_count={review_count}.json'
            data = fetch_data(update=False, term=term, radius=radius,price=price, rating=rating, review_count=review_count, json_cache=json_cache, url=ENDPOINT, headers=HEADERS, api_key=API_KEY)
        print(data)
        print(type(data))
        print(len(data))
        print(f'term_list = {term_list}')
        print(f'radius_list = {radius_list}')
        print(f'price_list = {price_list}')
        print(f'rating_list = {rating_list}')
        print(f'review_count_list = {review_count_list}')
        ans = input('Do you want to search again?')
        if ans == 'yes':
            continue
        else:
            break
    the_tree_dic = construct_the_tree(f'data_term={term}_radius={radius}_price={price}_rating={rating}_and_review_count={review_count}.json', term)
    graph = pydot.Dot(graph_type='graph')
    visit(the_tree_dic)
    graph.write_png('eg1.png')


def fetch_data(*, update=False, term, radius, price, rating, review_count, json_cache, url, headers, api_key):
    HEADERS = {'Authorization': 'bearer %s' % api_key}
    if update:
        json_data = None
    else:
        try:
            with open(json_cache, 'r') as file:
                json_data = json.load(file)
                print('Fetched data from local cache!')
        except(FileNotFoundError, json.JSONDecodeError) as e:
            print(f'No local cache found...({e})')
            json_data  = None

    if not json_data:
        print('Fetching new json data...(Creating local cache)')
        json_data = list()
        #json_data = requests.get(url=url, params=parames, headers=headers).json()
        #the_list = []
        for i in range(20):
            Params = {'location' : 'NYC',
                    'term' : term,
                    'limit' : 50,
                    'radius' : radius,
                    'lacole' : 'en_US',
                    'offset' : 0+50*i,
                    'open_now' : True,
                    'price' : price,
                    'rating' : rating,
                    'review_count' : review_count
                                        }
        # Make a request to the yelp API
            response = requests.get(url=url, params=Params, headers=HEADERS)
        # Convert a json string to a dictionary
            json_data.extend(response.json()['businesses'])
        with open(json_cache, 'w') as file:
            json.dump(json_data, file)

    return json_data
# rating, categories, name, transanction
def construct_the_tree(json_file, term):
    transaction_method1 = 'pickup'
    transaction_method2 = 'delivery'
    transaction_method3 = 'restaurant_reservation'
    transaction_method1_name = []
    transaction_method2_name = []
    transaction_method3_name = []
    transaction_method1_dic = {}
    transaction_method2_dic = {}
    transaction_method3_dic = {}
    dic = {term:{'pickup':1, 'delivery':2, 'restaurant_reservation':3}}
    f = open(f'{json_file}')  # open JSON file
    data = json.load(f)       # returns jSON object as a dictionary
    for i in range(5):
        if transaction_method1 in data[i]['transactions']:
            transaction_method1_name.append(data[i]['name'])
        if transaction_method2 in data[i]['transactions']:
            transaction_method2_name.append(data[i]['name'])
        if transaction_method3 in data[i]['transactions']:
            transaction_method3_name.append(data[i]['name'])
        for k in range(len(transaction_method1_name)):
            if transaction_method1_name[k] == data[i]['name']:
                transaction_method1_dic[transaction_method1_name[k]] = data[i]['display_phone']
        for l in range(len(transaction_method2_name)):
            if transaction_method2_name[l] == data[i]['name']:
                transaction_method2_dic[transaction_method2_name[l]] = data[i]['display_phone']
        for m in range(len(transaction_method3_name)):
            if transaction_method3_name[m] == data[i]['name']:
                transaction_method3_dic[transaction_method3_name[m]] = data[i]['display_phone']
    dic[term]['pickup'] = transaction_method1_dic
    dic[term]['delivery'] = transaction_method2_dic
    dic[term]['restaurant_reservation'] = transaction_method3_dic
    f.close()
    return dic

def draw(parent_name, child_name):
    edge = pydot.Edge(parent_name, child_name)
    graph.add_edge(edge)

def visit(node, parent=None):
    for k,v in node.items():
        if isinstance(v, dict):
            # We start with the root node whose parent is None
            # we don't want to graph the None node
            if parent:
                draw(parent, k)
            visit(v, k)
        else:
            draw(parent, k)
            # drawing the label using a distinct name
            draw(k, k+'_'+v)

'''
menu = {'dinner':
            {'chicken':'good',
             'beef':'average',
             'vegetarian':{
                   'tofu':'good',
                   'salad':{
                            'caeser':'bad'}
                   },
             'pork':'bad'}
        }

def draw(parent_name, child_name):
    edge = pydot.Edge(parent_name, child_name)
    graph.add_edge(edge)

def visit(node, parent=None):
    for k,v in node.items():
        if isinstance(v, dict):
            # We start with the root node whose parent is None
            # we don't want to graph the None node
            if parent:
                draw(parent, k)
            visit(v, k)
        else:
            draw(parent, k)
            # drawing the label using a distinct name
            draw(k, k+'_'+v)

graph = pydot.Dot(graph_type='graph')
visit(menu)
graph.write_png('eg1.png')
'''

'''
PARAMETERS = {'term' : 'good food',
              'location' : 'San Diego',    # location is required is either latitude or longitude is not provided
              'latitude' : 32.715736,       # latitude is required if location is not provided
              'longitude' : -117.161087,    # longitude is required if location is not provided
              'radius' : 10000,
              'categories' : 'bar,french',
              'locale' : 'en_US',
              'limit' : 50,
              'offset' : 150,
              'sort_by' : 'best_match',
              'price' : 'l',
              'open_now' : True,
              'open_at' : 1546215674,
              'attributes' : 'hot_and_new'
              }
'''


if __name__ == '__main__':
    main()
