# -*- coding: utf-8 -*-

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

from builtins import open, str

from future import standard_library
from survey.exporter.tex import ConfigurationBuilder
from survey.management.survey_command import SurveyCommand

standard_library.install_aliases()


class Command(SurveyCommand):

    """
        See the "help" var.
    """

    help = u"""This command permit to generate the latex configuration in order
    to manage the survey report generation. """

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument('output', nargs='+', type=str, help='Output file.')

    def handle(self, *args, **options):
        super(Command, self).handle(*args, **options)
        output = options["output"][0]
        if self.survey is None:
            conf = ConfigurationBuilder()
        else:
            conf = ConfigurationBuilder(self.survey)
        file_ = open(output, "w")
        file_.write(str(conf))
        file_.close()
