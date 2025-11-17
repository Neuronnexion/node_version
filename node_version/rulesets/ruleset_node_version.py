#!/usr/bin/env python3

from cmk.rulesets.v1 import Label, Title
from cmk.rulesets.v1.form_specs import BooleanChoice, DefaultValue, DictElement, Dictionary, Float, LevelDirection, SimpleLevels
from cmk.rulesets.v1.rule_specs import CheckParameters, HostAndItemCondition, Topic

def _parameter_form():
    return Dictionary(
        elements = {
            "api_key": DictElement(
                parameter_form=Password(
                    title=Title("newreleases.io API key"),
                ),
                required = True,
            ),
        }
    )

rule_spec_node_version = CheckParameters(
    name = "node_version",
    title = Title("Node version parameters"),
    topic = Topic.GENERAL,
    parameter_form = _parameter_form,
    condition = HostAndItemCondition(item_title=Title("Node version parameters"))
)