from contextvars import ContextVar
from uuid import uuid4


def set_context(*conns):
    for conn in conns:
        if isinstance(conn, ContextLocalSessionManager):
            conn.set_context()


def reset_context(*conns):
    for conn in conns:
        if isinstance(conn, ContextLocalSessionManager):
            conn.reset_context()


class ContextLocalSessionManager:
    name: str

    def _scope_func(self):
        return self._ctx.get()

    def init_context(self):
        self._ctx = ContextVar(self.name)

    def set_context(self):
        session_id = f'{self.name}-{uuid4()}'
        self._ctx_token = self._ctx.set(session_id)
        # logger.warning(f'Setting context to {self.name}: {session_id}')

    def reset_context(self):
        if self._ctx and self._ctx_token:
            # logger.warning(f'reset self._ctx_token: {self._ctx_token}')
            self._ctx.reset(self._ctx_token)
            self._ctx_token = None
        # else:
        #     logger.warning(f'There is no self._ctx_token for session_id "{self.name}" (ctx: {self._ctx}, ctx_token: {self._ctx_token})')
