from Persistence import DBInterface

from sqlalchemy import Column, Integer, String, Numeric, create_engine, ForeignKey, exists
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship

import logging

Base = declarative_base()

class SqlGPAsset(Base):
    __tablename__ = 'asset_identity_table'

    asset_id = Column(Integer, primary_key=True)
    asset_name = Column(String, nullable=False)
    params = relationship('SqlGPAssetParams', backref='asset_identity_table')

    def __repr__(self):
        return "<Asset(%r, %r)>" % (
            self.asset_name, self.asset_id
        )


class SqlGPAssetParams(Base):
    __tablename__ = 'parameter_identity_table'

    param_id = Column(Integer, primary_key=True)
    param_name = Column(String(50), nullable=False)
    asset_id = Column(Integer, ForeignKey('asset_identity_table.asset_id'))
    param_access = Column(Integer, nullable=False)
    param_value = Column(Numeric, default=0)

    def __repr__(self):
        return "<Parameter Attributes(%r, %r, %r, %r)>" % (
            self.param_name, self.param_id, self.param_value, self.param_access
        )


class SQLAlchemyGP(DBInterface):
    """ SQL Alchemy DB interface for GridPi"""
    def __init__(self, configparser):
        super(SQLAlchemyGP, self).__init__(configparser)

        self.engine = create_engine('sqlite:///gridpi.sqlite')
        Base.metadata.create_all(self.engine)

        self.session = Session(bind=self.engine)

    def add_asset(self, asset_name):
        """ Create a new Asset in the SQL Asset table.
            If *args are defined, corresponding parameters will be created.
        """
        asset_exists = self.session.query(exists().where(SqlGPAsset.asset_name == asset_name)).scalar()
        if not asset_exists:
            new_asset = SqlGPAsset(asset_name=asset_name)
            self.session.add(new_asset)
        else:
            logging.info('SQLAlchemyGP: Asset exists in database')

    def add_asset_params(self, asset_name, access_type, *args):
        """ Add Asset Parameters to an Asset. Asset will be created if it does not already exists.
        """
        asset = self.session.query(SqlGPAsset).filter(SqlGPAsset.asset_name == asset_name).scalar() # Get Asset Query obj

        existing_keys = [x.param_name for x in asset.params]      # get keys already associated with asset in database
        unique_args = list(set(args) - set(existing_keys))  # find the keys that need to be added, no duplication.

        for key in unique_args:
            asset.params.append(SqlGPAssetParams(param_name=key, param_access=access_type)) # Add params to Asset

        self.session.add(asset)

    def write_param(self, **kwargs):
        """ Write parameters from dict to database assets

        :param kwargs['payload'] dict(AssetName: dict{param_name_1: value_1, ..., param_name_n, value_n}}
        """

        assets = self.session.query(SqlGPAsset).all()
        for asset in assets:
            for param in asset.params:
                try:
                    param.param_value = kwargs['payload'][asset.asset_name][param.param_name]
                except:
                    pass

        self.session.commit()

    def read_param(self, **kwargs):
        """ Read parameter from database into dict.

        :param kwargs['payload']: dict(AssetName: dict{param_name_1: value_1, ..., param_name_n, value_n}}
        :return: dict(AssetName: dict{param_name_1: value_1, ..., param_name_n, value_n}}
        """

        assets = self.session.query(SqlGPAsset).all()
        for asset in assets:
            for param in asset.params:
                try:
                    kwargs['payload'][asset.asset_name][param.param_name] = param.param_value
                except:
                    pass
        return kwargs['payload']






