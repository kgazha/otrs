import pandas as pd
import os
import configparser
from datetime import datetime
from working_time import RegularWorkingTime
import xlwt


class Report:
    types = ['Все заявки',
             'Новые, не взятые в течение часа',
             'Время выполн. подходит к концу',
             'Заявки, сменившие очередь',
             'Просроченные']
    columns = {
        'tn': 'Номер заявки',
        'tcreatetime': 'Дата и время регистрации обращения',
        'service_name': 'Сервис, подсервис',
        'user_name': 'Владелец',
        'ticket_state_name': 'Статус',
        'queue_name': 'Очередь',
        'artsubject': 'Тема',
        'artbody': 'Текст обращения',
        'note': 'Заметка',
        'auto_close': 'Дата и время постановки обращения на автозакрытие',
        'closed': 'Дата и время закрытия заявки',
        'moved_count': 'Число смены очередей',
        'first_line_emergence_time': 'Дата и время появления на первой линии',
        'first_move_or_lock_time': 'Время первого перемещения или блокировки первой линии',
        'others_line_emergence_time': 'Время появления на второй линии',
        'others_line_lock_time': 'Время первого действия со стороны второй линии',
        'others_line_message_time': 'Время ответа другой линии',
        'auto_closed': 'Сколько прошло до постановки на автозакрытие заявки',
        'forced_close': 'Сколько прошло до решения заявки',
        'in_working_first': 'Время работы первой линии',
        'in_working_others': 'Время первой реакции второй линии'
    }

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

    def get_overdue_tickets(self, max_time):
        open_overdue_tickets = []
        open_tickets = self.df[self.df['ticket_state_name'] == 'open']
        for idx, row in open_tickets.iterrows():
            delta = RegularWorkingTime().compute_working_time(row['tcreatetime'], datetime.now())
            if delta >= max_time:
                open_overdue_tickets.append(row)
        return pd.DataFrame(open_overdue_tickets)

    def get_floating_tickets(self):
        return self.df[self.df['moved_count'] >= 2]


def save_xls(list_dfs, destination, filename):
    book = xlwt.Workbook(encoding="ansi")
    header_style = xlwt.Style.easyxf("align: wrap on, horiz center, vert center; font: bold on; borders: bottom dashed")
    style = xlwt.Style.easyxf("align: wrap on, horiz left, vert top")
    for n, df in enumerate(list_dfs):
        sheet = book.add_sheet(Report.types[n])
        sheet.set_panes_frozen(True)
        sheet.set_horz_split_pos(1)
        sheet.set_vert_split_pos(1)
        for idx, (n_row, row) in enumerate(df.iterrows()):
            if idx == 0:
                sheet_row = sheet.row(idx)
                for index, key in enumerate(Report.columns.keys()):
                    sheet.col(index).width = 5000
                    sheet_row.write(index, Report.columns[key], header_style)
            sheet_row = sheet.row(idx + 1)
            sheet_row.height_mismatch = True
            for index, key in enumerate(Report.columns.keys()):
                if not row[key] or pd.isnull(row[key]) or pd.isna(row[key]):
                    continue
                sheet_row.write(index, row[key], style)
    book.save(os.path.join(destination, filename))
    # writer = pd.ExcelWriter(xls_path, engine='xlsxwriter', options={'strings_to_urls': False})
    # for n, df in enumerate(list_dfs):
    #     df.to_excel(writer, 'sheet%s' % n)
    # writer.save()


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('settings.ini')
    REPORT_FILENAME = config['REPORT']['REPORT_FILENAME']
    report = Report(REPORT_FILENAME, sep='|', decimal=',')
    new_tickets_after_first_line = report.get_new_tickets_after_first_line()
    risk_tickets = report.get_risk_tickets(8)
    overdue_tickets = report.get_overdue_tickets(8)
    floating_tickets = report.get_floating_tickets()
    print(floating_tickets)
    save_xls([report.df, new_tickets_after_first_line, risk_tickets, floating_tickets, overdue_tickets],
             r'C:\вся инфа\sql-otrs\reports', 'Отчет_' + datetime.today().strftime("%d_%m_%Y") + '.xls')
