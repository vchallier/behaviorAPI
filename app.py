from flask import Flask
from flask import jsonify
from flask import request
from flask_pymongo import PyMongo

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

if __name__ == '__main__':
    app.run(debug=True)