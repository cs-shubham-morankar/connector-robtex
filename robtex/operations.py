""" Copyright start
  Copyright (C) 2008 - 2022 Fortinet Inc.
  All rights reserved.
  FORTINET CONFIDENTIAL & FORTINET PROPRIETARY SOURCE CODE
  Copyright end """

import requests
from connectors.core.connector import get_logger, ConnectorError
logger = get_logger('robtex')


class Robtex(object):

    def __init__(self, config):
        self.server_url = config.get('server').strip()
        if not self.server_url.startswith('https://'):
            self.server_url = 'https://{0}/'.format(self.server_url)

    def make_api_call(self, endpoint=None, method='GET', health_check=False):
        url = self.server_url + endpoint
        logger.debug('Final url to make rest call is: {0}'.format(url))
        try:
            logger.debug('Making a request with {0} method.'.format(method))
            response = requests.request(method, url)
            if response.status_code in [200]:
                if health_check:
                    return response
                try:
                    logger.debug(
                        'Converting the response into JSON format after returning with status code: {0}'.format(
                            response.status_code))
                    response_data = response.json()
                    return {'status': response_data['status'] if 'status' in response_data else 'Success', 'data': response_data}
                except Exception as e:
                    response_data = response.content
                    logger.error('Failed with an error: {0}. The response details are: {1}'.format(e, response_data))
                    return {'status': 'Failure', 'data': response_data}
            else:
                logger.error('Failed with response {0}'.format(response))
                raise ConnectorError(
                    {'status': 'Failure', 'status_code': str(response.status_code), 'response': response})
        except Exception as e:
            logger.exception(str(e))
            raise ConnectorError(str(e))

    def get_ip_query_details(self, params):
        endpoint = '/ipquery/{0}'.format(params.get('ip_address'))
        return self.make_api_call(endpoint=endpoint)

    def get_autonomous_system_query_details(self, params):
        endpoint = '/asquery/{0}'.format(params.get('autonomous_system_number'))
        return self.make_api_call(endpoint=endpoint)


def _run_operation(config, params):
    rb_obj = Robtex(config)
    command = getattr(Robtex, params['operation'])
    response = command(rb_obj, params)
    return response


def _check_health(config):
    try:
        rb_obj = Robtex(config)
        rb_obj.make_api_call(endpoint='/ipquery/', health_check=True)
        return True
    except Exception as err:
        logger.exception('Health check failed with: {0}'.format(err))
        raise ConnectorError('Health check failed with: {0}'.format(err))
