# -*- coding: utf-8 -*-
# Copyright © 2020 ACSONE SA/NV
# License LGPLv3 (http://www.gnu.org/licenses/lgpl-3.0-standalone.html)

import os
import shutil

from setuptools_odoo import get_requirements, make_default_setup

from . import DATA_DIR


def test_get_requirements(tmp_path):
    generated_dir = os.path.join(DATA_DIR, "setup")
    make_default_setup.main(["--addons-dir", DATA_DIR, "-f"])
    try:
        reqs_path = tmp_path / "reqs.txt"
        get_requirements.main(["--addons-dir", DATA_DIR, "-o", str(reqs_path)])
        assert reqs_path.read_text() == "astropy\npython-dateutil\n"
    finally:
        shutil.rmtree(generated_dir)
