#!/usr/bin/python
class Table:
  """Simple Table utility class for python"""
  @staticmethod
  def formatter(rows):
    """Takes a list of strings as input and gives out
       a string formatted like a table"""
    decorate = lambda string, sym: sym + sym.join(string) + sym
    maxcols = map(lambda row: max(map(len, row)), zip(*rows))
    banner = decorate(map(lambda x: "-" * x, maxcols), "+")
    ans = map(lambda row: decorate([" " * (y - len(x)) + \
       x for x, y in zip(row, maxcols)], "|"), rows)
    head, body = ans[0], "\n".join(ans[1:])
    return "\n".join((banner, head, banner, body,  banner))

  @staticmethod
  def print_table(rows):
    """A method that prints the formatted input to STDOUT"""
    print Table.formatter(rows)

