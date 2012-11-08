# Copyright (C) 2012 the DB2CSV authors and contributors
# <see AUTHORS file>
#
# This module is part of ColanderAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
import argparse
import csv
import datetime
import shutil
import tempfile
import urlparse
import zipfile


class Database(object):

    def __init__(self, db_uri, dst_dir, as_zip=True, verbose=False):
        self.db_uri = db_uri
        self.dst_dir = dst_dir
        self.as_zip = as_zip
        self.verbose = verbose
        self.engine = create_engine(db_uri, echo=verbose)
        self.Base = declarative_base()
        self.Base.metadata.bind = engine
        self.Base.metadata.reflect(engine)

    def archive(self):
        if self.as_zip:
            dst = tempfile.mkdtemp()

        else:
            dst = self.dst_dir

        for name, table in self.Base.metadata.tables.items():
            dst_file = os.path.join(dst, name)
            with open(dst_file, 'wb') as csvfile:
                writer = csv.writer(csvfile)
                for row in engine.execute(table.select()):
                    writer.writerow(row)

        if self.as_zip:
            uri = urlparse.urlparse(self.db_uri)
            now = datetime.datetime.now()
            format = '%Y-%m-%d_%H:%M:%S.%f'
            file_name = 'database_{}_archived_{}'.format(uri.path,
                                                         now.strftime(format))
            dst_file = os.path.join(self.dst_dir, file_name)
            with zipfile.ZipFile(dst_file, 'w') as myzip:
                for file_ in files:
                    myzip.write(file_)

            shutil.rmtree(dst)



class Parser(object):

    def __init__(self):
        parser = argparse.ArgumentParser(description='Export database tables as CSV files and archive them.')
        parser.add_argument('db', '--db',
                            dest='db_uri',
                            metavar='DATABASE URI',
                            required=True,
                            help='The SQLAlchemy database URI: http://docs.sqlalchemy.org/en/rel_0_7/core/engines.html?highlight=engine#database-urls')
        parser.add_argument('--dst',
                            dest='dst_dir',
                            metavar='DESTINATION DIR',
                            required=False,
                            default='.',
                            help='The destination path of archived files.')
        parser.add_argument('--zip',
                            dest='zip',
                            metavar='ARCHIVE AS ZIP',
                            required=False,
                            default=True,
                            help='Archive files as zip.')
        parser.add_argument('--verbose',
                            dest='verbose',
                            metavar='VERBOSE',
                            required=False,
                            default=False,
                            help='Enable displaying of SQLAlchemy logs.')
        self.parser = parser
        self.args = parser.parse_args()

    @property
    def db_uri(self):
        return self.args.db_uri

    @property
    def dst_dir(self):
        return self.args.dst_dir

    @property
    def zip(self):
        return self.args.zip

    @property
    def verbose(self):
        return self.args.verbose
