import unittest
import os
from ipums_data import save_extract

class TestStringMethods(unittest.TestCase):
    
    def test_download_us1850a(self):
        # verify that the download of the dataset with sample_id us1850a is successful
        self.assertEqual(save_extract("us1850a","data"), 1)
        self.assertTrue(os.path.isfile("data/us1850a/us1850a.csv"))
        self.assertTrue(any(".dat.gz" in s for s in os.listdir("data/us1850a")))
        self.assertTrue(os.path.isfile("data/us1850a/us1850a_description.json"))

if __name__ == '__main__':
    unittest.main()