import requests
import json
from pprint import pprint

api_url = "https://api.opensea.io/api/v1"
query_string = {"offset": "0", "limit": "1000"}
address_camel = "0x3b3bc9b1dd9f3c8716fff083947b8769e2ff9781/4754"
address_axie = "0xf5b0a3efb8e8e4c201e2a935f110eaaf3ffecb8d/220211"


def get_assets(api_url, collection, owner, nb_items):
	"""
	Get all the assets of an owner OR a collection.
	Ex : get_assets(api_url, 'xcopy', "", 1300)
	:param api_url: API URL
	:param collection: name of the collection (the name in the URL) or ""
	:param owner: name of the owner or ""
	:param nb_items: the number of items in the collection, 10000 if checking owner
	:return: a list of the assets in the collection or the owner
	"""
	print("Fetching all assets from : {} {}".format(collection, owner))
	print("The bigger the collection is, the longer it takes (12 000 item ~= 6 min)")
	assets = []
	for nindex in range(0, nb_items, 50):
		try:
			pprint("Loading : " + str(nindex) + "/" + str(nb_items))
			url = api_url + "/assets?owner={}&order_by=token_id&order_direction=desc&offset={}&limit=50&collection={}".format(
				owner, nindex, collection)
			headers = {'Content-Type': 'application/json'}
			response = requests.get(url, headers=headers)
			data_dict = json.loads(response.content)

			for item in data_dict["assets"]:
				assets.append(item)
		except ValueError:
			pprint("Error while retrieving assets : {}".format(ValueError))
			continue
	return assets


def get_asset(api_url, address):
	"""
	Return informations about a specific asset from a given address
	Ex : get_asset(api_url, address_axie)
	:param api_url: Opensea API_URL
	:param address: the adress of the asset
	:return: a dic with all the informations
	"""
	return json.loads(requests.request("GET", api_url + "/asset/" + address, params=query_string).text)


def get_contract(api_url, address):
	"""
	Return the contract from a contract address
	:param api_url: Opensea API_URL
	:param address: Adress of the contract
	:return: a dic with all the informations
	"""
	return json.loads(requests.request("GET", api_url + "/asset_contract/" + address, params=query_string).text)


def get_collections(api_url):
	""" Return the contract from a contract address """
	return json.loads(requests.request("GET", api_url + "/collections/", params=query_string).text)


def get_orders():
	"""
	:return: a list containing orders informations (transaction hash, name, date, contract  name)
	"""
	res = []
	headers = {"Accept": "application/json"}
	url = "https://api.opensea.io/wyvern/v1/orders"
	query = {"bundled": "false", "include_bundled": "false", "include_invalid": "false", "limit": "1000", "offset": "0", "order_by": "created_date", "order_direction": "desc"}
	response = requests.request("GET", url, headers=headers, params=query)

	for order in json.loads(response.text)['orders']:
		pprint(order)
		try:
			res.append({
				'id': order['order_hash'],
				'asset_name': order['asset']['name'],
				'contract_name': order['asset']['asset_contract']['name'],
				'created_date': order['created_date']
			})
		except ValueError:
			continue
	return res


def get_attributes(asset):
	"""
	Extract NFT attributes from an asset
	:param asset: a list of information about the asset (get_asset())
	:return: a dic with the traits of the asset
	"""
	res = []
	for key, val in asset.items():
		if key == 'traits':
			res += val
		if "\'traits\':" in str(val):
			for k in val['traits']:
				v = val['traits'][k]
				res.append({k: v})
	return res


def get_attributes_max(data):
	"""
	Get the max values from an asset attribute (ex: return 100 if attack is 13/100)
	Ex: pprint(get_attributes_max(get_attributes(get_asset(api_url, address_axie))))
	:param data: list with the attributes
	:return: a dic with the max values
	"""
	res = []
	for x in data:
		if "\'max\':" in str(x):
			res.append(x)
	return res


def get_collection_from_name(name):
	"""
	Return the collection based on its name
	Ex : get_collection_from_name('TrumpToys')
	:param name: the name of the collection
	:return: the collection contract
	"""
	collections = get_collections(api_url)
	for c in collections['collections']:
		pprint(c['name'].lower())
		if name.lower() in c['name'].lower():
			return c
	return None


def stats_orders(old_orders, new_orders):
	"""
	Return old stats + new stats with no duplicates. Need to be placed in a loop.
	Ex : while 1:
			orders = stats_orders(orders, get_orders())
	:param old_orders: the orders, we need to get_orders() once before
	:param new_orders: the freshly got orders (by get_orders())
	:return: the stats of all the orders we got
	"""
	for order in new_orders:
		if order['id'] not in str(old_orders):
			old_orders.append(order)
	return old_orders


def get_score_collections(orders):
	"""
	Return the most exchanged collections (with the most exchanged items now)
	Ex : while 1:
		orders = stats_orders(orders, get_orders())
		stats = get_score_collections(orders)
	:param orders: list containing orders information
	:return: A dictionary with the exchanged collections and the amount exchanged for each
	"""
	stats = {}
	for order in orders:
		if order['contract_name'] in stats:
			stats[order['contract_name']] += 1
		else:
			stats[order['contract_name']] = 1
	return stats


def get_rarity(asset, nb_items):
	"""
	Get the rarity of the asset
	:param attributes: the attributes of the asset
	:param nb_items: the number of items in the collection
	:return: a value representing the rarity of the asset (closest to 0 = rarest)
	"""
	try:
		rarity = 0
		name = asset['permalink']
		attributes = get_attributes(asset)
		if '12086788' in name:
			pprint(asset)
			exit()
		if len(attributes) <= 0:
			return {}
		for attribute in attributes:
			rarity += attribute['trait_count'] / nb_items * 100
	except ValueError:
		pprint("ERROR")
		return {}
	return {name: rarity / len(attributes)}


if __name__ == "__main__":
	rarities = []
	for asset in get_assets(api_url, 'crypto-corgis', "", 3100):
		rarity = get_rarity(asset, 3100)
		if rarity == {}:
			pass
		else:
			rarities.append(rarity)
	pprint(rarities)


"""
	orders = get_orders()
	while 1:
		try:
			orders = stats_orders(orders, get_orders())
			stats = get_score_collections(orders)
			#pprint(stats)
			#print(len(stats))
		except ValueError:
			continue
"""
#if "0xa8f8faf719b8d203fc49fe0c84d266918f98e50468df263ab5818d3085dbd9f5" not in [ {'asset_name': 'Picasso BabyWeebit #11',  'contract_name': 'OpenSea Collection',  'created_date': '2021-05-29T00:22:03.132451',  'order_hash': '0xa8f8faf719b8d203fc49fe0c84d266918f98e50468df263ab5818d3085dbd9f5'},
#																				 {'asset_name': 'Bitcoin Sign #2168',  'contract_name': 'OpenSea Collection',  'created_date': '2021-05-29T00:22:02.571002',  'order_hash': '0x837b207c99869c74f8d4a3f49df0e2710bcc9bc84fead6f3c1e36af0e661be8e'}]:
#pprint(get_collection_from_name('trump'))
# pprint(get_asset(api_url, address_axie))
# pprint(get_attributes_max(get_attributes(get_asset(api_url, address_axie))))
