from django.http import Http404

def parse_int_or_404(x):
    if x:
        try:
            parsed = int(x)
            return parsed
        except ValueError:
            raise Http404("Invalid argument")
    return Http404("No argument specified")
