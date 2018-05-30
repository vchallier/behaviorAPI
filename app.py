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
	output = {'user_id': new_event['user_id'], 'name' : new_event['name'], 'timestamp' : new_event['timestamp']}
	return jsonify({'result' : output})

@app.route('/user/<user_id>', methods=['GET'])
def view_user(user_id):
	view_events = mongo.db.view_events
	timestamp = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
	views = view_events.find({'timestamp' : { '$gt' : timestamp }, 'user_id' : user_id})
	if views.count() == 0:
		# If no result, return unknown user
		return jsonify({'result' : { 'views' : 'Unknown User' }})
	else:
		# If result, iterate over records and have logic to aggregate
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

@app.route('/user/<user_id>', methods=['DELETE'])
def delete_user(user_id):
	view_events = mongo.db.view_events
	view_events.remove({'user_id' : user_id})
	view_test = view_events.find_one({'user_id' : user_id })
	if not view_test:
		return jsonify({'result' : 'The records were deleted'})
	else:
		return jsonify({'result' : 'Records could not be deleted, oupsie'})

if __name__ == '__main__':
	app.run(debug=True)