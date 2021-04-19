from api.extensions import pymongo

db = pymongo.db


class OperationService:

    def find_operations(self, results_filter: dict):
        """
        Retrieves operations based on filters.
        :param dict results_filter: filters from url parameters.
        :return: list with all documents found in Operations collection.
        """
        results = []
        for document in db.operations.find(results_filter):
            document['_id'] = str(document['_id'])
            document['id'] = document['_id']
            del(document['_id'])
            results.append(document)
        return results

    def find_operation(self, operation_id):
        """
        Retrieves an operation from the Operations collection based on its id.
        :param ObjectId operation_id: id of operation to be retrieved.
        :return: dict containing the requested operation or NoneType if not found.
        """
        operation = db.operations.find_one_or_404({"_id": operation_id})
        operation["_id"] = str(operation["_id"])
        return operation

    def create_operation(self, new_operation):
        """
        Adds a new operation to the Operations collection.
        :param dict new_operation: operation to be added.
        :return: string id of the newly added operation.
        """
        result = db.operations.insert_one(new_operation)
        return str(result.inserted_id)

    def delete_operation(self, operation_id):
        """
        Deletes an operation from the Operations collection based on its id.
        :param ObjectId operation_id: id of operation to be deleted.
        :return: count of deleted items.
        """
        result = db.operations.delete_one({"_id": operation_id})
        return result.deleted_count

    def update_operation(self, operation_id, modified_operation):
        """
        Update operation specified by id.
        :param ObjectId operation_id: id of operation that will be modified.
        :param dict modified_operation: operation to be modified.
        :return:
        """
        result = db.operations.update_one({"_id": operation_id}, {"$set": modified_operation})
        return result.matched_count
