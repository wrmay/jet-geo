import os
import threading

import hazelcast
from bokeh.io import curdoc
from bokeh.layouts import column
from bokeh.models import ColumnDataSource
from bokeh.models.map_plots import GMapOptions
from bokeh.plotting import gmap

# set up Hazelcast connection

hz_config = hazelcast.ClientConfig()
hz_config.network_config.addresses.append('member-1:5701')
hz_config.network_config.addresses.append('member-2:5701')
# retry up to 10 times, waiting 5 seconds between connection attempts
hz_config.network_config.connection_timeout = 5
hz_config.network_config.connection_attempt_limit = 10
hz_config.network_config.connection_attempt_period = 5
hz = hazelcast.HazelcastClient(hz_config)

# position map and lock
position_map = hz.get_map('ping_input')  # remote hz map

# if we eventually end up with multiple map servers this should be a distributed lock
position_change_map_lock = threading.Lock()
position_change_map = dict()  # changes accumulate in this local map

# color map and lock
color_map = hz.get_map('ping_output')  # remote hz map

# if we eventually end up with multiple map servers this should be a distributed lock
color_change_map_lock = threading.Lock()
color_change_map = dict()  # changes accumulate in this local map

# alpha change  map and lock, used to hide expired entries
alpha_change_map = dict()
alpha_change_map_lock = threading.Lock()


# add a listener to position map to place all add/update events into the changeMap
def position_listener(event):
    global position_change_map
    with position_change_map_lock:
        position_change_map[event.key] = event.value


def deleted_listener(event):
    global alpha_change_map
    with alpha_change_map_lock:
        alpha_change_map[event.key] = 0.0


position_map.add_entry_listener(include_value=True, added_func=position_listener, updated_func=position_listener,
                                expired_func=deleted_listener)


# add a listener to position map to place all add/update events into the changeMap
def color_listener(event):
    global color_change_map
    with color_change_map_lock:
        color_change_map[event.key] = event.value


color_map.add_entry_listener(include_value=True, added_func=color_listener, updated_func=color_listener)

# now retrieve all entries from the map and build a ColumnDataSource
values = [entry.loads() for entry in
          position_map.values().result()]  # apparently map.values() returns a concurrent.futures.Future

key_to_index_map = {ping['id']: i for (i, ping) in enumerate(values)}  # given a key, return its position in values

latitudes = [entry['latitude'] for entry in values]
longitudes = [entry['longitude'] for entry in values]
ids = [entry['id'] for entry in values]
colors = ['gray' for c in range(len(latitudes))]
alphas = [1.0 for a in range(len(latitudes))]
data_source = ColumnDataSource({'latitude': latitudes, 'longitude': longitudes, 'color': colors, 'alpha': alphas})

# build the map
map_options = GMapOptions(map_type='roadmap', lat=39.98, lng=116.32, zoom=10)
p = gmap(os.environ['GOOGLE_MAPS_API_KEY'], map_options, title='Bejing')
p.circle('longitude', 'latitude', color='color', size=7, fill_alpha='alpha', line_width=0, source=data_source)
layout = column(p)


def update():
    patches = dict()
    if len(position_change_map) > 0:
        with position_change_map_lock:
            entry_list = [entry for entry in [e.loads() for e in position_change_map.values()] if
                          entry['id'] in ids]  # in check is costly, can we do something better ?
            longitude_patches = [(key_to_index_map[entry["id"]], entry["longitude"]) for entry in entry_list]
            latitude_patches = [(key_to_index_map[entry["id"]], entry["latitude"]) for entry in entry_list]
            patches['longitude'] = longitude_patches
            patches['latitude'] = latitude_patches
            position_change_map.clear()

    if len(color_change_map) > 0:
        with color_change_map_lock:
            color_patches = [(key_to_index_map[k], v) for k, v in color_change_map.items() if
                             k in ids]  # in check is costly, can we do something better ?
            color_change_map.clear()

        patches['color'] = color_patches

    if len(alpha_change_map) > 0:
        with alpha_change_map_lock:
            alpha_patches = [(key_to_index_map[k], v) for k, v in alpha_change_map.items() if k in ids]
            alpha_change_map.clear()

        patches['alpha'] = alpha_patches

    if len(patches) > 0:
        data_source.patch(patches)


curdoc().add_periodic_callback(update, 500)
curdoc().add_root(layout)
