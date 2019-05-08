# -*- coding: utf-8 -*-
"""
Created on Wed Aug  1 13:14:50 2018

@author: gazhakv
"""

import unittest
from working_time import EmployeeWorkingTime, RegularWorkingTime, FirstLineWorkingTime


class TestComputeTime(unittest.TestCase):
    employee_working_time = EmployeeWorkingTime(start_hour=8, end_hour=17, start_minute=30, end_minute=30,
                                                friday_end_hour=16, friday_end_minute=15)

    def test_compute_friday_working_time(self):
        _start = '06.07.18 16:00'
        _end = '09.07.18 10:30'
        result = TestComputeTime.employee_working_time.compute_working_time(_start, _end, True)
        self.assertEqual(result, 2.25)
    
    def test_compute_months_working_time(self):
        _start = '28.06.18 16:00'
        _end = '03.07.18 8:50'
        result = TestComputeTime.employee_working_time.compute_working_time(_start, _end, True)
        self.assertAlmostEqual(result, 17.083, places=3)

    def test_next_day(self):
        _start = '02.04.2018  19:00:02'
        _end = '03.04.2018  8:36:31'
        result = TestComputeTime.employee_working_time.compute_working_time(_start, _end, True)
        self.assertEqual(result, 0.1)
    
    def test_lunch(self):
        _start = '02.04.2018  12:30:00'
        _end = '02.04.2018  12:45:00'
        result = TestComputeTime.employee_working_time.compute_working_time(_start, _end, True)
        self.assertEqual(result, 0)
    
    def test_holiday(self):
        _start = '28.04.2018  10:50:00'
        _end = '28.04.2018  10:54:00'
        result = TestComputeTime.employee_working_time.compute_working_time(_start, _end, True)
        self.assertAlmostEqual(result, 0.067, places=3)
    
    def test_forced_close(self):
        _start = '02.04.2018 10:10'
        _end = '16.04.2018  14:45:06'
        result = TestComputeTime.employee_working_time.compute_working_time(_start, _end, True)
        self.assertAlmostEqual(result, 83.833, places=3)

    def test_case(self):
        start = '02.07.2018 14:50'
        end = '03.07.2018 8:20'
        res = TestComputeTime.employee_working_time.compute_working_time(start, end, True)
        self.assertAlmostEqual(res, 2.667, places=3)
    
    def test_case2(self):
        start = '2018-07-01 14:50'
        end = '2018-07-02 08:10'
        res = RegularWorkingTime().compute_working_time(start, end, False)
        self.assertEqual(res, 0)

    def test_first_line(self):
        _start = '02.04.2018  17:30:00'
        _end = '03.04.2018  8:30:00'
        employee_working_time = FirstLineWorkingTime()
        result = employee_working_time.compute_working_time(_start, _end, True)
        self.assertEqual(result, 15)


if __name__ == '__main__':
    unittest.main()
