import calendar
import time
import unittest

import jwt


class JWTtester(unittest.TestCase):

    def setUp(self):
        self.key = 'FIREFOX_MARKETPLACE_KEY'
        self.secret = 'FIREFOX_MARKETPLACE_SECRET'
        self.verifier = None

    def payload(self, app_id=None, exp=None, iat=None,
                typ='mozilla/postback/pay/v1', extra_req=None, extra_res=None):
        if not app_id:
            app_id = self.key
        if not iat:
            iat = calendar.timegm(time.gmtime())
        if not exp:
            exp = iat + 3600  # expires in 1 hour

        req = {'pricePoint': 1,
               'name': 'My bands latest album',
               'description': '320kbps MP3 download, DRM free!',
               'productData': 'my_product_id=1234'}
        if extra_req:
            req.update(extra_req)

        res = {'transactionID': '1234'}
        if extra_res:
            res.update(extra_res)

        return {
            'iss': 'marketplace.mozilla.org',
            'aud': app_id,
            'typ': typ,
            'exp': exp,
            'iat': iat,
            'request': req,
            'response': res,
        }

    def request(self, app_secret=None, payload=None, encode_kwargs=None,
                **payload_kw):
        if not app_secret:
            app_secret = self.secret
        if not payload:
            payload = self.payload(**payload_kw)
        if not encode_kwargs:
            encode_kwargs = {}

        encode_kwargs.setdefault('algorithm', 'HS256')
        encoded = jwt.encode(payload, app_secret, **encode_kwargs)
        return unicode(encoded)  # e.g. django always passes unicode

    def verify(self, request=None, update=None, update_request=None,
               verifier=None, verify_kwargs=None):
        if not verifier:
            verifier = self.verifier
        if not request:
            payload = self.payload()
            if update_request:
                payload['request'].update(update_request)
            if update:
                payload.update(update)
            request = self.request(payload=payload)
        if not verify_kwargs:
            verify_kwargs = {}
        return verifier(request, self.key, self.secret, **verify_kwargs)
