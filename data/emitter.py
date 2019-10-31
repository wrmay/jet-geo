import hazelcast
import os
import time

import pandas as pd

from hazelcast.core import HazelcastJsonValue

DATA_DIR = '/opt/project/data/Geolife Trajectories 1.3/Data'
traces = []
trace_count = 0
ping_count = 0

COUNT = 500


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
        self.curr_item = 0
        self.start_of_trace = df.at[0, 'Date'] * 3600 * 24

    def next(self, elapsed):
        """
        returns a list of all items happened before the given elapsed time and have not yet been returned
        raises a StopIteration exception if all items have already been returned.  May return an empty list

        self.curr_item always points to the first item that has not been returned
        """
        if self.curr_item >= len(self.data.index):
            raise StopIteration

        sim_time = self.start_of_trace + elapsed
        result = []
        while self.curr_item < len(self.data.index) and self.data.at[self.curr_item, 'Date'] * 3600 * 24 < sim_time:
            row = self.data.iloc[self.curr_item]
            result.append(
                {'latitude': row['Latitude'], 'longitude': row['Longitude'], 'time': row['Date'] * 3600 * 24 - self.start_of_trace})
            self.curr_item += 1

        return result


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
    location_map = hz.get_map('pings').blocking()

    # returns a map of traces
    traces = setup()

    # every 5 seconds, advance the simulation time 5s and for every trace, emit all of the pings that happened before
    # the new simulation time
    start_of_simulation = time.time()
    next_wakeup = start_of_simulation + 5
    while len(traces) > 0:
        sleep_time = next_wakeup - time.time()
        next_wakeup += 5
        if sleep_time > 0:
            time.sleep(sleep_time)

        simulation_time = time.time() - start_of_simulation
        print('simulation time={0}'.format(simulation_time))
        delete_list = []
        for key, val in traces.items():
            try:
                pings = val.next(simulation_time)
                # consider changing this to putAll
                for ping in pings:
                    ping['id'] = key
                    location_map.put(key, HazelcastJsonValue(ping))
                    print('item {0} t={3} at {1},{2}'.format(key, ping['latitude'], ping['longitude'], ping['time']))
            except StopIteration:
                delete_list.append(key)
                print('Trace {0} finished. {1} traces remain active.'.format(key, len(traces) - len(delete_list)))

        for key in delete_list:
            del traces[key]