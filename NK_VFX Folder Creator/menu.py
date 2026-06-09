import sys
import nuke

_VARIANT = "./cp{}{}".format(sys.version_info[0], sys.version_info[1])
nuke.pluginAddPath(_VARIANT)
