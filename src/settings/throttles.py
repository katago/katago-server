from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class BurstRateThrottleUser(UserRateThrottle):
    scope = "burstuser"


class SustainedRateThrottleUser(UserRateThrottle):
    scope = "sustaineduser"


class BurstRateThrottleAnon(AnonRateThrottle):
    scope = "burstanon"


class SustainedRateThrottleAnon(AnonRateThrottle):
    scope = "sustainedanon"
