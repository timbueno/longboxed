from flask.ext.login import UserMixin
from mongokit import Document
from requests import get, post

from datetime import datetime

# ===================================
# 
# Validators
#
# ===================================
def max_length(length):
    def validate(value):
        if len(value) <= length:
            return True
        raise Exception('%s must be at most %s characters long' % length)
    return validate

# ===================================
# 
# User Model
#
# ===================================
class User(Document, UserMixin):
    structure = {
        'id': unicode,
        'info': {
            'full_name': unicode,
            'first_name': unicode,
            'last_name': unicode,
            'gender': unicode,
            'birthday': datetime,
            'email': unicode
        },
        'comics': {
            'favorites': [unicode]
        },
        'settings': {
            'display_favs': bool,
            'default_cal': unicode
        },
        'tokens': {
            'refresh_token': unicode,
            'access_token': unicode,
            'expire_time': datetime,
        },
        'date_creation': datetime
    }
    validators = {
        'info.full_name': max_length(50),
        'info.email': max_length(120)
    }
    required_fields = ['id', 'info.email', 'date_creation']
    default_values = {
        'date_creation': datetime.utcnow,
        'settings.display_favs': True,
        'settings.default_cal': u'primary'
    }
    use_dot_notation = True
    
    def __repr__(self):
        return '<User %r>' % (self.name)


# # ===================================
# # 
# # Comic Book Model
# # 
# # ===================================
# class Comic(Document, UserMixin):
#     structure = {
#         'id': unicode,
#         'publisher': unicode,
#         'title': unicode,
#         'price': float,
#         'link': unicode,
#         'image_url': unicode,
#         'date': datetime,
#         'last_updated': datetime
#     }
#     required_fields = ['id', 'title']
#     default_values = {
#         'last_updated': datetime.utcnow
#     }
#     use_dot_notation = True
#     def __repr__(self):
#         return '<Comic %r>' % (self.name)

# ===================================
# 
# Comic Book Model
# 
# ===================================
class Comic(Document):
    structure = {
        'productID': unicode, # 0
        'info': { #1
            'name': unicode,
            'issue_number': float,
            'issues': float,
            'other': unicode,
            'complete_title': unicode,
            'one_shot': bool
        },
        'alink': unicode, # 4
        'thumbnail': unicode, # 5
        'bigImage': unicode, # 6
        'retailPrice': float, # 8
        'description': unicode, # 11
        'onSaleDate': datetime, # 12
        'genre': unicode, # 13
        'people': unicode, # 14
        'popularity': float, # 16
        'lastUpdated': datetime, # 17
        'publisher': unicode, # 19
        'id': unicode, # 20
        'category': unicode, # 21
        'upc': unicode # 25
    }
    required_fields = ['id', 'info.complete_title']
    use_dot_notation = True
    def __repr__(self):
        return '<Comic %r>' % (self.info.name)

    def is_float(self, number):
        try: 
            float(number)
            return True
        except ValueError:
            return False

    def complete_title(self):
        title = ''
        if self.info.name:
            title = title + self.info.name
        if self.is_float(self.info.issue_number):
            title = title + ' #%d' % self.info.issue_number
        if self.is_float(self.info.issues):
            title = title + ' (of %d)' % self.info.issues
        if self.info.other:
            title = title + self.info.other
        return title

