from collections import defaultdict
import repository

class StatisticsGenerator:

    @staticmethod
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
        data['distances'] = sorted(
            list(set([round(x.distance_km) for x in hopefuls])))

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

    @staticmethod
    def generate_vote_statistics(profile):
        given = list(repository.RepoVote.get_all_of_voter(profile.id))
        received = list(repository.RepoVote.get_all_of_hopeful(profile.id))

        fields = ["dislike", "like", "superlike"]

        data = {
            'given': {
                'total': 0
            },
            'received': {
                'total': 0
            }
        }

        for key in fields:
            data['given'][key] = len(
                list(filter(lambda e: e.value == key, given)))
            data['received'][key] = len(
                list(filter(lambda e: e.value == key, received)))
            data['given']['total'] += data['given'][key]
            data['received']['total'] += data['received'][key]

        return data
