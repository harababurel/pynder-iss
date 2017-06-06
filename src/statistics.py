from collections import defaultdict

def generate_age_statistics(hopefuls):
    data = {
        'male': {
            'count': 0,
            'age': defaultdict(int),
            'distance': defaultdict(int),
        },
        'female': {
            'count': 0,
            'age': defaultdict(int),
            'distance': defaultdict(int),
        },
        'ages': [],
        'distances': [],
    }

    data['ages'] = sorted(list(set([x.age for x in hopefuls])))
    data['distances'] = sorted(list(set([round(x.distance_km) for x in hopefuls])))

    for gender in ['male', 'female']:
        data[gender]['count'] = len(
            [x for x in hopefuls if x.gender == gender])

    for x in hopefuls:
        data[x.gender]['age'][x.age] += 1
        data[x.gender]['distance'][round(x.distance_km)] += 1

    # make sure there are no missing points in the line


    for gender in ['female', 'male']:
        for age in data['ages']:
            if age not in data[gender]['age']:
                data[gender]['age'][age] = 0

        for distance in data['distances']:
            if distance not in data[gender]['distance']:
                data[gender]['distance'][distance] = 0

    return data
