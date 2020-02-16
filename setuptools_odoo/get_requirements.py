# -*- coding: utf-8 -*-
# Copyright © 2020 ACSONE SA/NV
# License LGPLv3 (http://www.gnu.org/licenses/lgpl-3.0-standalone.html)

from __future__ import print_function

import argparse
import ast
import os
import re
import sys

from .core import get_addon_metadata
from .manifest import is_installable_addon

# ignore odoo and odoo addons dependencies
IGNORE_RE = re.compile("^(odoo>|odoo[0-9]+-addon-)")


def get_odoo_addon_keyword(setup_py_path):
    """Get the value of the odoo_addon keyword argument in a setup.py file """
    with open(setup_py_path) as f:
        parsed = ast.parse(f.read())
        for node in ast.walk(parsed):
            if not isinstance(node, ast.Call) or node.func.attr != "setup":
                continue
            for kw in node.keywords:
                if kw.arg != "odoo_addon":
                    continue
                return ast.literal_eval(kw.value)
    return None


def get_requirements(addons_dir):
    requirements = set()
    for addon_name in os.listdir(addons_dir):
        addon_dir = os.path.join(addons_dir, addon_name)
        if not is_installable_addon(addon_dir):
            continue
        setup_py_path = os.path.join(addons_dir, "setup", addon_name, "setup.py")
        if not os.path.exists(setup_py_path):
            continue
        odoo_addon = get_odoo_addon_keyword(setup_py_path)
        if odoo_addon is None:
            continue
        if odoo_addon is True:
            odoo_addon = {}
        metadata = get_addon_metadata(
            addon_dir,
            depends_override=odoo_addon.get("depends_override"),
            external_dependencies_override=odoo_addon.get(
                "external_dependencies_override"
            ),
            odoo_version_override=odoo_addon.get("odoo_version_override"),
        )
        for install_require in metadata.get_all("Requires-Dist"):
            if IGNORE_RE.match(install_require):
                continue
            requirements.add(install_require)
    return sorted(requirements)


def main(args=None):
    parser = argparse.ArgumentParser(
        description=(
            "Print external python dependencies for all addons in an "
            "Odoo addons directory"
        )
    )
    parser.add_argument("--addons-dir", "-d", default=".")
    parser.add_argument("--output", "-o", default="-")
    args = parser.parse_args(args)
    requirements = "\n".join(get_requirements(args.addons_dir))
    if args.output == "-":
        print(requirements)
    else:
        with open(args.output, "w") as f:
            print(requirements, file=f)


if __name__ == "__main__":
    main(sys.argv[1:])
