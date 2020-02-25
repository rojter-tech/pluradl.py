# -*- coding: utf-8 -*-
from __future__ import unicode_literals

"""
certifi.py
~~~~~~~~~~

This module returns the installation location of cacert.pem.
"""
import os


def where():
    f = os.path.dirname(__file__)

    return os.path.join(f, 'cacert.pem')
