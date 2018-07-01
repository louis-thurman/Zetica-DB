import os
import database_io
import datetime
import hashlib
import shutil

BACKUP_PERIOD = datetime.timedelta(minutes=1)
NUMBER_OF_BACKUPS_TO_RETAIN = 7
BACKUPS_DIR = os.path.join(os.path.dirname(database_io.DATABASE_LOCATION), "backups")


def find_last_backup():
    latest_backup_time = datetime.datetime(1970, 1, 1, 0, 0, 1)
    latest_backup_dir = ""
    try:
        backup_files = os.listdir(BACKUPS_DIR)
    except FileNotFoundError:
        return latest_backup_dir, latest_backup_time
    for f in backup_files:
        this_files_time = datetime.datetime.fromtimestamp(os.path.getctime(os.path.join(BACKUPS_DIR, f)))
        if this_files_time > latest_backup_time:
            latest_backup_time = this_files_time
            latest_backup_dir = os.path.join(BACKUPS_DIR, f)
        else:
            pass
    return latest_backup_dir, latest_backup_time


def get_hash(path):
    file_md5 = hashlib.sha3_256()
    try:
        fh = open(path, "br")
        data = fh.read()
        file_md5.update(data)
        fh.close()
    except FileNotFoundError:
        return ""
    return file_md5.hexdigest()


def check_and_backup():
    if os.path.exists(BACKUPS_DIR):
        pass
    else:
        print("Backup: Creating Backup Dir at {}".format(BACKUPS_DIR))
        os.mkdir(BACKUPS_DIR)
    last_backup_dir, last_backup_time = find_last_backup()
    if last_backup_time + BACKUP_PERIOD < datetime.datetime.now():
        bliss = database_io.db_prep_for_access()
        if bliss is None:
            print("Backup: Could not create back-up as connection to database timed-out! (at hash)")
            return None
        else:
            pass
        bliss.connection.close()
        current_db_hash = get_hash(database_io.DATABASE_LOCATION)
        database_io.db_unlock()
        last_backup_hash = get_hash(last_backup_dir)
        if last_backup_hash == current_db_hash:
            print("Backup: Not Backing-Up, No Change")
        else:
            print("Backup: Backing-up...")
            now = datetime.datetime.now()
            new_backup_filename = "{}_backup_{:04d}-{:02d}-{:02d}-{:02d}-{:02d}-{:02d}.db".format(
                os.path.basename(database_io.DATABASE_LOCATION).rsplit(".", 1)[0],
                now.year,
                now.month,
                now.day,
                now.hour,
                now.minute,
                now.second)
            bliss = database_io.db_prep_for_access()
            if bliss is None:
                print("Backup: Could not create back-up as connection to database timed-out! (at copy)")
                return None
            else:
                pass
            bliss.connection.close()
            shutil.copy2(database_io.DATABASE_LOCATION, os.path.join(BACKUPS_DIR, new_backup_filename))
            database_io.db_unlock()
            print("Backup: Back-up created at {}".format(os.path.join(BACKUPS_DIR, new_backup_filename)))
    else:
        print("Backup: Not Backing-Up, Backed-up Recently")
