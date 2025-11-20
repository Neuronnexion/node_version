#!/usr/bin/env python3

import json
import os.path
import time

import requests
from cmk.agent_based.v2 import (
    Result,
    Service,
    State,
)
from requests.auth import HTTPBasicAuth

# global variable for the cache location
loc_cache = "/omd/sites/monitoring/tmp/check_mk/cache/node_version"


# use the newreleases.io API to get a list of all node versions of node, sort it to get the latest major versions and store it in a cached file
def api_call(api_key):
    page = 1
    node_dict = dict()
    sorted_node_dict = dict()
    # get all the node versions page by page
    while True:
        response = requests.get(
            "https://api.newreleases.io/v1/projects/github/nodejs/node/releases",
            auth=HTTPBasicAuth(api_key, ""),
            params={"page": page},
        )
        node_dict.update(response.json())
        # sort the page results in a dict
        sorted_node_dict = sort_dict(node_dict, sorted_node_dict)
        page += 1
        # stop the loop when the last page is reached or when the API doesn't return OK anymore, to avoid request spamming
        if response.status_code != 200 or page == 45:
            break
    # only update the cache if all the pages have been reached
    if response.status_code == 200:
        with open(loc_cache, "w") as file:
            file.write(json.dumps(sorted_node_dict))
    return response.status_code


# compare the cache's last modification date to a fixed time value
def is_cache_old():
    # create the cache if it doesn't exist
    if not os.path.exists(loc_cache):
        return True
    else:
        # 6 hours
        interval = 21600
        # if the cache's last modification date is greater than value, return true
        if (int(time.time()) - int(os.path.getmtime(loc_cache))) >= interval:
            return True
        else:
            return False


# extract the latest versions for all major versions listed in the json retrived with the newreleases api, and put then in a sorted dict
def sort_dict(node_dict, sorted_node_dict):
    for i in range(0, len(node_dict["releases"])):
        # get the major version for each version number (ie for "v20.7.2", get "v20")
        version_short = str(node_dict["releases"][i]["version"].split(".")[0])
        # check sorted_node_dict is empty
        if sorted_node_dict:
            # if a major version isn't present in the sorted dict, put the current dict line in here
            if version_short not in sorted_node_dict:
                sorted_node_dict.update({version_short: node_dict["releases"][i]})
            # if a major version is in the sorted dict, but the full version number is lesser than version number in the current dict line,
            # remove that dict line and replace it by the current dict line
            else:
                version_current = int(
                    node_dict["releases"][i]["version"].replace(".", "")[1:]
                )
                version_sorted = int(
                    sorted_node_dict[version_short]["version"].replace(".", "")[1:]
                )
                if version_current > version_sorted:
                    sorted_node_dict.pop(version_short)
                    sorted_node_dict.update({version_short: node_dict["releases"][i]})
        else:
            sorted_node_dict = {version_short: node_dict["releases"][i]}
    return sorted_node_dict


# parse function
def parse_node_version(string_table):
    parsed = {}
    for line in string_table:
        parsed[line[0]] = {line[1]}
    return parsed


# discover function
def discover_node_version(section):
    for group in section:
        yield Service(item=group)


# check function
def check_node_version(item, params, section):
    api_key = params["api_key"]
    host_version = section.get(item)
    if not host_version:
        yield Result(state=State.UNKNOWN, summary="Node isn't intalled on this host!")
        return

    # only call the api_call function if the cache is outdated
    if is_cache_old():
        status_code = api_call(api_key)
        # print the error number and exit if the call failed
        if status_code != 200:
            yield Result(
                state=State.UNKNOWN, summary=f"Error {status_code} during API call"
            )
            return

    # extract the major version
    version_short = list(host_version)[0].split(".")[0]

    # load the cache file into a dict var
    with open(loc_cache, "r") as file:
        cache_version = json.loads(file.read())

    # put all the CVEs in a list to print in the service summary
    if "cve" in cache_version[version_short]:
        list_cve = list()
        for value in cache_version[version_short]["cve"]:
            list_cve.append(
                value
                + ", https://cve.mitre.org/cgi-bin/cvename.cgi?name="
                + value
                + " "
            )

    # handling of service states
    if version_short in cache_version:
        if cache_version[version_short]["version"] != list(host_version)[0]:
            if "cve" in cache_version[version_short]:
                yield Result(
                    state=State.CRIT,
                    summary=f"Your current node version contains known vulnerabilities: {list_cve}. Update to version {cache_version[version_short]['version']}. Current node version: {list(host_version)[0]}",
                )
            else:
                yield Result(
                    state=State.WARN,
                    summary=f"Your current node version is outdated. Update to version {cache_version[version_short]['version']}. Current node version: {list(host_version)[0]}",
                )
        else:
            yield Result(
                state=State.OK,
                summary=f"This version is up to date. Current node version: {list(host_version)[0]}.",
            )
    else:
        yield Result(
            state=State.UNKNOWN, summary=f"This version does not exist in the cache."
        )


register.agent_section(
    name="node_version",
    parse_function=parse_node_version,
)

register.check_plugin(
    name="node_version",
    sections=["node_version"],
    service_name="Node version %s",
    discovery_function=discover_node_version,
    check_function=check_node_version,
    check_default_parameters={},
    check_ruleset_name="node_version",
)
