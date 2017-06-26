""" Starcraft 2 build order, with ability to load/save to json """

import io
import json
import jsonpickle


def from_json(path):
    """ Load a BuildOrder from json """
    with open(path) as infile:
        return jsonpickle.decode(infile.read())


class BuildOrder(object):

    def __init__(self, name=None, race=None, url=None, category=None):
        self.name = name
        self.race = race
        self.url = url
        self.category = category
        # list of BuildStep
        self.steps = []

    def to_str(self):
        msg = self.name + '\n'
        msg += '\n'
        for step in self.steps:
            supply_str = str(step.supply_filled)
            if step.supply_available:
                supply_str += '/' + str(step.supply_available)
            msg += supply_str + ': ' + step.unit + '\n'
        return msg

    def to_json(self, path):
        with io.open(path, 'w', encoding='utf8') as outfile:
            # jsonpickle doesn't do pretty printing, so do it with json
            json_obj = json.loads(jsonpickle.encode(self))
            outfile.write(unicode(json.dumps(json_obj, indent=4, ensure_ascii=False)))


class BuildStep(object):

    def __init__(self, supply_filled, supply_available, unit, time=None, gameloop=None):
        # int
        self.supply_filled = int(supply_filled)
        # int
        self.supply_available = int(supply_available)
        # str
        self.unit = unit
        # str
        self.time = time
        # int
        self.gameloop = gameloop
