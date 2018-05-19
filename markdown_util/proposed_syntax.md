### Markdown Utility proposed syntax

```python
from support import markdown_util as md_util

data = [[1,2,3],["a","b","c"]]
header = ["Column1", "Column2", "Column3"]

t = md_util.Table()
t.set_header(header)
t.set_data(data)
t.dump()

# or
t = md_util.Table(header=header, data=data)
t.dump()

# both output the following:
#

"""
| Column1 | Column2 | Column3 |
| ======= | ======= | ======= |
| 1       | 2       | 3       |
| a       | b       | c       |  
"""

```
