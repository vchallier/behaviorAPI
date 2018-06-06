from flask import Flask
from flask import jsonify
from flask import request
from flask_pymongo import PyMongo
import datetime
from dateutil.parser import parse
import operator

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'MadKuduDB'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/MadKuduDB'

mongo = PyMongo(app)


@app.route('/page', methods=['POST'])
def add_event():
	view_events = mongo.db.view_events
	user_id = request.json['user_id']
	name = request.json['name']
	timestamp = parse(request.json['timestamp'])
	event_id = view_events.insert({'user_id': user_id, 'name': name, 'timestamp': timestamp})
	return jsonify({'result' : {'user_id': user_id, 'name': name, 'timestamp': timestamp}})


@app.route('/user/<user_id>', methods=['GET'])
def view_user(user_id):
	view_events = mongo.db.view_events

	# Initiate variables
	# views_count will track the number of views for each page
	# active_days will keep the days from the timestamps
	timestamp7 = (datetime.datetime.now() - datetime.timedelta(days=7))
	views_count = {}
	active_days = set()

	for view in view_events.find({'timestamp' : { '$gt' : timestamp7 }, 'user_id' : user_id}):
		active_days.add(view['timestamp'].day)
		if view['name'] in views_count:
			views_count[view['name']] += 1
		else:
			views_count[view['name']] = 1

	# Return result : unknown if there is no view
	if views_count == {}:
		return jsonify({'result' : 'Unknown or inactive user' })
	else:
		return jsonify({'result' : { 
			'user_id' : user_id , 
			'number_pages_viewed_the_last_7_days' : sum(views_count.values()), 
			'most_viewed_page_last_7_days' : max(views_count.items(), key=operator.itemgetter(1))[0], 
			'number_of_days_active_last_7_days' : len((active_days))}
			})


@app.route('/user/<user_id>', methods=['DELETE'])
def delete_user(user_id):
	view_events = mongo.db.view_events
	view_events.remove({'user_id' : user_id})
	view_test = view_events.find_one({'user_id' : user_id })
	if not view_test:
		return jsonify({'result' : 'The records were deleted'})
	else:
		return jsonify({'result' : 'Records could not be deleted, oupsie'})


@app.route('/refresh', methods=['DELETE'])
def delete_old_records():
	view_events = mongo.db.view_events
	timestamp = (datetime.datetime.now() - datetime.timedelta(days=7))
	view_events.remove({'timestamp' : { '$lt' : timestamp }})
	return jsonify({'result' : 'Old records were deleted'})


if __name__ == '__main__':
	app.run(debug=True)