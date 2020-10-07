from unittest import TestCase

from filter_deep_object_param import filter_deep_object_param

from . import make_request_obj


class BooleanTests(TestCase):
    """
    Test the 'filter_multi_param' parsing.
    """
    def test_value_conversion(self):
        # Boolean conversions
        self.assertEqual(
            filter_deep_object_param(make_request_obj(
                'filter[system_profile][started]', 'true'
            ), 'system_profile'),
            Q(system_profile__started=True)
        )
        self.assertEqual(
            filter_deep_object_param(make_request_obj(
                'filter[system_profile][started]', 'True'
            ), 'system_profile'),
            Q(system_profile__started=True)
        )
        self.assertEqual(
            filter_deep_object_param(make_request_obj(
                'filter[system_profile][started]', 'false'
            ), 'system_profile'),
            Q(system_profile__started=False)
        )
        self.assertEqual(
            filter_deep_object_param(make_request_obj(
                'filter[system_profile][started]', 'False'
            ), 'system_profile'),
            Q(system_profile__started=False)
        )
