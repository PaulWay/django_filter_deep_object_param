from . import make_request_obj

from UnitTest import TestCase


class BooleanTests(TestCase):
    """
    Test the 'filter_multi_param' parsing.
    """
    def test_value_conversion(self):
        # Boolean conversions
        self.assertEqual(
            filter_multi_param(make_request_obj(
                'filter[system_profile][started]', 'true'
            ), 'system_profile'),
            Q(system_profile__started=True)
        )
        self.assertEqual(
            filter_multi_param(make_request_obj(
                'filter[system_profile][started]', 'True'
            ), 'system_profile'),
            Q(system_profile__started=True)
        )
        self.assertEqual(
            filter_multi_param(make_request_obj(
                'filter[system_profile][started]', 'false'
            ), 'system_profile'),
            Q(system_profile__started=False)
        )
        self.assertEqual(
            filter_multi_param(make_request_obj(
                'filter[system_profile][started]', 'False'
            ), 'system_profile'),
            Q(system_profile__started=False)
        )
