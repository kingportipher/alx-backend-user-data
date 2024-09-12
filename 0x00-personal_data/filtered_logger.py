#!/usr/bin/env python3

def filter_datum(fields, redaction, message, separator):
  """Obfuscates specified fields in a log message."""
  pattern = r"(?:" + separator + r"(?:\w+|" + redaction + r"))+".join(fields) + r"(?=" + separator + r")"
  return re.sub(pattern, redaction + separator, message)
