#!/usr/bin/python

from AQPonicsServer import AQPServer
import os
import grp
import signal
import daemon
import lockfile


def data_handler():
	return "OK!"


def main_program():
    # 'Main' program for AQPonicsServer, which will run as a daemon
    server = AQPServer()
    server.serve_requests()


if __name__ == '__main__':
    #with daemon.DaemonContext():
    main_program()
