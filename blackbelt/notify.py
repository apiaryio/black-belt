

from os.path import exists
from subprocess import check_call


def notify(title, message):
    # MacOS
    if exists('/usr/bin/osascript'):
        try:
            check_call([
                '/usr/bin/osascript', '-e',
                'display notification "{}" with title "{}"'.format(message, title)
            ])
        except Exception:
            print "[Can't notify user using osascript]"

    # libnotify (many Linux distros)
    elif exists('/usr/bin/notify-send'):
        try:
            check_call(['/usr/bin/notify-send', title, message])
        except Exception:
            print "[Can't notify user using libnotify]"
