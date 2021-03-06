from bson.json_util import dumps
from bson.objectid import ObjectId
from flask import jsonify, request, Blueprint
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import pytz

from v1 import not_found, Status
from v1.config.db_config import mongo

collectionapi = Blueprint('collectionapi', __name__)


@collectionapi.route('/add', methods=['POST'])
def add_collections():
    _json = request.json
    _donationid = _json['donation_id']
    _donormobile = _json['donor_mobile']
    _volunteerid = _json['volunteer_id']
    _volunteermobile = _json['volunteer_mobile']
    _centreid = _json['_centreid']

    # validate the received values
    if _donationid and _volunteerid and request.method == 'POST':
        # save details
        result = mongo.db.collection.insert_one(
                    {
                        'donation_id': _donationid,
                        'donor_mobile': _donormobile,
                        'volunteer_id': _volunteerid,
                        'volunteer_mobile': _volunteermobile,
                        'centreid': _centreid,
                        'status': Status.ACCEPTED,
                        'collectiondate': datetime.now(pytz.timezone('Asia/Kolkata')),
                     }
        )
        resp = jsonify({'id': str(result.inserted_id)})
        resp.status_code = 200
        return resp
    else:
        return not_found()


@collectionapi.route('/list', methods=['GET'])
def collections_list():
    coll_list = mongo.db.collection.find()
    resp = dumps(coll_list)
    return resp

@collectionapi.route('/list', methods=['GET'])
def collections_list_for_volunteer():
    volunteer_mobile = request.args.get('vmobile', None)
    coll_list = mongo.db.collection.find({'volunteer_mobile': volunteer_mobile})
    resp = dumps(coll_list)
    return resp


@collectionapi.route('/<donatonid>', methods=['GET'])
def get_collection_info(donationid):
    centre = mongo.db.collection.find_one({'donation_id': donationid})
    resp = dumps(centre)
    return resp


@collectionapi.route('/update', methods=['PUT'])
def update_collection():
    _json = request.json
    _id = _json['_id']
    _donationid = _json['donation_id']
    _donormobile = _json['donor_mobile']
    _volunteerid = _json['volunteer_id']
    _volunteermobile = _json['volunteer_mobile']
    _centreid = _json['centreid']
    _status = _json['status']

    # validate the received values
    if _donationid and _volunteerid and request.method == 'PUT':
        # save edits
        _delivered_date = datetime.now(pytz.timezone('Asia/Kolkata')) if Status.DELIVERED==_status else None
        mongo.db.collection.update_one(
            {
                #'_id': ObjectId(_donationid['$oid']) if '$oid' in _donationid else ObjectId(_donationid)
                'donation_id': _donationid
            },
            {
                '$set':
                    {
                        'volunteer_mobile': _volunteermobile,
                        'status': _status,
                        'delivered_date': _delivered_date
                    }
            }
        )
        resp = jsonify('Collection updated successfully!')
        resp.status_code = 200
        return resp
    else:
        return not_found()


@collectionapi.route('/delete/<id>', methods=['DELETE'])
def delete_collection(id):
    item = mongo.db.colleection.delete_one({'_id': ObjectId(id)})
    if item.deleted_count:
        resp = jsonify('Collection deleted successfully!')
        resp.status_code = 200
        return resp
    else:
        return not_found()
