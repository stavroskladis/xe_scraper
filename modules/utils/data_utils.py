
# Get unique values
def unique(xlist):
    unique_list = []

    for x in xlist:
        if x not in unique_list:
            unique_list.append(x)

    return unique_list


def search(url_list, keyword):
    for x in range(len(url_list)):
        if url_list[x] == keyword:
            return True
    return False


def filter_blacklisted_areas(urls, blacklisted_areas):
    # Filters based on blacklisted areas

    for url in urls:
        for area in blacklisted_areas:
            if area in url:
                urls.remove(url)
                break  # if blacklisted break the loop
    return urls
