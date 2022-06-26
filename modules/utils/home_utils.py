from modules.home.home_entity import Home

def make_homes(urls):
    Homes = []

    for j in range(0, len(urls)):
        Homes.append(Home(urls[j]))
        Homes[j].set_property_id()

    return Homes
    