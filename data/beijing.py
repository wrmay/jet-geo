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

changeMap = dict()
pingMap = hz.get_map('pings')
map_lock = threading.Lock()


# add a listener to ping map to place all add/update events into the changeMap
def map_listener(event):
    global changeMap
    with map_lock:
        changeMap[event.key] = event.value


pingMap.add_entry_listener(include_value=True, added_func=map_listener, updated_func=map_listener)

# now retrieve all entries from the map and build a ColumnDataSource
values = [entry.loads() for entry in pingMap.values().result()]  # apparently map.values() returns a concurrent.futures.Future
latitudes = [entry['latitude'] for entry in values]
longitudes = [entry['longitude'] for entry in values]
data_source = ColumnDataSource({'latitude': latitudes, 'longitude': longitudes})
print('DATA SOURCE HAS {0}/{1} LATITUDES/LONGITUDES'.format(len(latitudes), len(longitudes)))

# build the map
map_options = GMapOptions(map_type='roadmap', lat=39.98, lng=116.32, zoom=14)
# map_options = GMapOptions(map_type='roadmap', lat=39.9042, lng=116.4074, zoom=11)
p = gmap("GOOGLE MAPS API KEY", map_options, title='Bejing')
p.circle('longitude', 'latitude', color='blue', size=10, source=data_source)
layout = column(p)


def update():
    with map_lock:
        entry_list = [entry.loads() for entry in changeMap.values()]
        longitude_patches = [(entry["id"], entry["longitude"]) for entry in  entry_list]
        latitude_patches = [(entry["id"], entry["latitude"]) for entry in entry_list]
        patches = {'longitude': longitude_patches, 'latitude': latitude_patches}
        changeMap.clear()

    data_source.patch(patches)


curdoc().add_periodic_callback(update, 200)
curdoc().add_root(layout)
