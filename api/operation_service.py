from api.extensions import pymongo

db = pymongo.db


class OperationService:

    def find_operations(self, results_filter):
        results = []
        for document in db.operations.find(results_filter):
            document['_id'] = str(document['_id'])
            document['id'] = document['_id']
            del(document['_id'])
            results.append(document)
        return results
