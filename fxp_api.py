#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Authors:
    - Tina
Mail:
    tina.cochet@viaa.be
Description:
    - Standalone flask api for fxp celery worker
    - Accepts:
        - POST to /
        - GET to /info
NOTES:
    - please use it with uwsgi server
USAGE:
    - POST a msg like the below to service:
        {
          "destination_file": "target-testfile.txt",
          "destination_host": "host2",
          "destination_password": "passwd2",
          "destination_path": "path2",
          "destination_user": "path2",
          "source_file": "testfile.txt",
          "source_host": "host1",
          "source_password": "passwd1",
          "source_path": "path1",
          "source_user": "user1",
          "move": false
        }
    - GET /info?taskid=XXXXX-YYY-UUU-UID&state=true/fasle
    Messgae gets validated and a request to worker will be send
"""
import logging
from logging.handlers import RotatingFileHandler
import datetime
import json
import configparser
from celery import chain
from celery.utils.log import get_logger
from flask import request, Flask
from schema import Schema, And, Use, Optional, SchemaError
from worker_tasks import res_pub, fxp_task
from task_info import fxp_result
LOG_FORMAT = ('[%(asctime)-15s %(levelname) -8s %(name) -10s %(funcName) '
              '-20s %(lineno) -5d] %(message)s')
logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)
LOGGER = get_logger(__name__)
CONFIG = configparser.ConfigParser()
CONFIG.read('config/config.ini')

APP = Flask(__name__)

@APP.route("/info", methods=['GET'])
def info():
    '''Gets state of a given task_id, parm state=true for task result'''
    default_error = json.dumps({'ERROR': 'No such fxp_id or wrong request'})
    try:
        t_id = request.args.get('task_id')
        LOGGER.info('Fetching results from ES')
        state = request.args.get('state') or False
        if state == 'true':
            res = fxp_result(task_id=t_id, state=state)
        else:
            res = fxp_result(task_id=t_id, state=False)
        
    except (ValueError, TypeError) as info_err:
        LOGGER.error(info_err)
        res = json.dumps({'ERROR': str(info_err)})
    try:
        res = json.dumps(res)
        return(res)
    except (ValueError, TypeError):
        return str(res)
    return default_error
        


@APP.route("/", methods=['POST'])
def fxp_call():
    """Accepts a post in json and start a worker chain ob async
       Chain:
            - First FXP
            - Then Post to Rabitmq
    """
    LOGGER.debug('**** FXP call from API ****')
    msg = request.get_json(silent=True)
    LOGGER.debug('incoming message %s', msg)
    default_err = {'error': 'not a valid message'}
    time_now = datetime.datetime.now().isoformat()
    job = chain(fxp_task.s(msg),
                res_pub.s(CONFIG['RabWorker']['user'],
                          CONFIG['RabWorker']['passw'],
                          CONFIG['RabWorker']['hostname'],
                          queue='pyfxp-result',
                          routing_key='py-fxp'))

    def check_msg():
        """Checks msg to conform to fields and types of values"""
        def check(conf_schema, conf):
            try:
                conf_schema.validate(conf)
                return True
            except SchemaError:
                return False

        conf_schema = Schema({
            'destination_file': And(Use(str)),
            'destination_host': And(Use(str)),
            'destination_password': And(Use(str)),
            'destination_path': And(Use(str)),
            'destination_user': And(Use(str)),
            'source_file': And(Use(str)),
            'source_host': And(Use(str)),
            'source_password': And(Use(str)),
            'source_path': And(Use(str)),
            'source_user': And(Use(str)),
            Optional('move'): And(Use(bool))
            })
        valid_msg = check(conf_schema, msg)
        if valid_msg:
            return True
        return False
    chk_msg = check_msg()
    LOGGER.info('valid fxp message: %s', chk_msg)
    if chk_msg:
        j = job.apply_async(retry=True)
        job_id = j.id
        LOGGER.info('fxp task %s started', job_id)
        LOGGER.info('FXP request for destination_file %s',
                    msg['destination_file'])
        out = {'FxpWorkId': j.parent.id,
               'PublishId': job_id,
               'Date': str(time_now)}
        LOGGER.info(str(out))
        return json.dumps(out)
    return json.dumps(default_err)


if __name__ == '__main__':
    LOG_FORMAT = ('[%(asctime)-15s %(levelname) -6s %(name) -8s %(funcName) '
                  '-14s %(lineno) -5d] %(message)s')
    FORMATTER = logging.Formatter(LOG_FORMAT)
    HANDLER = RotatingFileHandler('api.log',
                                  maxBytes=500000,
                                  backupCount=1)
    HANDLER.setLevel(logging.DEBUG)
    HANDLER.setFormatter(FORMATTER)
    LOGGER.addHandler(HANDLER)
    APP.debug = True
    APP.run(port=8888,
            host='0.0.0.0')
