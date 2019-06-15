# -*- coding: utf-8 -*-
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "supervisor.settings")
django.setup()

from report.models import Ticket
import pandas as pd
import configparser
from supervisor_report import Report


script_path = os.path.dirname(os.path.realpath(__file__))
main_path = os.path.dirname(script_path)
config = configparser.ConfigParser()
config.read(os.path.join(main_path, 'settings.ini'))

REPORT_FILENAME = config['REPORT']['REPORT_FILENAME']
report = Report(os.path.join(main_path, REPORT_FILENAME), sep=';', decimal=',')

report.df = report.df.replace(pd.np.nan, None, regex=True)
print(report.df.keys())
for idx, row in report.df.iterrows():
    ticket, created = Ticket.objects.get_or_create(tn=row.tn, tid=row.tid)
    if created:
        for key in row.keys():
            if key in ticket.__dict__:
                ticket.__setattr__(key, row.__getattr__(key))
        ticket.save()
