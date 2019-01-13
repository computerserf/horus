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
import time

from decimal import Decimal
from main.data_store import DataStore
from main.interfaces import Notifier, Engine
from main.agent import Agent

class TestAgent(unittest.TestCase):
    """Tests the agent class"""

    class FakeDataStore(DataStore):
        def __init__(self, task_id="AGENT_TEST"):
            self.task_id = task_id
            self.item_history = [Decimal(500)]
            self.modified = False

        def get_config_value(self, key):
            if key == "server_url":
                return "localhost"
            elif key == "max_history_length":
                return 2
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
            self.modified = True
            if key == "item1.html":
                self.item_history = history
            else:
                raise KeyError("Item '" + key + "' not mocked")

    class TestEngine(Engine):

        def __init__(self):
            pass

        def fetch(self, server_url, item_id):
            return Decimal(385)

        def compare(self, latest_data_point, history):
            return latest_data_point < history[-1]

        def wait(self):
            time.sleep(5)

    class TestNotifier(Notifier):

        def __init__(self):
            self.messages = []
            self.notified = False

        def add(self, item_id, latest_data_point):
            self.messages.append("item id '" + item_id + "' price dropped to " + str(latest_data_point))

        def alert(self):
            print("Test store has the following notifications:")
            for m in self.messages:
                print("=> " + m)
            self.notified = True

    def test_invalid_history_length(self):
        """Tests what happens if the agent is given an invalid history length"""

        class LocalDataStore(self.FakeDataStore):

            def get_config_value(self, key):
                if key == "max_history_length":
                    return 0
                else:
                    return super().get_config_value(key)

        notifier = self.TestNotifier()
        engine = self.TestEngine()
        data_store = LocalDataStore()
        agent = Agent(data_store)

        with self.assertRaises(RuntimeError):
            agent.execute(notifier, engine)

    def test_single_item_pass(self):
        """Tests if the agent can handle a single item normally that passes on"""

        notifier = self.TestNotifier()
        engine = self.TestEngine()
        data_store = self.FakeDataStore()
        agent = Agent(data_store)

        agent.execute(notifier, engine)

        history = data_store.get_item_history("item1.html")

        self.assertTrue(len(history) == 2)
        self.assertTrue(history[-1] == Decimal(385) and history[-2] == Decimal(500))
        self.assertTrue(data_store.modified)
        self.assertTrue(notifier.notified)
        self.assertTrue(len(notifier.messages) == 1)

    def test_double_item_pass(self):
        """Tests if the agent can handle more than a single item correctly"""

        class LocalDataStore(self.FakeDataStore):

            def __init__(self):
                self.item1_history = [Decimal(500)]
                self.item2_history = [Decimal(1000)]

            def get_item_ids(self):
                return ["item1.html", "item2.html"]

            def get_item_history(self, id):
                if id == "item1.html":
                    return self.item1_history
                elif id == "item2.html":
                    return self.item2_history
                else:
                    return super().get_item_history(id)

            def set_item_history(self, key, history):
                print("setting price key = '" + key + "', value = '" + str(history) + "'")
                self.modified = True
                if key == "item1.html":
                    self.item1_history = history
                elif key == "item2.html":
                    self.item2_history = history
                else:
                    raise KeyError("Item '" + key + "' not mocked")

        class LocalEngine(self.TestEngine):

            def __init__(self):
                pass

            def fetch(self, server_url, item_id):
                if item_id == "item1.html":
                    return Decimal(385)
                elif item_id == "item2.html":
                    return Decimal(999)
                assert False

        notifier = self.TestNotifier()
        engine = LocalEngine()
        data_store = LocalDataStore()
        agent = Agent(data_store)

        agent.execute(notifier, engine)

        history1 = data_store.get_item_history("item1.html")
        history2 = data_store.get_item_history("item2.html")

        self.assertTrue(len(history1) == 2)
        self.assertTrue(history1[-1] == Decimal(385))
        self.assertTrue(len(history2) == 2)
        self.assertTrue(history2[-1] == Decimal(999))
        self.assertTrue(data_store.modified)
        self.assertTrue(notifier.notified)
        self.assertTrue(len(notifier.messages) == 2)

    def test_history_is_too_large(self):
        """Tests the agent's behavior when the history length is above the limit"""

        class LocalDataStore(self.FakeDataStore):

            def __init__(self):
                self.item_history = [Decimal(500), Decimal(650), Decimal(550)]

        notifier = self.TestNotifier()
        engine = self.TestEngine()
        data_store = LocalDataStore()
        agent = Agent(data_store)

        agent.execute(notifier, engine)

        history = data_store.get_item_history("item1.html")

        self.assertTrue(len(history) == 2)
        self.assertTrue(history[-2] == Decimal(550) and history[-1] == Decimal(385))
        self.assertTrue(data_store.modified)
        self.assertTrue(notifier.notified)
        self.assertTrue(len(notifier.messages) == 1)

    def test_history_grows_too_large(self):
        """Tests the agent's behavior when the history grows larger than the limit"""

        class LocalDataStore(self.FakeDataStore):
            def __init__(self):
                self.item_history = [Decimal(500), Decimal(650)]

        notifier = self.TestNotifier()
        engine = self.TestEngine()
        data_store = LocalDataStore()
        agent = Agent(data_store)

        agent.execute(notifier, engine)

        history = data_store.get_item_history("item1.html")

        self.assertTrue(len(history) == 2)
        self.assertTrue(history[-2] == Decimal(650) and history[-1] == Decimal(385))
        self.assertTrue(data_store.modified)
        self.assertTrue(notifier.notified)
        self.assertTrue(len(notifier.messages) == 1)

    def test_single_item_fail(self):
        """Tests the agent's behavior when a single item fails on comparison"""

        class LocalEngine(self.TestEngine):

            def __init__(self):
                pass

            def fetch(self, server_url, item_id):
                return Decimal(685)

        notifier = self.TestNotifier()
        engine = LocalEngine()
        data_store = self.FakeDataStore()
        agent = Agent(data_store)

        agent.execute(notifier, engine)

        history = data_store.get_item_history("item1.html")

        self.assertTrue(len(history) == 2)
        self.assertTrue(history[-1] == Decimal(685))
        self.assertTrue(data_store.modified)
        self.assertTrue(notifier.notified)
        self.assertTrue(len(notifier.messages) == 0)


if __name__ == "__main__":
    unittest.main()