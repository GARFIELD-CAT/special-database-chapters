from datetime import timedelta
import datetime
import random

from pymongo import MongoClient

mongo_client = MongoClient('mongodb://localhost:27017')
db = mongo_client['test']
collection = db['users']

new_collection = db['dayagunov_collection']
data = []

for i in range(100):
    birthdate = datetime.datetime.now() - timedelta(random.randint(1, 10000))

    row = {
        'name': f'Имя {i}',
        'birthdate': birthdate,
        'age': random.randint(1, 100)
    }
    data.append(row)


new_collection.insert_many(data)


print('------------------REPORT---------------------')
print(f'count_documents: {new_collection.count_documents({})}')

print('----------------Row example------------------')
row = new_collection.find_one({'name': 'Имя 45'}, {"_id": 0})
print(row)

# Clear collection
db.drop_collection('dayagunov_collection')
# print(db.list_collection_names())












