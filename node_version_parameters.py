from cmk.gui.i18n import _
from cmk.gui.valuespec import (
    Dictionary,
    Percentage,
    TextInput,
    Tuple,
)
from cmk.gui.plugins.wato.utils import (
    CheckParameterRulespecWithItem,
    rulespec_registry,
    RulespecGroupCheckParametersApplications,
)

def _parameter_valuespec_node_version():
    return Dictionary(
        elements = [
            ("api_key",
            Password(
                title=_("newreleases.io API key"),
                allow_empty=False,
            ),),
        ],
    )

rulespec_registry.register(
    CheckParameterRulespecWithItem(
        check_group_name = "node_version",
        group = RulespecGroupCheckParametersApplications,
        match_type = "dict",
        parameter_valuespec = _parameter_valuespec_node_version,
        title = lambda: _("Node version parameters"),
    )
)