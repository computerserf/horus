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

from main.data_store import DataStore

class TestDataStore(unittest.TestCase):
    """Tests that the DataStore class works as expected"""

    def setUp(self):
        self.data_store = DataStore("DS_TEST")
        self.data_store.items = {"2172":[1, 2], "409":[3, 4]}
        self.data_store.keys = {"key1":"yada", "key2":"blabla", "key3":"do"}

    def tearDown(self):
        del self.data_store

    def test_starts_out_unmodified(self):
        self.assertFalse(self.data_store.modified)

    def test_gets_correct_item_ids(self):
        item_ids = self.data_store.get_item_ids()

        self.assertEqual(len(item_ids), 2)
        self.assertTrue("2172" in item_ids)
        self.assertTrue("409" in item_ids)

    def test_gets_correct_config_values(self):
        self.assertEqual(self.data_store.get_config_value("key1"), "yada")
        self.assertEqual(self.data_store.get_config_value("key2"), "blabla")
        self.assertEqual(self.data_store.get_config_value("key3"), "do")

    def test_exception_on_wrong_key(self):
        with self.assertRaises(KeyError):
            self.data_store.get_config_value("keyblade")

    def test_get_correct_item_history(self):
        history = self.data_store.get_item_history("409")

        self.assertEqual(len(history), 2)
        self.assertTrue(3 in history)
        self.assertTrue(4 in history)

    def test_throw_error_on_getting_wrong_history(self):
        with self.assertRaises(KeyError):
            self.data_store.get_item_history("007")

    def test_set_correct_item_history(self):
        history = [99, 201]

        self.data_store.set_item_history("409", history)

        self.assertEqual(self.data_store.get_item_history("409"), [99, 201])
        self.assertTrue(self.data_store.modified)

    def test_throw_error_on_setting_wrong_history(self):
        history = [23, 7]

        with self.assertRaises(KeyError):
            self.data_store.set_item_history("547", history)

        self.assertFalse(self.data_store.modified)


if __name__ == "__main__":
    unittest.main()