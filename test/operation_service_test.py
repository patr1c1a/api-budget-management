from unittest import mock

from api.operation_service import OperationService

mock_find_data = [{'_id': '6036e42857a3def8cbb7be49', 'type': 'income',
                   'description': 'monthly salary', 'amount': 83000,
                   'date': '31/01/2021', 'category': 'salary'},
                  {'_id': '6036e52c57a3def8cbb7be4b', 'type': 'income',
                   'description': 'freelancing', 'amount': 6000,
                   'date': '07/02/2021', 'category': 'salary'},
                  {'_id': '603f82b1a091ae4722e8ffcd', 'type': 'income',
                   'description': 'sell GOOGL', 'amount': 15000,
                   'date': '02/03/2021', 'category': 'stocks market'}]

expected = [
    {'type': 'income', 'description': 'monthly salary', 'amount': 83000,
     'date': '31/01/2021', 'category': 'salary',
     'id': '6036e42857a3def8cbb7be49'},
    {'type': 'income', 'description': 'freelancing', 'amount': 6000,
     'date': '07/02/2021', 'category': 'salary',
     'id': '6036e52c57a3def8cbb7be4b'},
    {'type': 'income', 'description': 'sell GOOGL', 'amount': 15000,
     'date': '02/03/2021', 'category': 'stocks market',
     'id': '603f82b1a091ae4722e8ffcd'}]


class TestOperationService:

    @mock.patch("api.operation_service.db")
    def test_find_all(self, mock_db):
        mock_db.operations.find.return_value = mock_find_data
        result = OperationService().find_operations({})
        assert expected == result
