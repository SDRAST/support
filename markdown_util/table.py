__all__ = ["MarkdownTable"]

class MarkdownTable(object):

    def __init__(self, header=None, data=None):
        self._header = header
        self._data = data
        self._max_column_size = None
        self._calc_max_column_size()

    @property
    def header(self):
        return self._header

    @header.setter
    def header(self, value):
        self._header = value
        self._calc_max_column_size()

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = value
        self._calc_max_column_size()

    def _calc_max_column_size(self):
        if self._header is None or self._data is None:
            return
        self._max_column_size = [0 for i in xrange(len(self._header))]
        for i in xrange(len(self._header)):
            current_max = self._max_column_size[i]
            column = self.column(i)
            max_column = max([len(elem) for elem in column])
            if max_column > current_max:
                self._max_column_size[i] = max_column

    def column(self, i):
        """
        Get a column, including the header
        """
        column = [self._header[i]]
        column.extend([d[i] for d in self._data])
        return column

    def row(self, i):
        """
        get a row, where the 0th row is the header.
        """
        if i == 0:
            return self._header
        else:
            return self._data[i-1]

    def _format_row(self, i):
        """
        """
        row = self.row(i)
        formatted_row = ["|"]
        for c, r in enumerate(row):
            white_space = " "*(self._max_column_size[c] - len(r))
            formatted_row.append(" {}{} |".format(r, white_space))
        return "".join(formatted_row)

    def _format_header_row(self):
        """
        """
        formatted_row = ["|"]
        for i in xrange(len(self._max_column_size)):
            formatted_row.append(" {} |".format("="*self._max_column_size[i]))
        return "".join(formatted_row)

    def dump(self):
        table = []
        table.append(self._format_row(0))
        table.append(self._format_header_row())
        for i in xrange(len(self._data)):
            table.append(self._format_row(i+1))
        return "\n".join(table)
