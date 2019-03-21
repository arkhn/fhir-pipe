import datetime
import logging
import re
from enum import Enum

# Utility functions (not callable)
from fhirpipe.scripts import patient

# Scripts specific to patients
from fhirpipe.scripts import utils


# From now on, standard scripts


def make_title(raw_input):
    return raw_input.title().strip()


def split_space(raw_input):
    return raw_input.split(" ")


def format_date_from_yyyymmdd(raw_input):
    if utils.is_empty(raw_input):
        return ""
    try:
        date = datetime.datetime.strptime(raw_input, "%Y%m%d")
        iso_date = date.isoformat()
        return iso_date
    except ValueError:
        return raw_input


def equal(raw_input):
    if raw_input is None or raw_input == "NaN":
        return ""
    return raw_input.strip()


def clean_phone(raw_input):
    pattern = re.compile("(\d{2})" + "[\.\-\s]*(\d{2})" * 4)
    occurrences = pattern.findall(raw_input)
    if len(occurrences) > 0:
        phone = " ".join(occurrences[0])
        return phone
    return ""


def if_valid(process, callback):
    """
    Behaviour:
        if given value (the col provided), process(given) is not empty
        then:
            if callback is a str or a number:
                return callback
            if callback is a function
                execute it with value and
                return the response
    """

    def if_valid_func(value):
        if not utils.is_empty(process(value)):
            if callable(callback):
                return callback(value)
            else:
                return callback
        else:
            return ""

    return if_valid_func


functions = {
    "make_title": make_title,
    "split_space": split_space,
    "format_date_from_yyyymmdd": format_date_from_yyyymmdd,
    "equal": equal,
    "clean_phone": clean_phone,
}
# Add the function declared in the specific resource files
resources = [patient]
for resource in resources:
    functions.update(resource.functions)


# Return the script if available
def get_script(name):
    if name in functions.keys():
        return functions[name]
    else:
        if name.startswith("if_valid("):
            return eval(name)
            # TODO can we implement a safety check?
            # Step: 1 extract the argument
            # Step2: if str ok, else check if in functions.keys()
        else:
            raise NameError("Function", name, "not found.")
