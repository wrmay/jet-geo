import hazelcast
import threading

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
position_map_lock = threading.Lock()  # if we eventually end up with multiple map servers this should be a distributed lock
position_change_map = dict()  # changes accumulate in this local map

# color map and lock
color_map = hz.get_map('ping_output')  # remote hz map
color_map_lock = threading.Lock()  # if we eventually end up with multiple map servers this should be a distributed lock
color_change_map = dict()  # changes accumulate in this local map


# add a listener to position map to place all add/update events into the changeMap
def position_listener(event):
    global position_change_map
    with position_map_lock:
        position_change_map[event.key] = event.value


position_map.add_entry_listener(include_value=True, added_func=position_listener, updated_func=position_listener)


# add a listener to position map to place all add/update events into the changeMap
def color_listener(event):
    global color_change_map
    with color_map_lock:
        color_change_map[event.key] = event.value


color_map.add_entry_listener(include_value=True, added_func=color_listener, updated_func=color_listener)

# now retrieve all entries from the map and build a ColumnDataSource
values = [entry.loads() for entry in
          position_map.values().result()]  # apparently map.values() returns a concurrent.futures.Future
latitudes = [entry['latitude'] for entry in values]
longitudes = [entry['longitude'] for entry in values]
ids = [entry['id'] for entry in values]
colors = ['gray' for c in range(len(latitudes))]
data_source = ColumnDataSource({'latitude': latitudes, 'longitude': longitudes, 'color': colors})

# build the map
map_options = GMapOptions(map_type='roadmap', lat=39.98, lng=116.32, zoom=10)
p = gmap("YOUR GOOGLE MAPS API KEY", map_options, title='Bejing')
p.circle('longitude', 'latitude', color='color', size=10, source=data_source)
layout = column(p)


def update():
    with position_map_lock:
        entry_list = [entry for entry in [e.loads() for e in position_change_map.values()] if
                      entry['id'] in ids]  # in check is costly, can we do something better ?
        longitude_patches = [(entry["id"], entry["longitude"]) for entry in entry_list]
        latitude_patches = [(entry["id"], entry["latitude"]) for entry in entry_list]
        patches = {'longitude': longitude_patches, 'latitude': latitude_patches}
        position_change_map.clear()

    data_source.patch(patches)

    if len(color_change_map) > 0:
        with color_map_lock:
            color_patches = [(k, v) for k, v in color_change_map.items() if
                             k in ids]  # in check is costly, can we do something better ?
            color_change_map.clear()

        print('PATCH COLORS {0}'.format(color_patches))
        data_source.patch({'color': color_patches})


curdoc().add_periodic_callback(update, 500)
curdoc().add_root(layout)
