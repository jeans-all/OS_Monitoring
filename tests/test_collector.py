import unittest
from src.data.collector import SystemDataCollector

class TestSystemDataCollector(unittest.TestCase):
    def test_collect_system_data(self):
        data = SystemDataCollector.collect_system_data()
        self.assertIsNotNone(data)
        self.assertIn('cpu_percent', data)
        self.assertIn('memory_percent', data)
        self.assertIn('disk_usage', data)

if __name__ == '__main__':
    unittest.main()