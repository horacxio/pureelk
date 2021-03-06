
"""
    The global execution context of the worker
"""
from celery.utils.log import get_task_logger
from .store import Store

logger = get_task_logger(__name__)


class Context(object):
    def __init__(self, path):
        self._array_contexts = {}
        self._store = Store(path, logger)

    def prepare(self):
        new_arrays = self._store.load_arrays()
        arrays_not_refreshed = self._array_contexts.keys()

        logger.info("Reloaded configs. existing arrays are {}, new arrays are {}".format(
            arrays_not_refreshed,
            new_arrays.keys()))

        # Update the current execution context based on the  config store.
        for new_array in new_arrays.values():
            if new_array.id in self._array_contexts:
                # If the array already exists, we update its config.
                self._array_contexts[new_array.id].update_config_json(new_array.get_config_json())
                arrays_not_refreshed.remove(new_array.id)
            else:
                # If the array does not exist, we add it into the array_contexts.
                self._array_contexts[new_array.id] = new_array

        # For arrays no longer exists in the config store, we remove it from the context
        for array_id in arrays_not_refreshed:
            del self._array_contexts[array_id]

        logger.info("Arrays for collections = {}".format(self.array_contexts.keys()))
        self._store.save_array_states(self.array_contexts.values())


    @property
    def array_contexts(self):
        return self._array_contexts
