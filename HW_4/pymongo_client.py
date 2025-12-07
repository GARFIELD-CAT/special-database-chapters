import random
import uuid
from pprint import pprint
from typing import Dict, Any, Optional

from bson import ObjectId
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError


class MongoDBClient:
    def __init__(
            self,
            db_name: str,
            collection_name: str,
            connection_str: str = 'mongodb://root:password@localhost:27017',
    ):
        self.client = MongoClient(connection_str)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def close_connection(self):
        self.client.close()

    def create_document(self, doc_data: Dict[str, Any]) -> Optional[str]:
        try:
            result = self.collection.insert_one(doc_data)
            doc_id = str(result.inserted_id)

            return doc_id
        except DuplicateKeyError:
            print('Error: record already exists')
            return None

    def find_document_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        try:
            result = self.collection.find_one({'_id': ObjectId(doc_id)})

            if result:
                result['id'] = str(result['_id'])

                return result
            else:
                print(f'Document with {doc_id=} not fount')
                return None
        except Exception as e:
            print(f'Error {e.__class__.__name__} getting record')
            return None

    def update_document(self, doc_id: str, filed: str,
                        new_content: str) -> bool:
        try:
            result = self.collection.update_one(
                {'_id': ObjectId(doc_id)},
                {'$set': {filed: new_content}}
            )

            if result.modified_count > 0:
                print('Updated row')
                return True
            else:
                print(f'Document with {doc_id=} not fount')
                return False
        except Exception as e:
            print(f'Error {e.__class__.__name__} updating record')
            return False

    def delete_document_by_id(self, doc_id: str) -> bool:
        try:
            result = self.collection.delete_one({'_id': ObjectId(doc_id)})

            if result.deleted_count > 0:
                print('Deleted row')
                return True
            else:
                print(f'Document with {doc_id=} not fount')
                return False
        except Exception as e:
            print(f'Error {e.__class__.__name__} deleting record')
            return False


class MongoReviews:
    def __init__(
            self,
            db_name: str,
            collection_name: str,
            connection_str: str = 'mongodb://root:password@localhost:27017',
            mongo_client: MongoClient = None,
    ):
        if mongo_client:
            self.client = mongo_client
        else:
            self.client = MongoDBClient(
                connection_str=connection_str,
                db_name=db_name,
                collection_name=collection_name,
            )

    def create_index(self):
        self.client.collection.create_index('user_id'),
        self.client.collection.create_index('order_data.product_id')

    def add_review(
            self,
            user_id: int,
            order_id: str,
            product_id: int,
            rating: int,
            content: str
    ):
        review_dict = {
            'user_id': user_id,
            'order_data': {
                'order_id': order_id,
                'product_id': product_id,
            },
            'rating': rating,
            'content': content
        }

        self.client.create_document(review_dict)

    def user_reviews_report(self):
        # отчет по отзывам пользователей
        pipeline = [
            {
                '$group': {
                    '_id': '$user_id',
                    'total_reviews': {'$sum': 1},
                    'average_rating': {'$avg': '$rating'}
                }
            },
            {
                '$sort': {'total_reviews': -1}
            }
        ]

        analysis = self.client.collection.aggregate(pipeline=pipeline)
        analysis_list = list(analysis)
        pprint(analysis_list)

    def get_product_report(self, product_id: int):
        # отчет по продуктам
        pipeline = [
            {
                "$match": {'order_data.product_id': product_id}
            },
            {
                '$group': {
                    '_id': '$order_data.product_id',
                    'total_reviews': {'$sum': 1},
                    'average_rating': {'$avg': '$rating'},
                    'min_rating': {'$min': '$rating'},
                    'max_rating': {'$max': '$rating'}
                }
            }
        ]

        analysis = self.client.collection.aggregate(pipeline=pipeline)
        analysis_list = list(analysis)
        pprint(analysis_list)

    def get_user_reviews(self, user_id: int, max_reviews: int = 10):
        list_reviews = []

        for review in self.client.collection.find(
                {'user_id': user_id}
        ).limit(max_reviews):
            list_reviews.append(review)

        print(f'Received {len(list_reviews)} reviews for user {user_id}')

        return list_reviews


def generate_test_data():
    with MongoClient('mongodb://root:password@localhost:27017') as client:
        db = client['customer']
        collection = db['reviews']

        for i in range(1000):
            id = str(uuid.uuid4())
            review_dict = {
                '_id': id,
                'user_id': random.randint(1, 10),
                'order_data': {
                    'order_id': str(uuid.uuid4()),
                    'product_id': random.randint(1, 10),
                },
                'rating': random.randint(1, 10),
                'content': 'some content'
            }
            collection.update_one(
                {'_id': id},
                {'$set': review_dict},
                upsert=True,
            )


if __name__ == '__main__':
    review_mongo = MongoReviews(
        db_name="customer",
        collection_name='reviews',
        connection_str='mongodb://root:password@localhost:27017',
    )

    print(review_mongo.client.collection.count_documents({}))
    # generate_test_data()
    # review_mongo.create_index()
    review_mongo.user_reviews_report()
    review_mongo.get_product_report(9)
    pprint(review_mongo.get_user_reviews(3, 5))
