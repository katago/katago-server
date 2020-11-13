from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

class BurstRateThrottleUser(UserRateThrottle):
    scope = 'burstuser'
class SustainedRateThrottleUser(UserRateThrottle):
    scope = 'sustaineduser'
class BurstRateThrottleAnon(AnonRateThrottle):
    scope = 'burstanon'
class SustainedRateThrottleAnon(AnonRateThrottle):
    scope = 'sustainedanon'


