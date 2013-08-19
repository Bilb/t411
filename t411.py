#! /usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Python interface for T411.me

Author : Arnout Pierre <pierre@arnout.fr>
"""

from http.client import HTTPSConnection
from urllib.parse import urlencode
import json

HTTP_OK = 200
API_URL = 'api.t411.me'
USER_FILE = 'user.json'
HTTP_HEADERS = {'Content-type': 'application/x-www-form-urlencoded'}

class T411 :
    """ Base class for t411 interface """

    def __init__(self, username = None, password = None) :
        """ Get user credentials and authentificate it, if any credentials
        defined use token stored in user file
        """
        
        if username is None or password is None :
            # Try to read user file
            try :
                u_file = open(USER_FILE, 'r')
            except :
                print('Error, you have to define an user and password. Signup '
                     +'at http://www.t411.me/users/signup/')
            
            #Extract data from file
            data = json.loads(u_file.read())
            try :
                token = data['token']
                uid = data['uid']
            except :
                print('Error, user file seems to be wrong. Restart with '
                     +'credentials informations')
        else :
            # Authentification and storing token
            auth = json.loads(self._auth(username, password))
            if 'error' in auth :
                print(auth['error'])
                return None
            else :
                token = auth['token']
                uid = auth['uid']

                # Create or update user file
                data = {'uid': '%s' % uid, 'token': '%s' % token}
                data = json.dumps(data)

                u_file = open(USER_FILE, 'w')
                u_file.write(data)
                u_file.close()
                del u_file

        self._token = token
        self._uid = uid

    def _auth(self, username, password) :
        """ Authentificate user and store token """
        return self.call('auth', {'username': username, 'password': password})

    def call(self, method = '', params = None) :
        """ Call T411 API """
        if params != None :
            params = urlencode(params)
        
        headers = HTTP_HEADERS
        if method != 'auth' :
            headers['Authorization'] = self._token

        conn = HTTPSConnection(API_URL)
        conn.request('POST', '/%s' % method, body = params, headers = headers)
        r = conn.getresponse()

        if r.status == HTTP_OK :
            rt = str(r.read(), encoding = "UTF-8")
            conn.close()
            
            return rt
        else :
            conn.close()
            return False

    def me(self) :
        """ Get personal informations """
        return self.call('users/profile/%s' % self._uid)

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
