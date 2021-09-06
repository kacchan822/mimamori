""" MIMAMORI """
import configparser
from datetime import datetime, timezone
import difflib
import hashlib
import os
import sqlite3
import urllib.request
from secrets import compare_digest
from urllib.error import HTTPError

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, 'mimamori.config.ini')
DB_FILE = os.path.join(BASE_DIR, 'mimamori.db')

config = configparser.ConfigParser()
config['DEFAULT'] = {
    'method': 'GET',
    'ua': 'MIMAMORI-Client/0.1 (https://github.com/kacchan822/mimamori)',
}
config.read(CONFIG_FILE)

# Check each section has `url`
for section in config.sections():
    if 'url' not in config.options(section):
        raise ValueError(f"{section} hasn't `url`! please set `url`")


class Mimamori:
    """ A Simple WEB Site Checker """
    def __init__(self, flash_table=False):
        self.database = self._connect_db()
        self.init_db(flash_table)

    def __del__(self):
        self.database.commit()
        self.database.close()

    def _connect_db(self):
        connection = sqlite3.connect(DB_FILE)
        return connection

    def _exec_sql(self, sql, params=None, commit=False):
        cursor = self.database.cursor()
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        if commit:
            self.database.commit()
        return cursor

    def _output(self, text):
        print('------------')
        print(text, end='')
        print('\n------------')

    def _request(self, url):
        headers = {'User-Agent': config.get('DEFAULT', 'ua')}
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req) as res:
                body = res.read()
                html = body.decode()
                checksum = hashlib.sha256(body).hexdigest()
                return checksum, html
        except HTTPError as error:
            self._output(error)

    def init_db(self, flash_table=False):
        if flash_table:
            self._exec_sql('DROP TABLE check_results', commit=True)

        self._exec_sql("""
            CREATE TABLE IF NOT EXISTS check_results(
                url TEXT NOT NULL PRIMARY KEY,
                checksum TEXT NOT NULL,
                html TEXT NOT NULL,
                last_checked TIMESTAMP NOT NULL
            )
            """, commit=True)

    def get_record(self, url):
        sql = """
            SELECT checksum, html, last_checked FROM check_results WHERE url=?
            """
        return self._exec_sql(sql, (url,)).fetchone()

    def update_record(self, url, checksum, html):
        sql = """
            INSERT OR REPLACE INTO check_results(
                url, checksum, html, last_checked
            ) VALUES(?, ?, ?, ?)
            """
        self._exec_sql(
            sql,
            (url, checksum, html, datetime.now(timezone.utc).isoformat()),
            commit=True
        )

    def diff(self, oldhtml, newhtml, name, olddatetime, newdatetime):
        diff = difflib.unified_diff(
            oldhtml.splitlines(keepends=True),
            newhtml.splitlines(keepends=True),
            fromfile=f'[{name}] {olddatetime}',
            tofile=f'[{name}] {newdatetime}',
            n=0
        )
        return ''.join(diff)

    def check(self, name, url):
        response = self._request(url)
        if response:
            checksum, html = response
            record = self.get_record(url)
            if record:
                old_checksum, old_html, last_checked = record
                if not compare_digest(old_checksum, checksum):
                    self._output(
                        self.diff(
                            old_html,
                            html,
                            name,
                            last_checked,
                            datetime.now(timezone.utc).isoformat()
                        )
                    )
            else:
                self._output(f'{name} is registered!')
            self.update_record(url, checksum, html)


if __name__ == '__main__':
    mimamori = Mimamori()
    for section in config.sections():
        mimamori.check(section, config.get(section, 'url'))
