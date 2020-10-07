from django.http import HttpRequest


def make_request_obj(param_name, value=None):
    # Set the query param
    rq = HttpRequest()
    rq.query_params = MultiValueDict()
    rq.query_params[param_name] = value
    return rq
