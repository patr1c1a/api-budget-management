import json
from bson import ObjectId
from flask import request, make_response
from flask_restful import Resource
from api.extensions import pymongo
from api.operation_service import OperationService

db = pymongo.db


class OperationCollection(Resource):

    def get(self):
        """
        Retrieve operations: either all operations (unfiltered) or based on filters specified in query parameters.
        :raises Exception: if the request is malformed (parameters can't be parsed).
        :return: tuple with all operations found and response code 200.
        """
        args = request.args

        try:
            results_filter = self.parse_find_parameters(args)
        except Exception as exp:
            return make_response({"message": str(exp)}, 400)
        results = OperationService().find_operations(results_filter)
        return results, 200

    def parse_find_parameters(self, args: dict):
        """
        Adds url parameters to a dictionary.
        :param dict args: parameters from url.
        :return: dict containing all filters specified in url parameters.
        """
        results_filter = {}
        if "type" in args:
            results_filter["type"] = args["type"]
        if "category" in args:
            results_filter["category"] = args["category"]
        if "date" in args:
            results_filter["date"] = args["date"]
        if all(parameter in args for parameter in ("amount", "comparison")):
            if not args["comparison"] in ("higher", "lower"):
                raise Exception("Wrong comparison operator. It should be 'higher' or 'lower'.")
            results_filter["amount"] = args["amount"]
            results_filter["comparison"] = args["comparison"]
        if "partial_description" in args:
            results_filter["partial_description"] = args["partial_description"]
        return results_filter


class OperationResource(Resource):

    def get(self, _id):
        """
        Retrieve single operation matching id.
        :param _id: operation id to be found.
        :return: tuple with operation and response code 200.
        """
        result = OperationService().find_operation(ObjectId(_id))
        return make_response(result, 200)

    def post(self):
        """
        Create new operation
        :return: tuple with id of the new operation created and response code 201.
        """
        args = json.loads(request.data)
        new_operation = {
            "type": args["type"],
            "description": args["description"],
            "amount": args["amount"],
            "date": args["date"],
            "category": args["category"]
        }
        new_op_id = OperationService().create_operation(new_operation)
        return new_op_id, 201

    def delete(self, _id):
        """
        Remove operation specified by id.
        :param _id: operation id to be deleted.
        :return: tuple with message detailing result and status code (200 or 404).
        """
        count = OperationService().delete_operation(ObjectId(_id))
        if count == 0:
            return {"message": "Id not found"}, 404
        return {"message": "Operation deleted successfully"}, 200

    def patch(self, _id):
        """
        Update operation specified by id. Type cannot be changed.
        :param str _id: operation id to be modified.
        :return: tuple with message detailing result and status code (204 or 404).
        """
        args = json.loads(request.data)
        modified_operation = {
            "description": args["description"],
            "amount": args["amount"],
            "date": args["date"],
            "category": args["category"]
        }
        count = OperationService().update_operation(ObjectId(_id), modified_operation)
        if count == 0:
            return {"message": "Id not found"}, 404
        return {"message": "Operation modified successfully"}, 204
