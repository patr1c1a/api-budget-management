from flask_restful import Api


def register_routes(api: Api):
    """
    El orden de los imports es importante, por eso estos están aqui dentro, caso
    contrario tendre imports circulares
    :param api:
    :return:
    """
    from api.controllers import OperationCollection, OperationResource

    api.add_resource(OperationCollection, "/operations", endpoint="operations")
    api.add_resource(OperationResource, "/operation",
                     "/operation/<string:_id>", endpoint="operation")
