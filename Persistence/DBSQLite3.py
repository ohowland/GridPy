from Persistence import Persistence

import sqlite3
import logging
from random import randint

def sqlite_default_value(field_type):
    if field_type == 'INTEGER':
        return 0
    elif field_type == 'TEXT':
        return ''
    elif field_type == 'REAL':
        return 0.0
    else:
        raise ValueError("field type '{ft}' not recognized".format(ft=field_type))


class DBSQLite3(Persistence.DBInterface):
    """ SQLite3 DB interface for GridPi"""
    def __init__(self, config_dict):
        super(DBSQLite3, self).__init__(config_dict)

        # get handle from sqlite3 class
        self.conn = self.connect(self.db_path)
        self.cursor = self.conn.cursor()

        # table names used in schema
        self.group_id_table = 'object_identity_table'
        self.parameter_id_table = 'parameter_identity_table'
        self.parameter_ownership_table = 'parameter_ownership_table'
        self.parameter_value_table = 'parameter_value_table'

        # column names used in schema:
        self.group_id_col = 'object_id'
        self.group_name_col = 'object_name'
        self.parameter_id_col = 'parameter_id'
        self.parameter_name_col = 'parameter_name'
        self.parameter_value_col = 'parameter_value'

        self.field_type = {self.group_id_col: "INTEGER",
                           self.group_name_col: "TEXT",
                           self.parameter_id_col: "INTEGER",
                           self.parameter_name_col: "TEXT",
                           self.parameter_value_col: "REAL"}

        if config_dict['empty_database_on_start']:
            self.constructSchema()  # Drops all tables in the database, constructs a fresh Schema.

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

        # create group_id table. this table links group_ids group_names
        self.create_table(self.group_id_table,
                          self.group_id_col,
                          self.field_type,
                          self.group_name_col)

        # create parameter_id table. this table links parameter_ids with parameter_names
        self.create_table(self.parameter_id_table,
                          self.parameter_id_col,
                          self.field_type,
                          self.parameter_name_col)

        # create parameter ownership table. this table links parameter_ids to group_ids
        self.create_table(self.parameter_ownership_table,
                          self.parameter_id_col,
                          self.field_type,
                          self.group_id_col)

        # create parameter value table. this table links parameter_ids with parameter_values
        self.create_table(self.parameter_value_table,
                          self.parameter_id_col,
                          self.field_type,
                          self.parameter_value_col)

    def addGroup(self, group_name, *args):
        """ Add a new group to the database schema. this function will create the group and assign it a unique group_id.
            all arguments passed this function beyond the group name are assumed to be parameters owned by the group.
            a unique parameter_id will be assigned to each parameter, linked to the group, and inserted into the
            parameter_id, parameter_ownership, and parameter_value tables.

        :param group_name: string that characterizes the group. i.e. the object's name that owns the parameters.
        :param args: parameter names to be created and linked to group
        :return:
        """

        retry_attempts = 0  # Track number of retry attempts. Raise sqlite3.IntegrityError after 10th failure.
        while True:  # Primary key is a random integer. If it ends up being a duplicate, try again.
            group_id = randint(0, 1000)
            try:
                self.insert(self.group_id_table,
                            self.group_id_col,
                            self.group_name_col,
                            (group_id, group_name))
                break
            except sqlite3.IntegrityError as detail:
                logging.warning('IntegrityError: {} ...duplicate primary key? trying again.'.format(detail.args[0]))
                if retry_attempts > 10:
                    raise sqlite3.IntegrityError
                retry_attempts += 1
                pass

        for param in args:
            retry_attempts = 0  # Track number of retry attempts. Raise sqlite3.IntegrityError after 10th failure.
            while True:         # Primary key is a random integer. If it ends up being a duplicate, try again.
                pid = randint(0, 1000)
                # generate parameters for parameter_id_table
                try:
                    self.insert(self.parameter_id_table,
                                self.parameter_id_col,
                                self.parameter_name_col,
                                (pid, param))
                    break
                except sqlite3.IntegrityError as detail:
                    logging.warning('IntegrityError: {} ...duplicate primary key? trying again.'.format(detail.args[0]))
                    if retry_attempts > 10:
                        raise sqlite3.IntegrityError
                    retry_attempts += 1
                    pass

            # link parameters and objects in parameter_ownership_table
            self.insert(self.parameter_ownership_table,
                        self.parameter_id_col,
                        self.group_id_col,
                        (pid, group_id))

            # generate values for parameter_val_table
            default_parameter_value = -1
            self.insert(self.parameter_value_table,
                        self.parameter_id_col,
                        self.parameter_value_col,
                        (pid, default_parameter_value))

    def writeParam(self, **kwargs):
        """ Write payload to DB schema

        :param kwargs: 'payload' = ((parameter_id_1, val_1, ..., parameter_id_n, val_n)):
        :return:
        """
        for pid, val in kwargs['payload']:
            try:
                self.cursor.execute("UPDATE {tn} SET {cn}=(?) WHERE {idcn}=(?)".
                                    format(tn=self.parameter_value_table,
                                           cn=self.parameter_value_col,
                                           idcn=self.parameter_id_col),
                                    (val, pid))
            except sqlite3.OperationalError as detail:
                logging.warning('OperationalError:', detail)

    def readParam(self, **kwargs):
        """ Read payload from DB schema

        :param kwargs: 'payload' = (parameter_id_1, ..., parameter_id_n):
        :return: tuple(param_val)
        """
        pass

# -------- Helper Functions --------

    def create_table(self, table_name, primary_key, field_types, *args):
        try:
            self.cursor.execute("CREATE TABLE {tn} ({cn} {ct} PRIMARY KEY)"
                                .format(tn=table_name,
                                        cn=primary_key,
                                        ct=field_types[primary_key]))
        except sqlite3.OperationalError as detail:
            logging.warning("OperationalError: {}: '{}'".format(detail.args[0], self.group_id_table))

        for column_name in args:
            try:
                self.cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct} DEFAULT '{df}'"
                                    .format(tn=table_name,
                                            cn=column_name,
                                            ct=field_types[column_name],
                                            df=sqlite_default_value(field_types[column_name])))

            except sqlite3.OperationalError as detail:
                logging.warning("OperationalError: {}: '{}'".format(detail.args[0], self.group_id_table))

    def insert(self, table_name, primary_key_column, param_column, value_tuple):
        try:
            self.cursor.execute("INSERT OR IGNORE INTO {tn} ({idcn}, {cn}) VALUES (?, ?)"
                                .format(tn=table_name,
                                        idcn=primary_key_column,
                                        cn=param_column),
                                value_tuple)
        except sqlite3.OperationalError as detail:
            logging.warning('OperationalError: {}'.format(detail.args[0]))

    def query_for_match(self, table_name, primary_key_column, parameter_column, value):
        self.cursor.execute("SELECT ({coi}) FROM {tn} WHERE {cn}=?"
                            .format(coi=primary_key_column,
                                    tn=table_name,
                                    cn=parameter_column),
                            (value,))

    def get_pid_names(self, name):
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
            @:return ( (parameter_name_1, parameter_id_1), ..., (parameter_name_n, parameter_id_n) )
        """
        asset_name = name
        # query for asset_id using asset_name from asset_id_table
        self.query_for_match(self.group_id_table,
                             self.group_id_col,
                             self.group_name_col,
                             asset_name)
        asset_id = self.cursor.fetchall()

        # query for parameter_ids (pids) that belong to asset_id from parameter_ownership_table
        self.query_for_match(self.parameter_ownership_table,
                             self.parameter_id_col,
                             self.group_id_col,
                             str(asset_id[0][0]))
        asset_parameter_ids = self.cursor.fetchall()

        # get parameter_names using parameter_id from parameter_id_table
        pname_pid_list = list()
        for pid in asset_parameter_ids:
            self.query_for_match(self.parameter_id_table,
                                 self.parameter_name_col,
                                 self.parameter_id_col,
                                 str(pid[0]))
            pname_pid_list.append((self.cursor.fetchall()[0][0], pid[0]))

        return tuple(pname_pid_list)

    def package_tags(self, tag_pid_tuple, read_func):
        """ Get current values params using read_func, then package as tuple of form:
            ( (parameter_id_1, parameter_value_1), ..., (parameter_id_n, parameter_value_n) )

        @:param tag_pid_tuple = ((tag_name, parameter_id))
        @:return tuple(pid_val_list) = ((parameter_id, tag_value))
        """
        pid_val_list = list()
        for tag, pid in tag_pid_tuple:
            pid_val_list.append((pid, read_func(tag)))  # new tuple (parameter_id, tag_value)
        return tuple(pid_val_list)

    def drop_all_tables(self):
        """ DANGER DANGER DANGER cleans entire database, there are no survivors. ]
        """
        tables = (self.group_id_table,
                  self.parameter_id_table,
                  self.parameter_ownership_table,
                  self.parameter_value_table)

        for table in tables:
            self.cursor.execute("DROP TABLE IF EXISTS {tn}".format(tn=table))
