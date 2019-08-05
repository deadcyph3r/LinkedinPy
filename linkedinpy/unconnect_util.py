""" Module which handles the connect features like unconnecting and connecting """
import json
import os
import sqlite3

from .database_engine import get_database
from .settings import Settings


def dump_connect_restriction(profile_name, logger, logfolder):
    """ Dump connect restriction data to a local human-readable JSON """
    try:
        db, id = get_database(Settings)
        conn = sqlite3.connect(db)

        with conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()

            cur.execute(
                "SELECT * FROM connectRestriction WHERE profile_id=:var",
                {"var": id})
            data = cur.fetchall()

        if data:
            filename = "{}connectRestriction.json".format(logfolder)
            if os.path.isfile(filename):
                with open(filename) as connectResFile:
                    current_data = json.load(connectResFile)
            else:
                current_data = {}

            connect_data = {user_data[1]: user_data[2]
                            for user_data in data or []}
            current_data[profile_name] = connect_data

            # dump the fresh connect data to a local human readable JSON
            with open(filename, 'w') as connectResFile:
                json.dump(current_data, connectResFile)

    except Exception as exc:
        logger.error(
            "Pow! Error occurred while dumping connect restriction data to a "
            "local JSON:\n\t{}".format(
                str(exc).encode("utf-8")))

    finally:
        if conn:
            conn.close()


def connect_restriction(operation, username, limit, logger):
    """ Keep track of the connected users and help avoid excessive connect of
    the same user """
    try:
        db, id = get_database(Settings)
        conn = sqlite3.connect(db)

        with conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()

            cur.execute(
                "SELECT * FROM connectRestriction WHERE profile_id=:id_var "
                "AND username=:name_var",
                {"id_var": id, "name_var": username})
            data = cur.fetchone()
            connect_data = dict(data) if data else None

            if operation == "write":
                if connect_data is None:
                    cur.execute(
                        "INSERT INTO connectRestriction (profile_id, "
                        "username, times) VALUES (?, ?, ?)",
                        (id, username, 1))
                else:
                    connect_data["times"] += 1
                    sql = "UPDATE connectRestriction set times = ? WHERE " \
                          "profile_id=? AND username = ?"
                    cur.execute(sql, (connect_data["times"], id, username))

                conn.commit()

            elif operation == "read":
                if connect_data is None:
                    return False

                elif connect_data["times"] < limit:
                    return False

                else:
                    exceed_msg = "" if connect_data[
                        "times"] == limit else "more than "
                    logger.info("---> {} has already been connected {}{} times"
                                .format(username, exceed_msg, str(limit)))
                    return True

    except Exception as exc:
        logger.error(
            "Dap! Error occurred with connect Restriction:\n\t{}".format(
                str(exc).encode("utf-8")))

    finally:
        if conn:
            conn.close()
