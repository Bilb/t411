#! /usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Python interface for T411.me

Author : Arnout Pierre <pierre@arnout.fr>
"""

import getpass
import json
import requests

HTTP_OK = 200
API_URL = 'https://api.t411.me/%s'
USER_CREDENTIALS_FILE = 'user.json'



class T411Exception(BaseException):
    pass

class T411(object):
    """ Base class for t411 interface """

    def __init__(self, username = None, password = None) :
        """ Get user credentials and authentificate it, if any credentials
        defined use token stored in user file
        """
        
        try :
            with open(USER_CREDENTIALS_FILE) as user_cred_file:
                self.user_credentials = json.loads(user_cred_file.read())
                if 'uid' not in self.user_credentials or 'token' not in \
                        self.user_credentials:
                    raise T411Exception('Wrong data found in user file')
                else:
                    # we have to ask the user for its credentials and get
                    # the token from the API
                    user = raw_input('Please enter username: ')
                    password = getpass.getpass('Please enter password: ')
                    self._auth(user, password)
        except IOError as e:
            # we have to ask the user for its credentials and get
            # the token from the API
            user = raw_input('Please enter username: ')
            password = getpass.getpass('Please enter password: ')
            self._auth(user, password)
        except T411Exception as e:
            raise T411Exception(e.message)
        except Exception as e:
            raise T411Exception('Error while reading user credentials: %s.'\
                    % e.message)

    def _auth(self, username, password) :
        """ Authentificate user and store token """
        self.user_credentials = self.call('auth', {'username': username, 'password': password})
        print(self.user_credentials)
        if 'error' in self.user_credentials:
            raise T411Exception('Error while fetching authentication token: %s'\
                    % self.user_credentials['error'])
        # Create or update user file
        user_data = json.dumps({'uid': '%s' % self.user_credentials['uid'], 'token': '%s' % self.user_credentials['token']})
        with open(USER_CREDENTIALS_FILE, 'w') as user_cred_file:
            user_cred_file.write(user_data)
        return True

    def call(self, method = '', params = None) :
        """ Call T411 API """
        
        if method != 'auth' :
            req = requests.post(API_URL % method, data=params, headers={'Authorization': self.user_credentials['token']}  )
        else:
            req = requests.post(API_URL % method, data=params)
            
        if req.status_code == requests.codes.OK:
            return req.json()
        else :
            raise T411Exception('Error while sending %s request: HTTP %s' % \
                    (method, req.status_code))

    def me(self) :
        """ Get personal informations """
        return self.call('users/profile/%s' % self.user_credentials['uid'])

    def user(self, user_id) :
        """ Get user informations """
        return self.call('users/profile/%s' % user_id)

    def categories(self) :
        """ Get categories """
        return self.call('categories/tree')

    def terms(self) :
        """ Get terms """
        return self.call('terms/tree')

    def details(self, torrent_id) :
        """ Get torrent details """
        return self.call('torrents/details/%s' % torrent_id)

    def download(self, torrent_id) :
        """ Download a torrent """
        return self.call('torrents/download/%s' % torrent_id)



if __name__ == "__main__":
    t411 = T411()
    #print(t411.categories())
    
    
    
