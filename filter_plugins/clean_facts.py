#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright:
#   2020 P. H. <github.com/perfide>
# License:
#   BSD-2-Clause (BSD 2-Clause "Simplified" License)
#   https://spdx.org/licenses/BSD-2-Clause.html

"""Ansible filter plugin to remove dynamic values from ansible_facts"""

FACTS_TO_CLEAN = {
    '_facts_gathered': None,
    'ansible_local': None,
    'date_time':
        {
            'date': None,
            'day': None,
            'epoch': None,
            'hour': None,
            'iso8601': None,
            'iso8601_basic': None,
            'iso8601_basic_short': None,
            'iso8601_micro': None,
            'minute': None,
            'month': None,
            'second': None,
            'time': None,
            'weekday': None,
            'weekday_number': None,
            'weeknumber': None,
            'year': None,
        },
    'env':
        {
            'PWD': None,
            'SUDO_COMMAND': None,
            'SUDO_GID': None,
            'SUDO_UID': None,
            'SUDO_USER': None,
        },
    'memfree_mb': None,
    'memory_mb':
        {
            'nocache': {
                'free': None,
                'used': None,
            },
            'real': {
                'free': None,
                'used': None,
            },
        },
    'uptime_seconds': None,
}

REMOVE_FROM_MOUNT = [
    'block_available',
    'block_used',
    'inode_available',
    'inode_used',
    'size_available',
]


def clean_dict(original_facts: dict, facts_to_clean: dict) -> dict:
    """Recursive dict cleanup

    Args:
        original_facts: the dict which needs cleanup
        facts_to_clean: the dict which defines keys to delete

    Returns:
        cleaned dict

    """
    for key in original_facts.copy():
        if key in facts_to_clean:
            is_dict_orig = isinstance(original_facts[key], dict)
            is_dict_clean = isinstance(facts_to_clean[key], dict)
            if facts_to_clean[key] is None:
                del original_facts[key]
            elif is_dict_orig and is_dict_clean:
                original_facts[key] = clean_dict(
                    original_facts[key], facts_to_clean[key]
                )
                if not original_facts[key]:
                    del original_facts[key]
            else:
                raise KeyError(
                    'incompatible structure in {}: {} vs. {}'.format(
                        key, original_facts[key], facts_to_clean[key]
                    )
                )
    return original_facts


def clean_facts(facts: dict) -> dict:
    """Remove dynamic items fron facts

    Args:
        facts: the content of the `ansible_facts` variable

    Returns:
        facts without dynamic values

    """
    facts = clean_dict(facts, FACTS_TO_CLEAN)
    for mount in facts['mounts']:
        for key in REMOVE_FROM_MOUNT:
            del mount[key]
    return facts


class FilterModule:  # pylint: disable=R0903
    """A class used by ansible to load filters"""
    def filters(self) -> dict:  # pylint: disable=R0201
        """A method to gather filter names and functions"""
        return {'clean_facts': clean_facts}


# [EOF]
