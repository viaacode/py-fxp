#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 15 09:59:49 2019
Description:
    - FXP a file between 2 FTP servers
    - Param move=True, to delete the source file
    - Retry random wait between  1 min 3 min, on some FTP errors

Usage:
    Fxp('host1','user1','passwd1','host2','user2','passwd2',
        'full_source_path',
        'full_destination_path',move=False)()
@author: tina
"""
import os
# import dotenv
from viaa.configuration import ConfigParser
from viaa.observability import logging
import ftplib
import ftpext

# dotenv.load_dotenv('.env')
config = ConfigParser()
logger = logging.get_logger(__name__, config=config)
PORT = 21


def fxp_src(host='host1', user='user1', password='password1'):
    """ Define a source server, try tls fallback to none tls"""
    try:
        ftp_src = ftpext.FTPExt(host, PORT, user, password, True, True, 1)
        return ftp_src
    except ftplib.error_perm as e_perm:
        if str(e_perm).startswith('530'):
            # Set tls off
            ftp_src = ftpext.FTPExt(host, PORT, user, password, False, True, 1)
            return ftp_src
    except ConnectionError as conn_e:
        logger.error(conn_e)
        raise ConnectionError()

    def _close():
        """ Use this to close the connection"""
        ftp_src.close()


def fxp_dst(host='host2', user='user2', password='password2'):
    """ Define a destination server"""
    try:
        ftp_dst = ftpext.FTPExt(host, PORT, user, password, True, True, 1)
        return ftp_dst
    except ftplib.error_perm as e_perm:
        if str(e_perm).startswith('530'):
            # Set tls off
            ftp_dst = ftpext.FTPExt(host, PORT, user, password, False, True, 1)
            return ftp_dst
    except ConnectionError as conn_e:
        logger.error(conn_e)
        raise ConnectionError()

    def _close():
        ftp_dst.close()


def delete_from_ftp(del_file, FTPE=None):
    '''Delete a file from ftp'''
    try:
        FTPE.delete(del_file)
        return True
    except FileNotFoundError:
        logger.error('file: %s Not found', del_file)
    except ConnectionError as conn_e:
        logger.error(conn_e)
        raise ConnectionError(conn_e)


class Fxp():
    """ Class for FXP transfer """

    def __init__(self,
                 host1,
                 user1,
                 password1,
                 host2,
                 user2,
                 password2,
                 in_path,
                 out_path,
                 move=False):
        self.move = move
        self.host1 = host1
        self.host2 = host2
        self.fxp_src = fxp_src(host1, user1, password1)
        logger.info('Logged in to source server %s', self.host1)
        self.fxp_dst = fxp_dst(host2, user2, password2)
        logger.info('Logged in to destination server %s', self.host2)
        self.in_path = in_path
        self.in_dir, self.in_file = os.path.split(self.in_path)
        logger.info('cwd src host %s', self.in_dir)
        self.fxp_src.cwd(self.in_dir)
        # self.fxp_src.ls()
        self.out_path = out_path
        self.out_dir, self.out_file = os.path.split(self.out_path)
        logger.info('cwd dest host %s', self.out_dir)
        self.fxp_dst.cwd(self.out_dir)
        self.out = os.path.join(self.out_dir, self.out_file)

    def close(self):
        """Close the connections"""
        try:
            self.fxp_src.close()
            logger.info('closed connection to %s', self.host1)
        except ConnectionError as conn_e:
            logger.error(conn_e)
            raise ConnectionError()
        try:
            self.fxp_dst.close()
            logger.info('closed connection to %s', self.host2)
        except ConnectionError as conn_e:
            logger.error(conn_e)
            raise ConnectionError()
        return True

    def run(self):
        '''The fxp shizel happens here'''
        try:
            self.fxp_src.fxp_to(self.in_file, self.fxp_dst, self.out_file)
            logger.info(
                f"fxp OK for {self.in_file} from {self.host1} to {self.host2}")
            if self.move:
                logger.info('delting source file %s', self.in_path)
                delete_from_ftp(del_file=self.in_file, FTPE=self.fxp_src)
            self.close()
        except ftpext.ftplib.error_temp as serveroverload_err:
            logger.error(serveroverload_err)
            raise ConnectionError(serveroverload_err)
        except ConnectionError as conn_e:
            raise ConnectionError(conn_e)
        except TimeoutError as timeout_e:
            raise ConnectionError(timeout_e)

    def __call__(self):
        logger.info('transfer starting')
        self.run()
        return self.out
