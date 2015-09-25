from __future__ import absolute_import

import math
from datetime import datetime
from datetime import timedelta
import json
import unittest

import six

from ably import AblyRest
from ably import Options
from ably.types.capability import Capability
from ably.util.exceptions import AblyException

from test.ably.restsetup import RestSetup
from test.ably.utils import VaryByProtocolTestsMetaclass, dont_vary_protocol

test_vars = RestSetup.get_test_vars()


@six.add_metaclass(VaryByProtocolTestsMetaclass)
class TestRestCapability(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ably = AblyRest(key=test_vars["keys"][0]["key_str"],
                            host=test_vars["host"],
                            port=test_vars["port"],
                            tls_port=test_vars["tls_port"],
                            tls=test_vars["tls"])

    def per_protocol_setup(self, use_binary_protocol):
        self.ably.options.use_binary_protocol = use_binary_protocol

    def test_blanket_intersection_with_key(self):
        key = test_vars['keys'][1]
        token_details = self.ably.auth.request_token(key_name=key['key_name'],
                                                     key_secret=key['key_secret'])
        expected_capability = Capability(key["capability"])
        self.assertIsNotNone(token_details.token, msg="Expected token")
        self.assertEqual(expected_capability, token_details.capability,
                         msg="Unexpected capability.")

    def test_equal_intersection_with_key(self):
        key = test_vars['keys'][1]

        token_params = {
            "capability": key["capability"],
        }

        token_details = self.ably.auth.request_token(key_name=key['key_name'],
                key_secret=key['key_secret'],
                token_params=token_params)

        expected_capability = Capability(key["capability"])

        self.assertIsNotNone(token_details.token, msg="Expected token")
        self.assertEqual(expected_capability, token_details.capability,
                         msg="Unexpected capability")

    @dont_vary_protocol
    def test_empty_ops_intersection(self):
        key = test_vars['keys'][1]

        token_params = {
            "capability": {
                "testchannel": ["subscribe"],
            },
        }

        self.assertRaises(AblyException, self.ably.auth.request_token,
                key_name=key['key_name'],
                key_secret=key['key_secret'],
                token_params=token_params)

    @dont_vary_protocol
    def test_empty_paths_intersection(self):
        key = test_vars['keys'][1]

        token_params = {
            "capability": {
                "testchannelx": ["publish"],
            },
        }

        self.assertRaises(AblyException, self.ably.auth.request_token,
                key_name=key['key_name'],
                key_secret=key['key_secret'],
                token_params=token_params)

    def test_non_empty_ops_intersection(self):
        key = test_vars['keys'][4]

        kwargs = {
            "key_name": key["key_name"],
            "key_secret": key["key_secret"],
            "token_params": {
                "capability": {
                    "channel2": ["presence", "subscribe"],
                },
            },
        }

        expected_capability = Capability({
            "channel2": ["subscribe"]
        })

        token_details = self.ably.auth.request_token(**kwargs)

        self.assertIsNotNone(token_details.token, msg="Expected token")
        self.assertEqual(expected_capability, token_details.capability,
                         msg="Unexpected capability")

    def test_non_empty_paths_intersection(self):
        key = test_vars['keys'][4]

        kwargs = {
            "key_name": key["key_name"],

            "key_secret": key["key_secret"],
            "token_params": {
                "capability": {
                    "channel2": ["presence", "subscribe"],
                    "channelx": ["presence", "subscribe"],
                },
            },
        }

        expected_capability = Capability({
            "channel2": ["subscribe"]
        })

        token_details = self.ably.auth.request_token(**kwargs)

        self.assertIsNotNone(token_details.token, msg="Expected token")
        self.assertEqual(expected_capability, token_details.capability,
                         msg="Unexpected capability")

    def test_wildcard_ops_intersection(self):
        key = test_vars['keys'][4]

        kwargs = {
            "key_name": key["key_name"],
            "key_secret": key["key_secret"],
            "token_params": {
                "capability": {
                    "channel2": ["*"],
                },
            },
        }

        expected_capability = Capability({
            "channel2": ["subscribe", "publish"]
        })

        token_details = self.ably.auth.request_token(**kwargs)

        self.assertIsNotNone(token_details.token, msg="Expected token")
        self.assertEqual(expected_capability, token_details.capability,
                         msg="Unexpected capability")

    def test_wildcard_ops_intersection_2(self):
        key = test_vars['keys'][4]

        kwargs = {
            "key_name": key["key_name"],
            "key_secret": key["key_secret"],
            "token_params": {
                "capability": {
                    "channel6": ["publish", "subscribe"],
                },
            },
        }

        expected_capability = Capability({
            "channel6": ["subscribe", "publish"]
        })

        token_details = self.ably.auth.request_token(**kwargs)

        self.assertIsNotNone(token_details.token, msg="Expected token")
        self.assertEqual(expected_capability, token_details.capability,
                         msg="Unexpected capability")

    def test_wildcard_resources_intersection(self):
        key = test_vars['keys'][2]

        kwargs = {
            "key_name": key["key_name"],
            "key_secret": key["key_secret"],
            "token_params": {
                "capability": {
                    "cansubscribe": ["subscribe"],
                },
            },
        }

        expected_capability = Capability({
            "cansubscribe": ["subscribe"]
        })

        token_details = self.ably.auth.request_token(**kwargs)

        self.assertIsNotNone(token_details.token, msg="Expected token")
        self.assertEqual(expected_capability, token_details.capability,
                         msg="Unexpected capability")

    def test_wildcard_resources_intersection_2(self):
        key = test_vars['keys'][2]

        kwargs = {
            "key_name": key["key_name"],
            "key_secret": key["key_secret"],
            "token_params": {
                "capability": {
                    "cansubscribe:check": ["subscribe"],
                },
            },
        }

        expected_capability = Capability({
            "cansubscribe:check": ["subscribe"]
        })

        token_details = self.ably.auth.request_token(**kwargs)

        self.assertIsNotNone(token_details.token, msg="Expected token")
        self.assertEqual(expected_capability, token_details.capability,
                         msg="Unexpected capability")

    def test_wildcard_resources_intersection_3(self):
        key = test_vars['keys'][2]

        kwargs = {
            "key_name": key["key_name"],
            "key_secret": key["key_secret"],
            "token_params": {
                "capability": {
                    "cansubscribe:*": ["subscribe"],
                },
            },
        }

        expected_capability = Capability({
            "cansubscribe:*": ["subscribe"]
        })

        token_details = self.ably.auth.request_token(**kwargs)

        self.assertIsNotNone(token_details.token, msg="Expected token")
        self.assertEqual(expected_capability, token_details.capability,
                         msg="Unexpected capability")

    @dont_vary_protocol
    def test_invalid_capabilities(self):
        kwargs = {
            "token_params": {
                "capability": {
                    "channel0": ["publish_"],
                },
            },
        }

        with self.assertRaises(AblyException) as cm:
            token_details = self.ably.auth.request_token(**kwargs)

        the_exception = cm.exception
        self.assertEqual(400, the_exception.status_code)
        self.assertEqual(40000, the_exception.code)

    @dont_vary_protocol
    def test_invalid_capabilities_2(self):
        kwargs = {
            "token_params": {
                "capability": {
                    "channel0": ["*", "publish"],
                },
            },
        }

        with self.assertRaises(AblyException) as cm:
            token_details = self.ably.auth.request_token(**kwargs)

        the_exception = cm.exception
        self.assertEqual(400, the_exception.status_code)
        self.assertEqual(40000, the_exception.code)

    @dont_vary_protocol   
    def test_invalid_capabilities_3(self):
        capability = Capability({
            "channel0": []
        })

        kwargs = {
            "token_params": {
                "capability": {
                    "channel0": [],
                },
            },
        }

        with self.assertRaises(AblyException) as cm:
            token_details = self.ably.auth.request_token(**kwargs)

        the_exception = cm.exception
        self.assertEqual(400, the_exception.status_code)
        self.assertEqual(40000, the_exception.code)


