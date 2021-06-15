import getpass
import logging
import os
import pathlib
import platform
import random
import datetime
import sys

from crontab import CronTab
import shutil

START_TIME = datetime.time(17, 0, 0)
END_TIME = datetime.time(20, 0, 0)
DURATION = datetime.timedelta(hours=1)

WINDOWS_ETC_HOSTS = pathlib.Path("C:\Windows\System32\Drivers\etc\hosts")
LINUX_MAC_ETC_HOSTS = pathlib.Path("/etc/hosts")

UPDATE_HOSTS_CMD = ""

# used to identify the crontab during the update, keep it short and simple.
# WARNING: this is not validated
CRONTAB_COMMENT = "German homework redirect."

computer_username = getpass.getuser()

dns_scheduler = CronTab(user=computer_username)

# create the new cron job
job = dns_scheduler.new(command='', comment=CRONTAB_COMMENT)
# To schedule the job for every minute, add the following line of code:
job.minute.every(1)
# write the job to a tab
dns_scheduler.write()

tab_to_update = CronTab(user=computer_username)

for job in dns_scheduler:
    if job.comment == CRONTAB_COMMENT:
        print(job)


def select_hour() -> datetime.timedelta:
    """
    Selects a random hour to start the lockout

    Returns:

    """
    time_between_times = END_TIME - START_TIME
    random_hour = random.randrange(time_between_times)
    random_date = START_TIME + datetime.timedelta(hours=random_hour)

    return random_date


def backup_hosts_file() -> bool:
    """
    Copies the existing `/etc/hosts` file and appends a `.bck` extension. If there is no file located in the default
    location for Windows/Linux/MacOS it will prompt the user to manually to take a copy of `/etc/hosts`.

    Returns:
        bool: True for success, False otherwise.
    """
    if platform.system().lower() == "windows":
        logging.debug(f"identified {platform.system().lower()} system, default path for `/etc/hosts` "
                      f"is {WINDOWS_ETC_HOSTS}.")
        shutil.copyfile(WINDOWS_ETC_HOSTS, WINDOWS_ETC_HOSTS + ".backup")
        logging.info(f"backed up {WINDOWS_ETC_HOSTS} to {WINDOWS_ETC_HOSTS + '.backup'}.")
        return True
    elif platform.system().lower() == "linux" or platform.system().lower() == "darwin":
        logging.debug(f"identified {platform.system().lower()} system, default path for `/etc/hosts` "
                      f"is {LINUX_MAC_ETC_HOSTS}.")
        shutil.copyfile(LINUX_MAC_ETC_HOSTS, LINUX_MAC_ETC_HOSTS + ".bck")
        logging.info(f"backed up {LINUX_MAC_ETC_HOSTS} to {LINUX_MAC_ETC_HOSTS + '.bck'}.")
        return True
    else:
        logging.warning("unable to locate `/etc/hosts` file. manually backup before continuing.")
        response = query_yes_no("I have manually backed up my /etc/hosts file:")
        if response is True:
            logging.info("continuing with the `/etc/hosts` file modification.")
            return True
        else:
            logging.critical("unable to continue until `/etc/hosts` file is backed up.")
            return False


def query_yes_no(question: str, default: str = "yes") -> bool:
    """Ask a yes/no question via raw_input() and return their answer.

    `question` is a string that is presented to the user.
    `default` is the presumed answer if the user just hits <Enter>.
            It must be "yes" (the default), "no" or None (meaning an answer is required of the user).

    Returns:
        bool: True for "yes", False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == "":
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' " "(or 'y' or 'n').\n")


if __name__ == '__main__':
    if not backup_hosts_file():
        sys.exit(os.EX_OSFILE)
    else:
        print("continue working things here")
