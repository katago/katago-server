from django import template

register = template.Library()

# Peformance hack for converting times to a fixed ISO-like format noticeably faster
# than strftime, which has to handle a lot of other cases.
@register.filter(expects_localtime=False)
def isotimestr(value):
  return '{}-{:02d}-{:02d} {:02d}:{:02d}:{:02d} {}'.format(
    value.year,
    value.month,
    value.day,
    value.hour,
    value.minute,
    value.second,
    value.tzname()
  )

