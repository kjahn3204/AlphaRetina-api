from functools import wraps

from dependency_injector.wiring import inject, Provide
from rcore.log import logger

from core.container import CoreContainer


def context(original_fn):
    @wraps(original_fn)
    @inject
    def _context(*args,
                 core: CoreContainer = Provide['core'],
                 **kwargs):
        # before calling src func
        logger.info(f'@context')

        core.set_context()
        ret = original_fn(*args, **kwargs)
        core.reset_context()

        return ret

    return _context


def acontext(original_fn):
    @wraps(original_fn)
    @inject
    async def _context(*args,
                       core: CoreContainer = Provide['core'],
                       **kwargs):
        # before calling src func
        logger.info(f'@context')

        core.set_context()
        ret = await original_fn(*args, **kwargs)
        core.reset_context()

        return ret

    return _context

