#!/usr/bin/env python3
import functools
import json
import logging
from threading import Thread
import sys
import time

import pika
from pika.connection import ConnectionParameters
from pika.credentials import PlainCredentials
from pika.spec import BasicProperties
from pika.channel import Channel

logger = logging.getLogger(__name__)

url = "localhost"
username = "guest"
password = "guest"

# url = 'localhost'
# username = 'guest'
# password = 'guest'

exchange_type = 'topic'
exchange = "an_exchange"
queue = "a_queue"
routing_key = "a_routing_key"


class Publisher(Thread):
    _channel: Channel

    def __init__(self):
        Thread.__init__(self, daemon=True)
        self._nacked_msgs = []
        self._last_delivered_msg_tag = 0
        self._connection = None
        self._channel = None
        self.creds = PlainCredentials(username=username, password=password)
        self.params = ConnectionParameters(credentials=self.creds,
                                           host=url,
                                           port=5672)
        self._stopping = False
        self._acks = 0
        self._nacks = 0
        self._message_number = 0
        self._deliveries = []

    def connect(self):
        try:
            return pika.SelectConnection(parameters=self.params,
                                         on_close_callback=self.on_close_callback,
                                         on_open_error_callback=self.on_open_error_callback,
                                         on_open_callback=self.on_conn_open)
        except Exception as ex:
            logger.error(ex)
            raise ex

    def run(self):
        self._connection = self.connect()
        self._connection.ioloop.start()

        while not self._stopping:
            time.sleep(5)

        # self.stop()
        if (self._connection is not None and
                not self._connection.is_closed):
            # Finish closing
            self._connection.ioloop.start()

    def on_delivery_confirm2(self, method_frame):
        confirmation_type = method_frame.method.NAME.split('.')[1].lower()
        logger.info('Received %s for delivery tag: %i' % (
            confirmation_type,
            method_frame.method.delivery_tag))
        if confirmation_type == 'ack':
            self._acks += 1
        elif confirmation_type == 'nack':
            self._nacks += 1
        self._deliveries.remove(method_frame.method.delivery_tag)
        logger.info(
            'Published %i messages, %i have yet to be confirmed, %i were '
            'acked and %i were nacked' % (
                self._message_number, len(self._deliveries),
                self._acks, self._nacks))

    def on_delivery_confirm(self, method_frame):

            m = method_frame.method
            confirmation_type = m.NAME.split('.')[1].lower()
            multiple = m.multiple
            delivery_tag = m.delivery_tag
            if multiple and delivery_tag == 0:
                num_acks = len(self._deliveries)
            else:
                num_acks = delivery_tag - self._last_delivered_msg_tag

            logger.info('Received %s %sfor delivery tag: %i',
                        confirmation_type, '*multiple* ' if multiple else '', delivery_tag)


            if confirmation_type == 'ack':
                self._acks += num_acks
            elif confirmation_type == 'nack':
                self._nacks += num_acks

            if delivery_tag == 0:

                if confirmation_type == 'nack':
                    self._nacked_msgs.extend(self._deliveries)
                self._deliveries.clear()
            else:
                for tag in range(self._last_delivered_msg_tag + 1, delivery_tag + 1):

                    if confirmation_type == 'nack':
                        self._nacked_msgs.append(tag)
                    self._deliveries.remove(tag)

            self._last_delivered_msg_tag = delivery_tag

            logger.info('Published %i messages, %i have yet to be confirmed, %i were acked and %i were nacked',
                        self._message_number, len(self._deliveries), self._acks, self._nacks)

    def on_conn_open(self, unused_connection):
        self._connection.channel(on_open_callback=self.on_chan_open)
        logger.info('created channel')

    def on_close_callback(self, connection, exception):
        # self._connection.channel(on_open_callback=self.on_chan_open)
        logger.info('connection closed, error: {}'.format(exception))

    def on_open_error_callback(self, connection, exception):
        # self._connection.channel(on_open_callback=self.on_chan_open)
        logger.info('error while opening connection, error: {}'.format(exception))

    def on_chan_open(self, channel):
        self._channel = channel
        self._channel.confirm_delivery(self.on_delivery_confirm)
        self._channel.exchange_declare(exchange,
                                       exchange_type,
                                       durable=True,
                                       callback=self.on_exchange_declareok)
        logger.info('declared exchange')

    def on_exchange_declareok(self, unused_frame):
        self._channel.queue_declare(callback=self.on_queue_declareok,
                                    queue=queue, durable=True)
        logger.info('declared queue')

    def on_queue_declareok(self, unused_frame):
        self._channel.queue_bind(callback=None, exchange=exchange,
                                 queue=queue,
                                 routing_key=routing_key)
        logger.info('bound queue')

    def pub(self, message):
        self._message_number += 1
        self._deliveries.append(self._message_number)
        props = BasicProperties(content_type='application/json',
                                content_encoding='utf-8')

        def inner_call():
            #time.sleep(0.1)
            self._channel.basic_publish(
                                        exchange=exchange,
                                        routing_key=routing_key,
                                        body=message,
                                        properties=props,
                                        mandatory=True)

        self._connection.ioloop.add_callback_threadsafe(inner_call)


def run_example():
    pub = Publisher()
    pub.start()
    print("waiting 2 seconds")
    time.sleep(2)

    times = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    for i in range(0, times):
        with open('af.json') as fo:
            message = json.dumps(json.load(fo))
        try:
            pub.pub(message)
            # time.sleep(0.001)
            # print(" [x] Sent %r:%r" % (routing_key, message))
        except Exception as e:
            print(e)

        # Keep the script running so we can wait for more confirmations...
        while True:
            pass

# run_example()
