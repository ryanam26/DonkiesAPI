import argparse
import requests
import sys
import time


class ManualMember:
    """
    Currently works for Weels Fargo, but can be adjusted for other banks.
    """
    API_URL = 'http://localhost:8000'
    USER_EMAIL = 'alex@donkies.co'
    USER_PASSWORD = '111'
    USER_FIRST_NAME = 'Alex'
    USER_LAST_NAME = 'Alex'

    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-u', help='Username')
        parser.add_argument('-p', help='Password')
        parser.add_argument(
            '-c', help='Institution code', default='wells_fargo')
        p = parser.parse_args()

        self.username = getattr(p, 'u', None)
        if self.username is None:
            sys.exit('Error: username is not provided.')

        self.password = getattr(p, 'p', None)
        if self.password is None:
            sys.exit('Error: password is not provided.')

        self.institution_code = getattr(p, 'c')
        self.token = None

    def get_headers(self):
        if self.token is None:
            sys.exit('Token is not defined.')
        return {'Authorization': 'Token {}'.format(self.token)}

    def registration(self):
        url = self.API_URL + '/v1/auth/signup'
        dic = {
            'email': self.USER_EMAIL,
            'password': self.USER_PASSWORD,
            'first_name': self.USER_FIRST_NAME,
            'last_name': self.USER_LAST_NAME
        }
        r = requests.post(url, json=dic)
        if r.status_code == 204:
            print('Registration successful.')
            print('Waiting 10 seconds while user will be created in Atrium...')
            time.sleep(10)
            return

        if r.status_code == 400:
            print(r.text)

    def login(self):
        url = self.API_URL + '/v1/auth/login'
        dic = {
            'email': self.USER_EMAIL,
            'password': self.USER_PASSWORD
        }
        r = requests.post(url, json=dic)
        if r.status_code == 200:
            self.token = r.json()['token']
        else:
            sys.exit('Can not login.')

    def get_credentials(self):
        """
        Not used.
        """
        url = self.API_URL + '/v1/credentials/{}'.format(self.institution_code)
        r = requests.get(url, headers=self.get_headers())
        if r.status_code == 200:
            self.credentials = r.json()
        sys.exit('Can not get credentials')

    def get_credentials_wells_fargo(self):
        return [
            {'field_name': 'userid', 'value': self.username},
            {'field_name': 'password', 'value': self.password},
        ]

    def create_member(self):
        url = self.API_URL + '/v1/members'
        dic = {
            'institution_code': self.institution_code,
            'credentials': self.get_credentials_wells_fargo()
        }
        r = requests.post(url, json=dic, headers=self.get_headers())
        print(r.text)

    def run(self):
        self.registration()
        self.login()
        self.create_member()


if __name__ == '__main__':
    mm = ManualMember()
    mm.run()
