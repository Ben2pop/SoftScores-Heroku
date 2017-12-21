# -*- coding: utf-8 -*-

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

import os

from django.core.management import call_command
from future import standard_library
from survey.tests.management.test_management import TestManagement

standard_library.install_aliases()


class TestGenerateTexConfiguration(TestManagement):

    def assert_command_create_file(self, arg=None, value=None):
        file = "output"
        call_command("generate_tex_configuration", file, arg, value)
        self.assertTrue(os.path.exists(file))
        if os.path.exists(file):
            os.remove(file)

    def test_handle(self):
        self.assert_command_create_file()
        self.assert_command_create_file("--survey-name", "Test survëy")
        self.assert_command_create_file("--survey-id", 1)

    def test_error_message(self):
        self.assertRaises(ValueError, call_command,
                          "generate_tex_configuration", "output",
                          "--survey-id", 25)
        self.assertRaises(ValueError, call_command,
                          "generate_tex_configuration", "output",
                          "--survey-name", "Do not exists")
