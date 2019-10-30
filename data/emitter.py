import hazelcast
import os
import time

import pandas as pd

from hazelcast.core import HazelcastJsonValue

DATA_DIR = '/opt/project/data/Geolife Trajectories 1.3/Data'
traces = []
trace_count = 0
ping_count = 0

COUNT = 100
PING_INTERVAL_MS = 5000


class Traces:
    def __init__(self, dir_name):
        self.dir_name = dir_name
        self.file_names = sorted([file_name for file_name in os.listdir(os.path.join(dir_name, 'Trajectory')) if
                                  file_name.endswith('.plt') and os.path.exists(
                                      os.path.join(dir_name, 'Trajectory', file_name))])
        self.next_file = -1

    def next(self):
        self.next_file += 1
        df = Traces.loadfile(
            os.path.join(self.dir_name, 'Trajectory', self.file_names[self.next_file % len(self.file_names)]))
        return Trace(df)

    def loadfile(fname):
        return pd.read_csv(fname, skiprows=6, header=None, usecols=[0, 1, 3, 4, 5, 6],
                           names=['Latitude', 'Longitude', 'Altitude', 'Date', 'Date String', 'Time String'])


class Trace:
    def __init__(self, df):
        self.data = df
        self.curr_item = -1
        self.increment = 1

    def next(self):
        self.curr_item += self.increment
        if self.curr_item == len(self.data.index):
            self.curr_item -= 1
            self.increment = -1
        elif self.curr_item < 0:
            self.curr_item += 1
            self.increment = 1

        row = self.data.iloc[self.curr_item]
        return {'latitude': row['Latitude'], 'longitude': row['Longitude']}


def setup():
    # make a (ordered) list of dirs and with each dir, keep an iterator over .plt files (ordered)
    # to get the next file, go to the next dir and get the next file, if there is no next file,
    # reset the iterator and carry on.
    result = dict()

    trace_dirs = sorted([os.path.join(DATA_DIR, dir_name) for dir_name in os.listdir(DATA_DIR) if
                         os.path.isdir(os.path.join(DATA_DIR, dir_name))])
    traces_list = [Traces(d) for d in trace_dirs]

    for i in range(COUNT):
        result[i] = traces_list[i % len(traces_list)].next()

    return result


if __name__ == '__main__':
    config = hazelcast.ClientConfig()
    config.network_config.addresses.append('member-1:5701')
    config.network_config.addresses.append('member-2:5701')
    # retry up to 10 times, waiting 5 seconds between connection attempts
    config.network_config.connection_timeout = 5
    config.network_config.connection_attempt_limit = 10
    config.network_config.connection_attempt_period = 5
    hz = hazelcast.HazelcastClient(config)
    map = hz.get_map('pings').blocking()

    # returns a map of traces
    traces = setup()

    # in a loop, emit the next lat/long in the trace - emit one item each, every 5 seconds
    # Allow 1 ms for emitting each one.  There are 5000ms in which to emit 100 entries so
    # wait approximately 4900 / 100 = 49ms before  each.
    wait_ms = (PING_INTERVAL_MS - COUNT) / COUNT
    next_wakeup = (time.time_ns() / 1000000) + PING_INTERVAL_MS
    while True:
        for key, val in traces.items():
            time.sleep(wait_ms / 1000)
            coordinate = val.next()
            coordinate['id'] = key
            map.put(key, HazelcastJsonValue(coordinate))
            #print('item {0} at {1},{2}'.format(key, coordinate['latitude'], coordinate['longitude']))

        # sleep an additional amount of time if necessary to stay on schedule
        now_ms = time.time_ns() / 1000000
        if now_ms < next_wakeup:
            sleep_time = (next_wakeup - now_ms) / 1000
            next_wakeup += PING_INTERVAL_MS
            time.sleep(sleep_time)
