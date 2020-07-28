import multiprocessing
from typing import List
from typing import TypeVar
from typing import Callable
from logging import Logger
from typing import Optional
import multiprocessing_logging
from typing import Any
import ray
from ray.util.multiprocessing import Pool

T = TypeVar('T')


class Globals:
    def __init__(self):
        self.F_MAPPERS = None


G = Globals()


class Composed:
    def __init__(self, functions: Callable[[], List[Callable[[T], T]]]):
        """
        A helper class for composing a list of functions with the same input and return type, such that they become a
        single callable object that applies consecutive transformations. Beware: because of
        Multiprocessing internals, local procedures will not work (since they can't be pickled).
        :param functions: A callable that returns a list of callable objects such that they all share the same input and
        return type. Thanks to being a callable instead of the list itself, one can initialize callable classes within
        the processes, avoiding the "non-pickable" error when Multiprocessing tries to serialize a non-serializable
        object.
        """
        self.functions = functions()

    def __call__(self, arg: T) -> T:
        """
        Consecutively applies a series of transformations to the input argument.
        :param arg: Object o transform.
        :return: The resulting transformation.
        """
        for f in self.functions:
            arg = f(arg)
        return arg


class PipelineLogger:
    def __init__(self, logger: Logger):
        """
        Wrapper around the standard Python logger, but calling multiprocessing_logging for having a process-safe
        logger.
        :param logger: Standard, initialized logger.
        """
        self.logger = logger
        multiprocessing_logging.install_mp_handler()


S = TypeVar('S')
R = TypeVar('R')
Q = TypeVar('Q')


class MappingPipeline:
    def __init__(self, streams: List[S], mappers_factory: Callable[[], List[Callable[[S], S]]],
                 parallel: bool, logger: Optional[PipelineLogger] = None, log_every_iter: int = 10,
                 backend: str = 'mp'):
        """
        A simple class for parallelizing map-like functions.
        :param streams: The seed input to the mappers.
        :param mappers_factory: A callable that returns a list of callable objects (functions or objects with the
        __call__ method), which will be the mappers of the pipeline.
        :param parallel: Whether to run the pipeline in parallel. By default, set to True.
        :param logger: A standard logger (optional).
        :param log_every_iter: If the logger is set, the pipeline will log every log_every_iter iterations (int).
        """

        assert backend in ['mp', 'ray']
        self.backend = backend

        self.streams = streams
        self.par_logger = logger

        self.mappers_factory = mappers_factory
        self.parallel = parallel
        self.log_every_iter = log_every_iter
        if self.par_logger:
            raise NotImplementedError('No pipeline logging implemented')
        self.done = False
        self.f_mappers = None

    @staticmethod
    def _initialize_mappers(mappers_factory):
        """
        Helper function to initialize the mappers (and, therefore, allow non-pickable callable to be passed to a
        parallel map). The use of global, although not ideal, is safe in this case, and it is used as a workaraound
        for initializing the mappers in each process.
        :return:
        """
        G.F_MAPPERS = Composed(mappers_factory)

    @staticmethod
    def _map_f(x):
        """
        Helper function to call the composed mappers.
        :param x: Object to be transformed.
        :return: Result from the series of transformations.
        """
        return G.F_MAPPERS(x)

    def run(self) -> Any:
        """
        Runs the pipeline with the aforementioned parallelization strategy if parallel is set to True. Otherwise, the
        pipeline is executed sequentially.
        :return:
        """

        assert not self.done
        if self.par_logger:
            pass
        if self.parallel:
            if self.par_logger:
                self.par_logger.logger.info(f'{self.__class__.__name__}: Initializing mappers')
            if self.backend == 'mp':
                with multiprocessing.Pool(initializer=self._initialize_mappers, initargs=(self.mappers_factory,)) \
                        as pool:
                            res = pool.map(self._map_f, self.streams)
            else:
                ray.init(address='auto')
                with Pool(initializer=self._initialize_mappers, initargs=(self.mappers_factory,)) as pool:
                    res = pool.map(self._map_f, self.streams)
        else:
            self._initialize_mappers(self.mappers_factory)
            res = []
            for e in self.streams:
                res.append(self._map_f(e))

        if self.par_logger:
            self.par_logger.logger.info(f'{self.__class__.__name__}: Mapping pipeline executed')
        self.done = True
        return res
