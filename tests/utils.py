import csv
import tempfile
from pathlib import Path
from typing import List, Union, Tuple
from unittest.mock import DEFAULT

import openpyxl

from rumydata import Layout, CsvFile, ExcelFile
from rumydata.field import Field


def mock_no_module(module: str):
    """ force exception on specified module import. For use with mocker """

    def func(*args):
        if args[0] == module:
            raise ModuleNotFoundError
        else:
            return DEFAULT

    return func


def file_row_harness(row: List[Union[str, int]], layout: dict):
    """ Write row to file for testing in ingest """
    lay = Layout(layout, no_header=True)

    with tempfile.TemporaryDirectory() as d:
        csv_p = Path(d, 'file_test.csv')

        with csv_p.open('w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(row)

        xl_p = Path(d, 'excel_test.xlsx')
        wb = openpyxl.Workbook()
        sheet = wb['Sheet']
        for ix, value in enumerate(row, start=1):
            sheet.cell(row=1, column=ix).value = value
        wb.save(filename=xl_p)

        to_check = [
            ('CsvFile', CsvFile(lay), csv_p),
            ('ExcelFile', ExcelFile(lay), xl_p)
        ]
        aes = {}
        for nm, obj, p in to_check:
            try:
                assert not obj.check(p)
            except AssertionError as e:
                aes[nm] = e
        new_line = '\n'
        assert not aes, f'Write test failed for:\n {new_line.join([f"{k}:{v}" for k, v in aes.items()])}'


def file_cell_harness(value: str, field: Field):
    """ Wrapper to convert cell to row for harness check """
    file_row_harness(row=[value], layout={'c1': field})
