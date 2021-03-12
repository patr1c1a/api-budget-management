import json

from bson import ObjectId
from flask import request, make_response, jsonify
from flask_restful import Resource

from api.extensions import pymongo
from api.operation_service import OperationService

db = pymongo.db



class OperationCollection(Resource):

    def get(self):
        """
        Retrieve operations: either all operations (unfiltered) or based on filters specified in query parameters.
        """

        args = request.args

        # GET operations according to filters

        try:
            results_filter = self.parse_find_parameters(args)
        except Exception as exp:
            return make_response( {"message": str(exp)}, 400)

        '''
        # filter results by partial description
        if "partial_description" in args:
            results = []
            for document in db.operations.find({"description": {
                "$regex": args["partial_description"],
                "$options": "i"}
            }):
                document['_id'] = str(document['_id'])
                results.append(document)
            return results, 200
        '''

        results = OperationService().find_operations(results_filter)
        return results, 200

    def parse_find_parameters(self, args: dict):
        results_filter = {}
        if "type" in args:
            results_filter["type"] = args["type"]
        if "category" in args:
            results_filter["category"] = args["category"]
        if "date" in args:
            results_filter["date"] = args["date"]

        if all(key in args for key in ("amount", "comparison")):
            if not args["comparison"] in ("higher", "lower"):
                raise Exception("Wrong comparison operator. "
                                               "It should be 'higher' or "
                                               "'lower'.")
            comparison_op = "$gte" if args["comparison"] == "higher" else\
                "$lte"
            results_filter["amount"] = {comparison_op: float(args["amount"])}

        if "partial_description" in args:  # FIXME revisar
            results_filter["description"] = {"description": {
                "$regex": args["partial_description"],
                "$options": "i"}
            }
        return results_filter


class OperationResource(Resource):
    def get(self, _id):
        """
        Retrieve single operation matching id.
        """

        cursor = db.operations.find_one_or_404({"_id": ObjectId(_id)})
        cursor["_id"] = str(cursor["_id"])
        return make_response(jsonify(cursor), 200)

    def post(self):
        """
        Create new operation
        """

        args = json.loads(request.data)
        new_operation = {
            "type": args["type"],
            "description": args["description"],
            "amount": args["amount"],
            "date": args["date"],
            "category": args["category"]
        }
        result = db.operations.insert_one(new_operation)
        return str(result.inserted_id), 201

    def delete(self, _id):
        """
        Remove operation specified by id
        """

        result = db.operations.delete_one({"_id": ObjectId(_id)})
        if result.deleted_count == 0:
            return {"message": "Id not found"}
        return {"message": "Operation deleted successfully"}

    def patch(self, _id):
        """
        Update operation specified by id. Type cannot be changed.
        """

        args = json.loads(request.data)
        modified_operation = {
            "description": args["description"],
            "amount": args["amount"],
            "date": args["date"],
            "category": args["category"]
        }
        result = db.operations.update_one({"_id": ObjectId(_id)}, {"$set": modified_operation})
        if result.matched_count == 0:
            return {"message": "Id not found"}
        return {"message": "Operation modified successfully"}