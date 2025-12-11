import unittest
from unittest.mock import patch, MagicMock
import sys
import io
import requests
from disaster_info import APIClient, Earthquake, Tsunami

# mock data for test
MOCK_EARTHQUAKE_DATA = {
    'id': 'earthquake0123456789abcd',
    'earthquake': {
        'hypocenter': {
            'name': '東京湾',
            'magnitude': 5.5
        },
        'time': '2025/12/01 11:00:00',
        'domesticTsunami': 'No tsunami triggered.'
    }
}

MOCK_TSUNAMI_DATA = {
    'id': 'tsunami0123456789abcdefg',
    'issue': {
        'time': '2025/12/02 12:00:00'
    },
    'areas': [
        {'name': '東京都北部'},
        {'name': '東京都南部'},
    ]
}


class TestDisasterInfo(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.TEST_URL = "http://test.mock.api.url"

        pass


    @patch('requests.get')
    def test_fetch_data_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [MOCK_EARTHQUAKE_DATA]
        mock_get.return_value = mock_response

        client = APIClient(self.TEST_URL)
        data = client.fetch_data(code=551, limit=1)

        self.assertEqual(data, [MOCK_EARTHQUAKE_DATA])
        mock_get.assert_called_once()


    @patch('requests.get')
    @patch('sys.exit')
    @patch('logging.error')
    def test_fetch_data_network_error(self, mock_log_error, mock_sys_exit, mock_get):
        mock_get.side_effect = requests.exceptions.ConnectionError

        client = APIClient(self.TEST_URL)
        client.fetch_data(code=551, limit=1)

        mock_sys_exit.assert_called_once_with(1)
        mock_log_error.assert_called_once()


    @patch('requests.get')
    @patch('sys.exit')
    @patch('logging.error')
    def test_fetch_data_http_error(self, mock_log_error, mock_sys_exit, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        mock_get.return_value = mock_response

        client = APIClient(self.TEST_URL)
        client.fetch_data(code=551, limit=1)

        mock_sys_exit.assert_called_once_with(1)
        mock_log_error.assert_called_once()


    @patch('requests.get')
    @patch('sys.exit')
    @patch('logging.error')
    def test_fetch_data_value_error(self, mock_log_error, mock_sys_exit, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "Not Json Text"
        mock_response.json.side_effect = ValueError("Not json text")
        mock_get.return_value = mock_response

        client = APIClient(self.TEST_URL)
        data = client.fetch_data(code=551, limit=1)

        mock_sys_exit.assert_called_once_with(1)
        mock_log_error.assert_called_once()


    def test_earthquake_parsing_robustness(self):
        earthquake = Earthquake({})

        self.assertEqual(earthquake.id, 'Unknown ID')
        self.assertEqual(earthquake.time, 'Unknown Time')
        self.assertEqual(earthquake.name, 'Unknown Location')
        self.assertEqual(earthquake.magnitude, -1.0)
        self.assertEqual(earthquake.tsunami_status, 'None')


    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('disaster_info.Translator')
    def test_earthquake_display(self, mock_translator, mock_stdout):
        mock_translation_result = MagicMock()
        mock_translation_result.text = "Tokyo Bay" 
        mock_translator.return_value.translate.return_value = mock_translation_result

        earthquake = Earthquake(MOCK_EARTHQUAKE_DATA)
        earthquake.display()

        expected_output = (
            "Earthquake ID: earthquake0123456789abcd\n"
            "Hypocenter: Tokyo Bay\n"
            "Magnitude: 5.5\n"
            "Time: 2025/12/01 11:00:00\n"
            "Tsunami: No tsunami triggered.\n"
        )
        self.assertEqual(mock_stdout.getvalue(), expected_output)


    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('disaster_info.Translator')
    @patch('logging.warning')
    def test_earthquake_display_with_original_text(self, mock_log_warning, mock_translator, mock_stdout):
        mock_translator.return_value.translate.return_value = Exception("Error")

        earthquake = Earthquake(MOCK_EARTHQUAKE_DATA)
        earthquake.display()

        expected_output = (
            "Earthquake ID: earthquake0123456789abcd\n"
            "Hypocenter: 東京湾\n"
            "Magnitude: 5.5\n"
            "Time: 2025/12/01 11:00:00\n"
            "Tsunami: No tsunami triggered.\n"
        )
        self.assertEqual(mock_stdout.getvalue(), expected_output)
        mock_log_warning.assert_called_once()


    def test_tsunami_parsing_robustness(self):
        tsunami = Tsunami({})

        self.assertEqual(tsunami.id, 'Unknown ID')
        self.assertEqual(tsunami.time, 'Unknown Time')
        self.assertEqual(tsunami.areas, [])


    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('disaster_info.Translator')
    def test_tsunami_display(self, mock_translator, mock_stdout):
        mock_translation_result1 = MagicMock()
        mock_translation_result1.text = "Northern Tokyo"
        mock_translation_result2 = MagicMock()
        mock_translation_result2.text = "Southern Tokyo"
        mock_translator.return_value.translate.side_effect = [
            mock_translation_result1,
            mock_translation_result2,
        ]

        tsunami = Tsunami(MOCK_TSUNAMI_DATA)
        tsunami.display()

        expected_output = (
            "Tsunami ID: tsunami0123456789abcdefg\n"
            "Time: 2025/12/02 12:00:00\n"
            "Areas: Northern Tokyo, Southern Tokyo\n"
        )
        self.assertEqual(mock_stdout.getvalue(), expected_output)


if __name__ == '__main__':
    unittest.main()
