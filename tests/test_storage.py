import unittest
import pandas as pd
from src.data.storage import DataStorage
from datetime import datetime

class TestDataStorage(unittest.TestCase):
    def setUp(self):
        self.storage = DataStorage()
        self.test_data = {
            'timestamp': datetime.now(), 
            'cpu_percent': 50.0, 
            'memory_percent': 60.0, 
            'disk_usage': 70.0, 
            'network_bytes_sent': 1000, 
            'network_bytes_recv': 2000 
        }

    def test_save_and_load_data(self):
        self.storage.save_to_db(self.test_data)

        loaded_data = self.storage.load_data(limit=1)

        self.assertFalse(loaded_data.empty)
        self.assertEqual(len(loaded_data), 1)
        self.assertIn('id', loaded_data.columns)

        self.assertEqual(loaded_data.iloc[0]['cpu_percent'], self.test_data['cpu_percent'])

if __name__ == '__main__':
    unittest.main()