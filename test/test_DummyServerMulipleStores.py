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
import os
import time

from horus import load_config, save_config
from decimal import Decimal
from main.agent import Agent
from main.interfaces import Notifier, Engine


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

class TestEngine1(Engine):

    def __init__(self):
        pass

    def fetch(self, server_url, item_id):
        r = requests.get("http://" + server_url + ":9000" + "/" + item_id)
        return Decimal(r.text)

    def compare(self, latest_data_point, history):
        return latest_data_point < history[-1]

    def wait(self):
        time.sleep(5)

class TestEngine2(Engine):

    def __init__(self):
        pass

    def fetch(self, server_url, item_id):
        r = requests.get("http://" + server_url + ":9001" + "/" + item_id)
        return Decimal(r.text)

    def compare(self, latest_data_point, history):
        return latest_data_point < history[-1]

    def wait(self):
        time.sleep(5)

def find_notifier(task_id):
    if task_id == "TEST1" or "TEST2":
        return TestNotifier()
    else:
        raise RuntimeError("Task name not recognized")

def find_engine(task_id):
    if task_id == "TEST1":
        return TestEngine1()
    elif task_id == "TEST2":
        return TestEngine2()
    else:
        raise RuntimeError("Task name not recognized")

class TestDummyServerMultipleStores(unittest.TestCase):
    """Tests the fetching of multiple items from multiple data stores from the server."""

    def setUp(self):
        # start the first mock http server
        command = ["python", "./test/dummy_server.py", "9000"]
        self.process1 = subprocess.Popen(command)

        # start the second mock http server
        command = ["python", "./test/dummy_server.py", "9001"]
        self.process2 = subprocess.Popen(command)

        # wait till dummy servers stabilize
        time.sleep(5)

    def tearDown(self):
        # shutdown the HTTP servers
        self.process1.terminate()
        self.process1.wait()
        self.process2.terminate()
        self.process2.wait()

    def test_execution(self):
        """Tests the execution of the system by reading a configuration file, fetching
        requests from a dummy server, checking if the notification component is
        used properly, and if the persistence component works as expected."""
        # load data stores from configuration file
        def deserialize(task, data_str):
            if task == "TEST1":
                return Decimal(data_str)
            elif task == "TEST2":
                return Decimal(data_str)
            else:
                raise RuntimeError("Task not implemented")

        input_data_stores = load_config("./test/input_config.json", deserialize)

        # load the engines and notifiers
        notifiers = [find_notifier(input_data_stores[0].task_id), find_notifier(input_data_stores[1].task_id)]
        engines = [find_engine(input_data_stores[0].task_id), find_engine(input_data_stores[1].task_id)]

        for i in range(len(input_data_stores)):

            # check that we only have one price in history (in our config)
            before_items = input_data_stores[i].get_item_ids()

            for it in before_items:
                assert(len(input_data_stores[i].get_item_history(it)) == 1)

            # create and execute the agent
            agent = Agent(input_data_stores[i])
            agent.execute(notifiers[i], engines[i])

            # check if we fetched an additional price
            after_items = input_data_stores[i].get_item_ids()

            assert before_items == after_items

            for it in after_items:
                assert (len(input_data_stores[i].get_item_history(it)) == 2)

            # assert that notifier works properly
            if input_data_stores[i].task_id == "TASK1":
                self.assertEqual(len(notifiers[i].messages), 2)
            elif input_data_stores[i].task_id == "TASK2":
                self.assertEqual(len(notifiers[i].messages), 2)
            self.assertTrue(notifiers[i].alerted)

        # check that persistence works fine
        def serialize(task, data_point):
            if task == "TEST1":
                return str(data_point)
            elif task == "TEST2":
                return str(data_point)
            else:
                raise RuntimeError("Task not implemented")

        save_config(input_data_stores, "./test/output_config.json", serialize)

        output_data_stores = load_config("./test/output_config.json", deserialize)

        assert input_data_stores == output_data_stores

        os.remove("./test/output_config.json")


if __name__ == "__main__":
    unittest.main()