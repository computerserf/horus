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
import subprocess
import requests
import time

from decimal import Decimal
from main.data_store import DataStore
from main.interfaces import Notifier, Engine
from main.agent import Agent


class TestDummyServerSingleItem(unittest.TestCase):
    """Tests the fetching of a single item price from the mock server"""

    class FakeDataStore(DataStore):
        def __init__(self, task_id):
            self.task_id = task_id
            self.item_history = [Decimal(500)]
            pass

        def get_config_value(self, key):
            if key == "server_url":
                return "localhost"
            elif key == "max_history_length":
                return 10
            else:
                raise KeyError("Configuration value '" + key + "' not mocked")

        def get_item_ids(self):
            return ["item1.html"]

        def get_item_history(self, id):
            if id == "item1.html":
                return self.item_history
            else:
                raise KeyError("Item '" + id + "' not mocked")

        def set_item_history(self, key, history):
            print("setting price key = '" + key + "', value = '" + str(history) + "'")
            if key == "item1.html":
                self.item_history = history
            else:
                raise KeyError("Item '" + key + "' not mocked")

    class TestNotifier(Notifier):

        def __init__(self):
            self.messages = []
            self.alerted = False

        def add(self, item_id, latest_data_point):
            self.messages.append("item id '" + item_id + "' price dropped to " + str(latest_data_point))

        def alert(self):
            print("Test store has the following notifications:")
            for m in self.messages:
                print("=> " + m)
            self.alerted = True

    class TestEngine(Engine):

        def __init__(self):
            pass

        def fetch(self, server_url, item_id):
            r = requests.get("http://" + server_url + ":8000" + "/" + item_id)
            return Decimal(r.text)

        def compare(self, latest_data_point, history):
            return latest_data_point < history[-1]

        def wait(self):
            time.sleep(5)

    def setUp(self):
        # start the mock http server
        command = ["python", "./test/dummy_server.py"]
        self.process = subprocess.Popen(command)

        # wait till dummy server stabilizes
        time.sleep(5)

    def tearDown(self):
        # shutdown the HTTP server
        self.process.terminate()
        self.process.wait()

    def test_execution(self):
        """This end to end test starts a mock server, requests an item from it
        and checks if a mock data store is updated properly."""
        # create mock data store
        data_store = self.FakeDataStore("TEST_E2E1")

        notifier = self.TestNotifier()

        # create and execute the agent
        agent = Agent(data_store)
        agent.execute(notifier, self.TestEngine())

        # verify that the new cost is correct
        history = data_store.get_item_history("item1.html")
        self.assertTrue(len(history) == 2)
        self.assertAlmostEqual(history[1], 370.00)

        # assert that notifier works properly
        self.assertEqual(len(notifier.messages), 1)
        self.assertTrue(notifier.alerted)


if __name__ == "__main__":
    unittest.main()
