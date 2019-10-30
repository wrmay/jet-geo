import os

import pandas as pd
from bokeh.io import curdoc
from bokeh.layouts import column
from bokeh.models import ColumnDataSource
from bokeh.models.map_plots import GMapOptions
from bokeh.plotting import gmap


DATA_DIR = 'Geolife Trajectories 1.3/Data'


def loadfile(fname):
    print("LOADING " + fname)
    return pd.read_csv(fname, skiprows=6, header=None, usecols=[0, 1, 3, 4, 5, 6],
                       names=['Latitude', 'Longitude', 'Altitude', 'Date', 'Date String', 'Time String'])
    print(df)


# for each directory, grab the first file and load it into a dataframe so we have a list of data frames
phones = []
for dirname in sorted(os.listdir(DATA_DIR)):
    phonedir = os.path.join(DATA_DIR, dirname)
    if os.path.isdir(phonedir):
        for filename in sorted(os.listdir(os.path.join(phonedir, 'Trajectory'))):
            tracefile = os.path.join(phonedir, 'Trajectory', filename)
            if tracefile.endswith('.plt'):
                phones.append(loadfile(tracefile))
                break

print('PHONES LOADED {}'.format(len(phones)))

global_row = 0
lats = [df.at[global_row, 'Latitude'] for df in phones]
longitudes = [df.at[global_row, 'Longitude'] for df in phones]

# build the map
map_options = GMapOptions(map_type='roadmap', lat=39.9042, lng=116.4074, zoom=11)
p = gmap("YOUR GOOGLE MAPS API KEY", map_options, title='Bejing')
source = ColumnDataSource({'lat': lats, 'lon': longitudes})
p.circle('lon', 'lat', color='blue', size=10, source=source)
layout = column(p)


# right now, replace everything
def update():
    global global_row
    global_row += 1
    longitude_patches = [(p, phones[p].at[global_row, 'Longitude']) for p in range(len(phones)) if len(phones[p].index) > global_row]
    latitude_patches = [(p, phones[p].at[global_row, 'Latitude']) for p in range(len(phones)) if len(phones[p].index) > global_row]
    patches = {'lon': longitude_patches, 'lat': latitude_patches}
    source.patch(patches)


curdoc().add_periodic_callback(update, 200)
curdoc().add_root(layout)
