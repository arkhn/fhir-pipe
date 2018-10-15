import datetime
import logging
from enum import Enum

from arkhn.scripts import utils


class Gender(Enum):
    MALE = 'male'
    FEMALE = 'female'
    UNKNOWN = 'unknown'


class Deceased(Enum):
    ALIVE = False
    DEAD = True


class FamilySituation(Enum):
    MARRIED = 'Marié(e)'
    SINGLE = 'Célibataire'
    WIDOWED = 'Veuvage'
    DIVORCED = 'Divorcé(e)'


def map_gender(raw_input):
    mapping = {
        'M': Gender.MALE.value,
        'F': Gender.FEMALE.value
    }
    if raw_input in mapping.keys():
        return mapping[raw_input]
    else:
        return Gender.UNKNOWN.value


def map_deceased(raw_input):
    mapping = {
        'O': Deceased.DEAD.value,
        'N': Deceased.ALIVE.value
    }
    return mapping[raw_input]


def process_address(raw_input):
    if raw_input is None:
        return None
    # TODO: Process: add coma, R->RUE, etc.
    return raw_input


def merge_insee(value1, value2):
    if not utils.is_empty(value1):
        return value1
    else:
        return value2


def family_situation(code):
    status = FamilySituation
    mapping = {
        'M': status.MARRIED.value,
        'C': status.SINGLE.value,
        'V': status.WIDOWED.value,
        'D': status.DIVORCED.value
    }
    if code in mapping.keys():
        return mapping[code]
    else:
        logging.warning('In {}, args {} not recognised'.format('family_situation', code))
        return code

functions = {
    'map_gender': map_gender,
    'map_deceased': map_deceased,
    'process_address': process_address,
    'merge_insee': merge_insee,
    'family_situation': family_situation
}
