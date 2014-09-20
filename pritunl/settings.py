from pritunl.constants import *
from pritunl.exceptions import *
from pritunl.descriptors import *
from pritunl.settings_test import SettingsTest
from pritunl.mongo_transaction import MongoTransaction
import pritunl.mongo as mongo
import pritunl.listener as listener

class Settings(object):
    @cached_static_property
    def collection(cls):
        return mongo.get_collection('system')

    @cached_property
    def test(self):
        return SettingsTest()

    def start(self):
        listener.add_listener('setting', self.on_msg)

    def on_msg(self, msg):
        setattr(getattr(self, msg[0]), msg[1], msg[2])

    def commit(self, all_fields=False):
        bulk = self.collection.initialize_unordered_bulk_op()

        for group in dir(self):
            if group[0] == '_' or group in SETTINGS_RESERVED:
                continue
            doc = getattr(self, group).get_commit_doc(all_fields)

            bulk.find({
                '_id': doc['_id'],
            }).upsert().update({'$set': doc})

        bulk.execute()
