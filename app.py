from flask import Flask
from flask import jsonify
from flask import request
from flask_pymongo import PyMongo
import datetime

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'MadKuduDB'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/MadKuduDB'

mongo = PyMongo(app)

@app.route('/page', methods=['POST'])
def add_event():
	view_events = mongo.db.view_events
	user_id = request.json['user_id']
	name = request.json['name']
	timestamp = request.json['timestamp']
	event_id = view_events.insert({'user_id': user_id, 'name': name, 'timestamp': timestamp})
	new_event = view_events.find_one({'_id': event_id })
	output = {'user_id': new_event['user_id'], 'name' : new_event['name'], 'timestamp' : new_event['timestamp']}
	return jsonify({'result' : output})

@app.route('/user/<user_id>', methods=['GET'])
def view_user(user_id):
	view_events = mongo.db.view_events
	timestamp = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
	views = view_events.find({'timestamp' : { '$gt' : timestamp }, 'user_id' : user_id})
	if not views:
		return jsonify({'result' : { 'views' : 'Unknown User' }})
	else:
		pages = {}
		page_count = 0
		max_page = {'page_name_max' : '', 'view_count_max' : 0}
		for doc in views:
			page_count += 1
			if doc['name'] in pages:
				pages[doc['name']] += 1
			else:
				pages[doc['name']] = 1
			if max_page['view_count_max'] < pages[doc['name']]:
				max_page['page_name_max'] = doc['name']
				max_page['view_count_max'] = pages[doc['name']]
		return jsonify({'result' : { 'user_id' : user_id , 'number_pages_viewed_the_last_7_days' : page_count, 'most_viewed_page_last_7_days' : max_page['page_name_max']}})

if __name__ == '__main__':
	app.run(debug=True)