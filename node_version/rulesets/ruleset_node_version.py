#!/usr/bin/env python3

from cmk.rulesets.v1 import Title
from cmk.rulesets.v1.form_specs import (
    DictElement,
    Dictionary,
    Password,
    validators,
)
from cmk.rulesets.v1.rule_specs import CheckParameters, HostCondition, Topic

def _parameter_valuespec_node_version():
    return Dictionary(
        elements={
            "api_key": DictElement(
                required=False,
                parameter_form=Password(
                    title=Title("newreleases.io API key"),
                    custom_validate=(validators.LengthInRange(min_value=1),),
                ),
            )
        }
    )

rule_spec_node_version = CheckParameters(
    name = "node_version",
    title = Title("Node version parameters"),
    topic = Topic.GENERAL,
    parameter_form = _parameter_valuespec_node_version,
    condition = HostAndItemCondition(item_title=Title("Node version parameters"))
)