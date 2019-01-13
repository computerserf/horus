#     Copyright 2018-2019 Haresh Bhagchandani
#
#     This file is part of Horus.
#
#     Horus is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     Horus is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with Horus.  If not, see <https://www.gnu.org/licenses/>.

import unittest
import filecmp
import os

from horus import load_config, save_config

class TestHorus(unittest.TestCase):
    """Tests the runtime Horus methods that the user calls"""

    def test_load_works_as_expected(self):
        deserialize = lambda task, data_str: int(data_str)

        stores = load_config("./test/input_config.json", deserialize)

        self.assertEqual(len(stores), 2)

        self.assertEqual(stores[0].task_id, "TEST1")
        keys = {"server_url":"localhost","max_history_length":2}
        self.assertEqual(stores[0].keys, keys)
        items = {"item1.html": [500], "item2.html": [560]}
        self.assertEqual(stores[0].items, items)

        self.assertEqual(stores[1].task_id, "TEST2")
        # keys = {"server_url": "localhost", "max_history_length": 2}
        self.assertEqual(stores[1].keys, keys)
        items = {"item1.html": [120], "item2.html": [780]}
        self.assertEqual(stores[1].items, items)

    def test_save_works_as_expected(self):
        deserialize = lambda task, data_str: int(data_str)
        serialize = lambda task, data_pt: str(data_pt)

        stores = load_config("./test/input_config.json", deserialize)
        save_config(stores, "./test/output_config.json", serialize)
        new_stores = load_config("./test/output_config.json", deserialize)

        self.assertTrue(filecmp.cmp("./test/input_config.json", "./test/input_config.json"))
        os.remove("./test/output_config.json")

        self.assertEqual(stores, new_stores)


if __name__ == "__main__":
    unittest.main()