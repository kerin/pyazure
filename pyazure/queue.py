#!/usr/bin/env python
# encoding: utf-8
"""
Python wrapper around Windows Azure storage and management APIs

Authors:
    Sriram Krishnan <sriramk@microsoft.com>
    Steve Marx <steve.marx@microsoft.com>
    Tihomir Petkov <tpetkov@gmail.com>

License:
    GNU General Public Licence (GPL)
    
    This file is part of pyazure.
    
    pyazure is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    pyazure is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with pyazure. If not, see <http://www.gnu.org/licenses/>.
"""

import base64
from lxml import etree
from urllib2 import Request, urlopen, URLError

from util import *

class QueueMessage(): pass

class QueueStorage(Storage):
    def __init__(self, host, account_name, secret_key, use_path_style_uris = None):
        super(QueueStorage, self).__init__(host, account_name, secret_key, use_path_style_uris)

    def create_queue(self, name):
        req = RequestWithMethod("PUT", "%s/%s" % (self.get_base_url(), name))
        req.add_header("Content-Length", "0")
        self._credentials.sign_request(req)
        try:
            response = urlopen(req)
            return response.code
        except URLError, e:
            return e.code

    def delete_queue(self, name):
        req = RequestWithMethod("DELETE", "%s/%s" % (self.get_base_url(), name))
        self._credentials.sign_request(req)
        try:
            response = urlopen(req)
            return response.code
        except URLError, e:
            return e.code
            
    def put_message(self, queue_name, payload):
        data = "<QueueMessage><MessageText>%s</MessageText></QueueMessage>" % base64.encodestring(payload)
        req = RequestWithMethod("POST", "%s/%s/messages" % (self.get_base_url(), queue_name), data=data)
        req.add_header("Content-Type", "application/xml")
        req.add_header("Content-Length", len(data))
        self._credentials.sign_request(req)
        try:
            response = urlopen(req)
            return response.code
        except URLError, e:
            return e.code

    def get_message(self, queue_name):
        req = Request("%s/%s/messages" % (self.get_base_url(), queue_name))
        self._credentials.sign_request(req)
        response = urlopen(req)
        dom = etree.fromstring(response.read())
        messages = dom.findall(TAGS_ATOM_QUEUEMESSAGE)
        result = None
        if len(messages) == 1:
            message = messages[0]
            result = QueueMessage()
            result.id = message.find(TAGS_ATOM_MESSAGEID).text
            result.pop_receipt = message.find(TAGS_ATOM_POPRECEIPT).text
            result.text = base64.decodestring(message.find(TAGS_ATOM_MESSAGETEXT).text)
        return result

    def delete_message(self, queue_name, message):
        id = message.id
        pop_receipt = message.pop_receipt
        req = RequestWithMethod("DELETE", "%s/%s/messages/%s?popreceipt=%s" % (self.get_base_url(), queue_name, id, pop_receipt))
        self._credentials.sign_request(req)
        try:
            response = urlopen(req)
            return response.code
        except URLError, e:
            return e.code