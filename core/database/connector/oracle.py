from core.database.connector.sqlalchemy import SyncSqlAlchemyConnector


class SyncOracleConnector(SyncSqlAlchemyConnector):
    @property
    def url(self) -> str:
        dbms = self.config['kind']
        driver = 'oracledb'
        user_id = self.config['userId']
        password = self.config['password']
        host = self.config['host']
        port = self.config['port']
        sid = self.config['sid']

        return f'{dbms}+{driver}://{user_id}:{password}@{host}:{port}/{sid}'
