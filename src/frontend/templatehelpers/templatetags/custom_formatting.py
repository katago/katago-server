from django import template

register = template.Library()


# Peformance hack for converting times to a fixed ISO-like format noticeably faster
# than strftime, which has to handle a lot of other cases.
@register.filter(expects_localtime=False)
def isotimestr(value):
    return "{}-{:02d}-{:02d} {:02d}:{:02d}:{:02d} {}".format(
        value.year, value.month, value.day, value.hour, value.minute, value.second, value.tzname()
    )


# Replace underscores with spaces - used to make it more natural to wordbreak a column
# and get better css flow
@register.filter()
def underscores_to_spaces(value):
    return value.replace("_", " ")


@register.filter()
def chop_network_run_name(value, run_name):
    if value.startswith(run_name + "-"):
        return value[len(run_name) + 1 :]
    return value


@register.filter()
def game_winner_class(game, network):
    if game.winner == "W" and game.white_network.name == network.name:
        return "winnerResultStyle"
    if game.winner == "B" and game.black_network.name == network.name:
        return "winnerResultStyle"
    if game.winner == "B" and game.white_network.name == network.name:
        return "loserResultStyle"
    if game.winner == "W" and game.black_network.name == network.name:
        return "loserResultStyle"
    return "drawResultStyle"

@register.filter()
def network_row_style(network, strongest_confident_network):
    if network.name == strongest_confident_network.name:
        return "strongestNetworkRowStyle"
    return "networkRowStyle"
