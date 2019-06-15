import pandas as pd
import configparser
from datetime import datetime
from working_time import RegularWorkingTime
from pandas import ExcelWriter


class Report:
    def __init__(self, filename, **kwargs):
        if 'sep' in kwargs:
            if 'decimal' in kwargs:
                self.df = pd.read_csv(filename, sep=kwargs['sep'], decimal=kwargs['decimal'])
            else:
                self.df = pd.read_csv(filename, sep=kwargs['sep'])
        else:
            self.df = pd.read_csv(filename)

    def get_new_tickets_hour(self):
        new_tickets_hour = []
        new_tickets = self.df[self.df['ticket_state_name'] == 'new']
        for idx, row in new_tickets.iterrows():
            delta = RegularWorkingTime().compute_working_time(row['tcreatetime'], datetime.now())
            if delta > 1:
                new_tickets_hour.append(row)
        return pd.DataFrame(new_tickets_hour)

    def get_new_tickets_after_first_line(self, max_time=1):
        tickets = []
        new_tickets = self.df[self.df['ticket_state_name'] == 'new']
        for idx, row in new_tickets.iterrows():
            delta = RegularWorkingTime().compute_working_time(row['tcreatetime'], datetime.now())
            if delta > max_time and not pd.isnull(row['in_working_first'])\
               and not pd.isnull(row['first_line_emergence_time'])\
               and row['first_line_emergence_time'] != '':
                tickets.append(row)
        return pd.DataFrame(tickets)

    def get_risk_tickets(self, max_time, threshold=1):
        open_risk_tickets = []
        open_tickets = self.df[self.df['ticket_state_name'] == 'open']
        for idx, row in open_tickets.iterrows():
            delta = RegularWorkingTime().compute_working_time(row['tcreatetime'], datetime.now())
            if max_time - threshold < delta < max_time:
                open_risk_tickets.append(row)
        return pd.DataFrame(open_risk_tickets)

    def get_floating_tickets(self):
        return self.df[self.df['moved_count'] >= 2]


def save_xls(list_dfs, xls_path):
    with ExcelWriter(xls_path) as writer:
        for n, df in enumerate(list_dfs):
            df.to_excel(writer, 'sheet%s' % n)
        writer.save()


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('settings.ini')
    REPORT_FILENAME = config['REPORT']['REPORT_FILENAME']
    report = Report(REPORT_FILENAME, sep=';', decimal=',')
    new_tickets_after_first_line = report.get_new_tickets_after_first_line()
    risk_tickets = report.get_risk_tickets(8)
    floating_tickets = report.get_floating_tickets()
    save_xls([report.df, new_tickets_after_first_line, risk_tickets, floating_tickets],
             r'C:\вся инфа\sql-otrs\reports\report.xlsx')
