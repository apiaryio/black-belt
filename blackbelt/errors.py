
class BlackBeltError(Exception):
    """ Catch me to handle all "expected" error states from this package """

class ConfigurationError(BlackBeltError):
    """ Catch me to handle bad configuration (missing config, expired tokens etc.) """
