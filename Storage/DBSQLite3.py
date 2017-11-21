from Storage import DBInterface

import sqlite3
import asyncio
import logging
from random import randint
from pathlib import Path

class DBSQLite3(DBInterface.DBInterface):
    """ SQLite3 DB interface for GridPi"""
    def __init__(self):
        super(DBSQLite3, self).__init__()

        # define path the database
        self.DB_Path = Path('tmp_db', 'tmp_db.sqlite')
        self.DB_Dir = Path(self.DB_Path.stem)
        self.DB_Dir.mkdir(exist_ok=True)

        # get handle to sqlite3 db
        self.conn = self.connect(self.DB_Path)
        self.cursor = self.conn.cursor()

        # params used for table setup:
        self.object_id_col = 'object_id'
        self.object_name_col = 'object_name'
        self.parameter_id_col = 'parameter_id'
        self.parameter_name_col = 'parameter_name'
        self.parameter_value_col = 'parameter_value'


        self.field_type = {self.object_id_col: "INTEGER",
                           self.object_name_col: "TEXT",
                           self.parameter_id_col: "INTEGER",
                           self.parameter_name_col: "TEXT",
                           self.parameter_value_col: "REAL"}

        self.object_id_table = 'object_identity_table'
        self.parameter_id_table = 'parameter_identity_table'
        self.parameter_ownership_table = 'parameter_ownership_table'
        self.parameter_value_table = 'parameter_value_table'

        self.constructSchema()

    def __del__(self):
        self.conn.commit()
        self.conn.close()

    def connect(self, db_path):
        conn = sqlite3.connect(db_path.as_posix())
        return conn

    def disconnect(self):
        self.conn.commit()
        self.conn.close()

    def constructSchema(self):
        self.drop_all_tables()  # drop all tabels from schema

        # -------- Create object ID table --------
        self.create_table(self.object_id_table,
                          self.object_id_col,
                          self.field_type,
                          self.object_name_col)

        # -------- Create parameter ID table --------
        self.create_table(self.parameter_id_table,
                          self.parameter_id_col,
                          self.field_type,
                          self.parameter_name_col)

        # -------- Create parameter ownership table --------
        self.create_table(self.parameter_ownership_table,
                          self.parameter_id_col,
                          self.field_type,
                          self.object_id_col)

        # -------- Create parameter value table --------
        self.create_table(self.parameter_value_table,
                          self.parameter_id_col,
                          self.field_type,
                          self.parameter_value_col)

    def addGroup(self, group_name, *args):
        """

        :param group_name: group name for parameters
        :param args: parameter names to be created and linked to group
        :return:
        """

        while True:  # Primary key is a random integer. If it ends up being a duplicate, try again.
            group_id = randint(0, 1000)
            try:
                self.cursor.execute("INSERT INTO {tn} ({idcn}, {cn}) VALUES (?, ?)" \
                                .format(tn=self.object_id_table,
                                        idcn=self.object_id_col,
                                        cn=self.object_name_col),
                                (group_id, group_name))
                break
            except sqlite3.OperationalError as detail:
                logging.warning('OperationalError: {}'.format(detail.args[0]))
                break
            except sqlite3.IntegrityError as detail:
                logging.warning('IntegrityError: {} ...duplicate primary key? trying again.'.format(detail.args[0]))
                pass


        for param in args:
            while True:  # Primary key is a random integer. If it ends up being a duplicate, try again.
                pid = randint(0,1000)
                # generate parameters for parameter_id_table
                try:
                    self.cursor.execute("INSERT OR IGNORE INTO {tn} ({idcn}, {cn}) VALUES (?, ?)" \
                                        .format(tn=self.parameter_id_table,
                                                idcn=self.parameter_id_col,
                                                cn=self.parameter_name_col),
                                        (pid, param))
                    break

                except sqlite3.OperationalError as detail:
                    logging.warning('OperationalError: {}'.format(detail.args[0]))
                    break
                except sqlite3.IntegrityError as detail:
                    logging.warning('IntegrityError: {} ...duplicate primary key? trying again.'.format(detail.args[0]))
                    pass

            # link parameters and objects in parameter_ownership_table
            try:
                self.cursor.execute("INSERT OR IGNORE INTO {tn} ({idcn}, {cn}) VALUES (?, ?)" \
                                    .format(tn=self.parameter_ownership_table,
                                            idcn=self.parameter_id_col,
                                            cn=self.object_id_col),
                                    (pid, group_id))
            except sqlite3.OperationalError as detail:
                logging.warning('OperationalError: {}'.format(detail.args[0]))

            # generate values for parameter_val_table
            default_parameter_value = -1
            try:
                self.cursor.execute("INSERT OR IGNORE INTO {tn} ({idcn}, {cn}) VALUES (?, ?)" \
                                    .format(tn=self.parameter_value_table,
                                            idcn=self.parameter_id_col,
                                            cn=self.parameter_value_col),
                                    (pid, default_parameter_value))
            except sqlite3.OperationalError as detail:
                logging.warning('OperationalError: {}'.format(detail.args[0]))

    def writeParam(self, **kwargs):
        """ Write payload to DB schema

        :param kwarg['payload'] = ((parameter_id_1, val_1, ..., parameter_id_n, val_n)):
        :return:
        """
        for pid, val in kwargs['payload']:
            try:
                self.cursor.execute("UPDATE {tn} SET {cn}=(?) WHERE {idcn}=(?)". \
                               format(tn=self.parameter_value_table,
                                      cn=self.parameter_value_col,
                                      idcn=self.parameter_id_col),
                               (val, pid))
            except sqlite3.OperationalError as detail:
                logging.warning('OperationalError:', detail)

    def readParam(self, **kwargs):
        """ Read payload from DB schema

        :param kwarg['payload'] = (parameter_id_1, ..., parameter_id_n):
        :return: tuple(param_val)
        """


# -------- Helper Functions --------

    def sqlite_default_value(self, field_type):
        if field_type == 'INTEGER':
            return 0
        elif field_type == 'TEXT':
            return ''
        elif field_type == 'REAL':
            return 0.0
        else:
            raise ValueError("field type '{ft}' not recognized".format(ft=field_type))

    def create_table(self, table_name, primary_key, field_types, *args):
        try:
            self.cursor.execute("CREATE TABLE {tn} ({cn} {ct} PRIMARY KEY)"\
                                .format(tn=table_name,
                                        cn=primary_key,
                                        ct=field_types[primary_key]))
        except sqlite3.OperationalError as detail:
            logging.warning("OperationalError: {}: '{}'".format(detail.args[0], self.object_id_table))

        for column_name in args:
            try:
                self.cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct} DEFAULT '{df}'"\
                                    .format(tn=table_name,
                                            cn=column_name,
                                            ct=field_types[column_name],
                                            df=self.sqlite_default_value(field_types[column_name])))

            except sqlite3.OperationalError as detail:
                logging.warning("OperationalError: {}: '{}'".format(detail.args[0], self.object_id_table))


    def get_pid_tuple_by_asset(self, name):
        """ Given an Asset name, update all parameters owned by that asset with a given value, by name.

            Flow of operation without caching:
            asset_name -> object_id
            object_id -> [parameter_IDs owned by object]
            for each parameter ID -> parameter_name
                if parameter_name == asset.parameter.name:
                parameter_id->value = asset.parameter.value

            Because we're doing this often, this operation would benefit from using an index. Caching the final
            (tag_name, parameter_id) list of tuples under the assets name would allow us to skip most of this
            process.
            @:param name = asset.config['name'] string.
        """
        asset_name = name
        # get asset_id using asset_name from asset_id_table
        self.cursor.execute("SELECT ({coi}) FROM {tn} WHERE {cn}=?" \
                            .format(coi=self.object_id_col,
                                    tn=self.object_id_table,
                                    cn=self.object_name_col),
                            (asset_name,))

        asset_id = self.cursor.fetchall()
        # get parameter_ids (pids) that belong to asset_id from parameter_ownership_table
        self.cursor.execute("SELECT ({coi}) FROM {tn} WHERE {cn}=?" \
                       .format(coi=self.parameter_id_col,
                               tn=self.parameter_ownership_table,
                               cn=self.object_id_col),
                       (str(asset_id[0][0]),))
        asset_parameter_ids = self.cursor.fetchall()

        # get parameter_names using parameter_id from parameter_id_table
        pname_pid_list = list()
        for pid in asset_parameter_ids:
            self.cursor.execute("SELECT ({coi}) FROM {tn} WHERE {cn}=?" \
                           .format(coi=self.parameter_name_col,
                                   tn=self.parameter_id_table,
                                   cn=self.parameter_id_col),
                                   (str(pid[0]),))
            pname_pid_list.append((self.cursor.fetchall()[0][0], pid[0]))

        return tuple(pname_pid_list)

    def get_tag_pid_tuple(self, name_id_tuple, asset_name):
        """ create tuples (parameter_name, parameter_id, parameter_value)
        """
        tag_pid_list = list()
        for param_name, pid in name_id_tuple:
            tag_name = ''.join(asset_name + '_' + param_name)
            tag_pid_list.append((tag_name, pid))

        return tuple(tag_pid_list)

    def package_tags(self, tag_pid_tuple, read_func):
        """ Get current tag values for package as tuple(param_id, new_value)

        @:param tag_pid_tuple = ((tag_name, parameter_id))
        @:return tuple(pid_val_list) = ((parameter_id, tagbus_value))
        """
        pid_val_list = list()
        for tag, pid in tag_pid_tuple:
            val = read_func(tag)
            pid_val_list.append((pid, val))
        return tuple(pid_val_list)

    def drop_all_tables(self):
        tables = (self.object_id_table,
                  self.parameter_id_table,
                  self.parameter_ownership_table,
                  self.parameter_value_table)

        for table in tables:
            self.cursor.execute("DROP TABLE IF EXISTS {tn}".format(tn=table))