from core.database.connector.sqlalchemy import SyncSqlAlchemyConnector, AsyncSqlAlchemyConnector


class SyncMysqlConnector(SyncSqlAlchemyConnector):
    @property
    def url(self) -> str:
        dbms = self.config['kind']
        driver = 'pymysql'
        user_id = self.config['userId']
        password = self.config['password']
        host = self.config['host']
        port = self.config['port']
        database = self.config['database']

        return f'{dbms}+{driver}://{user_id}:{password}@{host}:{port}/{database}'


class AsyncMysqlConnector(AsyncSqlAlchemyConnector):
    @property
    def url(self) -> str:
        dbms = self.config['kind']
        driver = 'aiomysql'
        user_id = self.config['userId']
        password = self.config['password']
        host = self.config['host']
        port = self.config['port']
        database = self.config['database']

        return f'{dbms}+{driver}://{user_id}:{password}@{host}:{port}/{database}'
