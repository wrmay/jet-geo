import bokeh.io
import bokeh.layouts
import bokeh.models
import bokeh.plotting
import random

COUNT = 1000


def color(dist):
    """return a color given a distance"""
    if dist < 20:
        return 'indigo'
    elif dist < 40:
        return 'blue'
    elif dist < 60:
        return 'yellow'
    elif dist < 80:
        return 'orange'
    else:
        return 'red'


random.seed()

x_coordinates = [random.gauss(100, 20) for i in range(COUNT)]
y_coordinates = [random.gauss(100, 20) for i in range(COUNT)]
coordinates = zip(x_coordinates, y_coordinates)
distances = [((x - 100) ** 2 + (y - 100) ** 2) ** 0.5 for (x, y) in coordinates]
colors = [color(d) for d in distances]
cds = bokeh.models.ColumnDataSource({'x': x_coordinates, 'y': y_coordinates, 'c': colors})

figure = bokeh.plotting.figure()
figure.circle('x', 'y', fill_color='c', radius=1, source=cds)


def update():
    global x_coordinates, y_coordinates, cds
    for i in range(COUNT):
        x_coordinates[i] += random.uniform(-1, 1)
        y_coordinates[i] += random.uniform(-1, 1)

    z = zip(x_coordinates, y_coordinates)
    dist = [((x - 100) ** 2 + (y - 100) ** 2) ** 0.5 for (x, y) in z]
    c = [color(d) for d in dist]
    cds.data = {'x': x_coordinates, 'y': y_coordinates, 'c': c}


bokeh.io.curdoc().add_periodic_callback(update, 100)
bokeh.io.curdoc().add_root(bokeh.layouts.column(figure))
