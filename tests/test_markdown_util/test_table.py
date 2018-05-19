import unittest

from support.markdown_util.table import MarkdownTable

class TestMarkdownTable(unittest.TestCase):

    def setUp(self):
        table = MarkdownTable()
        table.header = ["Column 1", "Column 2", "Column 3"]
        table.data = [["1","2","3"],["a"*10,"b","c"]]
        self.table = table

    def test__calc_max_column_size(self):
        self.table._calc_max_column_size()
        self.assertItemsEqual(self.table._max_column_size,[10, 8, 8])

    def test_column(self):
        column0 = self.table.column(0)
        column1 = self.table.column(1)
        self.assertItemsEqual(column0, ["Column 1", "1", "a"*10])
        self.assertItemsEqual(column1, ["Column 2", "2", "b"])

    def test_row(self):
        header = self.table.row(0)
        data0 = self.table.row(1)

        self.assertTrue(header, self.table.header)
        self.assertTrue(data0, self.table.data[0])

    def test__format_row(self):
        row0 = self.table._format_row(0)
        self.assertTrue(row0 == "| Column 1   | Column 2 | Column 3 |")

    def test__format_header_row(self):
        self.assertTrue(self.table._format_header_row() == "| ========== | ======== | ======== |")

    def test_dump(self):
        final_str = ("| Column 1   | Column 2 | Column 3 |\n"
                     "| ========== | ======== | ======== |\n"
                     "| 1          | 2        | 3        |\n"
                     "| aaaaaaaaaa | b        | c        |")
        dump = self.table.dump()
        self.assertTrue(dump == final_str)

if __name__ == "__main__":
    unittest.main()
