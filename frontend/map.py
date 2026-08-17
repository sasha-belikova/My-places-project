import folium
from backend.borders import countries_borders, show_cities
from folium.plugins import MiniMap



def build_map(user_id):
    m = folium.Map(
        location=[0, 0],
        zoom_start=3,
        min_zoom=3,
        max_zoom=18,
        max_bounds=True,
        min_lat=-90,
        max_lat=90,
        min_lon=-180,
        max_lon=180,
        tiles="cartodb positron")

    c = countries_borders(user_id)
    fg = folium.FeatureGroup(name="Visited countries", show=False).add_to(m)
    countries_layer_name = fg.get_name()
    c.add_to(fg)

    p = show_cities(user_id)
    ft = folium.FeatureGroup(name="Visited cities", show=False).add_to(m)
    city_layer_name = ft.get_name()
    for city, coordinates in p.items():
        folium.Marker(location = coordinates, popup = city, icon=folium.Icon(icon='star', color='purple')).add_to(ft)

    MiniMap().add_to(m)
    folium.LayerControl().add_to(m)
    return m, countries_layer_name, city_layer_name


def noId_build_map():
    n = folium.Map(
            location=[0, 0],
            zoom_start=3,
            min_zoom=3,
            max_zoom=18,
            max_bounds=True,
            min_lat=-90,
            max_lat=90,
            min_lon=-180,
            max_lon=180,
            tiles="cartodb positron")
    MiniMap().add_to(n)
    folium.LayerControl().add_to(n)
    return n



