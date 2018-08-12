import logging
import numpy

logger = logging.getLogger(__name__)
  
class TagBody(object):
  """
  superclass for HTML tag classes
  """
  def __init__(self, *args, **kwargs):
    """
    initialize a tag body
    
    @param args : items to be enclosed in the tag
    @type  args : TagBody objects, str, int, float
    
    @param kwargs : tag attributes in key=value format
    @type  kwargs : name=str
    """
    self.logger = logging.getLogger(logger.name +
                                         ".{}".format(self.__class__.__name__))
    self.logger.debug("__init__: logger is %s", self.logger.name)
    self.logger.debug("__init__: args: %s", args)
    self.logger.debug("__init__: kwargs: %s", kwargs)
    if args:
      self.content = args
    else:
      self.content = ""
    for k, v in kwargs.items():
      self.logger.debug("__init__: setting %s to %s", k, v)
      setattr(self, k, v)
    self.text = ""
  
  def str_if_needed(self, obj):
    """
    converts obj to str for output
    """
    self.logger.debug("str_if_needed: object type is %s", type(obj))
    if obj.__class__ == str:
        text = obj
    elif obj.__class__ == int or obj.__class__ == bool:
        text = str(obj)
    else:
        text = obj.render()
    self.logger.debug("str_if_needed: returns %s", text)
    return text
    
  def render(self):
    """
    convert self to str
    
    The following attributes are not converted to HTML attributes::
      tag     - tag name
      logger  - logging.Logger
      text    - accumulates the HTML text
      content - what was passed in 'args' when initialized
      enclose - tag contents all on one line
    """
    self.logger.debug("render: opening %s", self.tag)
    self.text += "<"+self.tag
    keywords = self.__dict__.keys()
    for attr in keywords:
      if attr != "tag" and \
         attr != "logger" and \
         attr != "text" and \
         attr != "content" and \
         attr != "enclose":
        self.text += " "+attr+"="+self.str_if_needed(self.__dict__[attr])
    if self.enclose:
      self.text += ">"
    else:
      self.text += ">\n"
    if self.content:
      for item in self.content:
        self.text += self.str_if_needed(item)
      if self.enclose == False:
        self.text += "\n"
    self.text += "</"+self.tag+">"
    if self.enclose == False:
      self.text += "\n"
    self.logger.debug("render: closing %s", self.tag)
    return self.text
    
class HTMLpage(TagBody):
  def __init__(self, *args, **kwargs):
    self.tag = "HTML"
    self.enclose = False
    super(HTMLpage, self).__init__(*args, **kwargs)
  
class Head(TagBody):
  def __init__(self, *args, **kwargs):
    self.tag = "HEAD"
    self.enclose = False
    super(Head, self).__init__(*args, **kwargs)

class Title(TagBody):
  def __init__(self, text, **kwargs):
    self.tag = "TITLE"
    self.enclose = True
    super(Title, self).__init__(text, **kwargs)

class Body(TagBody):
  def __init__(self, *args, **kwargs):
    self.tag = "BODY"
    self.enclose = False
    super(Body, self).__init__(*args, **kwargs)

class H1(TagBody):
  def __init__(self, *args, **kwargs):
    self.tag = "H1"
    self.enclose = True
    super(H1, self).__init__(*args, **kwargs)

class Table(TagBody):
  def __init__(self, *args, **kwargs):
    self.tag = "TABLE"
    self.enclose = False
    super(Table, self).__init__(*args, **kwargs)

class TableRow(TagBody):
  def __init__(self, *args, **kwargs):
    self.tag = "TR"
    self.enclose = False
    super(TableRow, self).__init__(*args, **kwargs)

class TableHeader(TagBody):
  def __init__(self, *args, **kwargs):
    self.tag = "TH"
    self.enclose = True
    super(TableHeader, self).__init__(*args, **kwargs)
    
class TableData(TagBody):
  def __init__(self, *args, **kwargs):
    self.tag = "TD"
    self.enclose = True
    super(TableData, self).__init__(*args, **kwargs)

class Link(TagBody):
  def __init__(self, *args, **kwargs):
    self.tag = "A"
    self.enclose = True
    super(Link, self).__init__(*args, **kwargs)

class Centering(TagBody):
  def __init__(self, *args, **kwargs):
    self.tag = "CENTER"
    self.enclose = False
    super(Centering, self).__init__(*args, **kwargs)


if __name__ == "__main__":
  mylogger = logging.getLogger()
  mylogger.setLevel(logging.DEBUG)
  
  months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
            'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  stations = ["DSS-14", "DSS-15", "DSS-24", "DSS-25", "DSS-26"]
  years = [2016, 2017, 2018]
  
  # make table data
  cells = numpy.empty((len(stations),len(years),len(months)), dtype='S3')
  counter = 1
  for stn_idx in range(len(stations)):
    for year_idx in range(len(years)):
      for month_idx in range(len(months)):
        cells[stn_idx, year_idx, month_idx] = str(counter)
        counter += 1
  
  # head; title
  title=Title("My Page")
  head = Head(title)
  
  # body: main header
  h1 = H1("My Very Fine Web Page")
  # table: header rows
  tabhdr = [TableHeader(" ")] # empty cell for Months column
  yrhdr = [TableData(' ')]    # empty cell for Months column
  for dss in stations:
    tabhdr.append(TableHeader(dss, COLSPAN=3))
    for year in years:
      yrhdr.append(TableData(year))
  hdr_row = TableRow(*tabhdr)
  yr_row = TableRow(*yrhdr)
  
  # table: data rows; fill table by indices
  month_rows = []
  for month in months:
    month_idx = months.index(month)
    monthrow = []
    monthrow.append(TableData(month))
    for cell in range(len(stations)*len(years)):
      year_idx = cell % len(years)
      stn_idx = cell % len(stations)
      cell_data = cells[stn_idx, year_idx, month_idx]
      monthrow.append(TableData(str(cell_data)))
      monthrow.append(",")
    month_rows.append(TableRow(*monthrow))
  # table: completed
  table = Table(hdr_row, yr_row, *month_rows, BORDER=1)
  centered = Centering(table)
  # body: completed
  body = Body(h1, centered)
  # page: completed
  html = HTMLpage(head, body)
  
  # save to file
  outfile = open("HTMLtest", "w")
  outfile.write(html.render())
  outfile.close()
  
