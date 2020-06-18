import multiprocessing
from typing import Generator
from typing import List
from typing import TypeVar
from typing import Callable
from logging import Logger
from typing import Iterable
from typing import Optional
import multiprocessing_logging
import time
from typing import Any
try:
    from ray.util.multiprocessing import Pool
except ImportError:
    pass


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


class CollectingPipeline:
    def __init__(self, streamers: List[Generator[S, None, None]], mappers_factory: Callable[[], List[Callable[[S], S]]],
                 output_reducer: Callable[[Iterable[S]], None], batch_size: int, parallel: bool, parallel_streams: bool,
                 logger: Optional[PipelineLogger] = None, log_every_iter: int = 10, backend: str = 'mp'):
        """
        A simple class for parallelizing a set of transformations that are consecutively applied to a stream of data.
        Notice that Multiprocessing's parallel map cannot work with generators, which makes it not usable when data is
        to big to fit in memory. Inspired by MapReduce, but considerably simpler (and less powerful).
        It is assumed that the transformations are independently applied to each object (ie. map-like).
        The output is deterministic (ie. in parallel the result is exactly equal to the one that would be
        obtained sequentially). Specifically, the output will have the following order: batch 1 of streamer 1, batch 1
        of streamer 2,...
        This class tries to handle the needs of severely I/O bound applications by parallelizing a list of streamers.
        The parallelization strategy is as follows:
            - The list of streamers will be used to generate a batch of objects that will be stored in memory.
            - When the batch is ready, a parallel map will be applied to the batch, while the other streams prepare the
            next batch running in background. So, the application iterates round robin the different streamers.
            - Once the parallel map has been applied, the results are reduced (reduced as in folded) and output in
            background.
        :param streamers: A list of generators that yield objects. Typically, it will involve some I/O.
        :param mappers_factory: A callable that returns a list of callable objects (functions or objects with the
        __call__ method), which will be the mappers of the
        :param output_reducer: A callable object or function that receives an iterable collection of objects, optionally
         applies a reduction and outputs it (eg. it writes it to a file).
        :param batch_size: The number of elements that will be stored in memory each time the mappers are applied.
        Ideally, it should be as big as possible such that no out of memory errors are caused.
        :param parallel: Whether to run the pipeline in parallel. By default, set to True.
        :param logger: A standard logger (optional). If set,
        :param log_every_iter: If the logger is set, the pipeline will log every log_every_iter iterations (int).
        """

        assert backend in ['mp', 'ray']
        self.backend = backend

        self.streamers = [self.batch_generator(g, batch_size) for g in streamers]
        self.par_logger = logger
        if parallel_streams:
            if self.par_logger:
                self.streamers_loading = time.time()
                self.par_logger.logger.info(f'{self.__class__.__name__}: Initializing streamers')
            self.streamers = [self.background_generator(g) for g in self.streamers]
            _ = list(map(next, self.streamers))  # Initialization of streamers (very expensive call)
            if self.par_logger:
                self.streamers_loading = time.time()-self.streamers_loading

        else:
            self.streamers_loading = 0.0

        self.mappers_factory = mappers_factory
        self.output_reducer = output_reducer
        self.parallel = parallel
        self.log_every_iter = log_every_iter
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

    def run(self):
        """
        Runs the pipeline with the aforementioned parallelization strategy if parallel is set to True. Otherwise, the
        pipeline is executed sequentially.
        :return:
        """

        assert not self.done
        if self.par_logger:
            input_time = 0.0
            compute_time = 0.0
            output_time = 0.0
        first = True
        if self.parallel:
            if self.par_logger:
                t0 = time.time()
                self.par_logger.logger.info(f'{self.__class__.__name__}: Initializing mappers')
            if self.backend == 'mp':
                with multiprocessing.Pool(initializer=self._initialize_mappers, initargs=(self.mappers_factory,)) \
                        as pool:
                    if first:
                        if self.par_logger:
                            t1 = time.time()
                            self.par_logger.logger.info(
                                f'{self.__class__.__name__}: Mappers initialized in {t1-t0:.2f}s')
                        first = False
                    p_init = False
                    if self.par_logger:
                        t0 = time.time()
                    i = 0
                    while len(self.streamers) > 0:
                        for idx, generator in enumerate(self.streamers):
                            try:
                                batch = next(generator)
                            except StopIteration:
                                del self.streamers[idx]
                                continue
                            if self.par_logger:
                                t1 = time.time()
                                input_time += (t1-t0)
                                t0 = time.time()
                            res = pool.map(self._map_f, batch)
                            if self.par_logger:
                                t1 = time.time()
                                compute_time += (t1-t0)
                            if p_init:
                                p.join()
                                if self.par_logger:
                                    t1_output = time.time()
                                    output_time += (t1_output - t0_output)
                            if self.par_logger:
                                if (idx+1) % self.log_every_iter == 0:
                                    self.par_logger.logger.info(f'{self.__class__.__name__}: Processed batch {idx+1+i}')
                                t0_output = time.time()
                            p = multiprocessing.Process(target=self.output_reducer, args=(res,))
                            p.start()
                            p_init = True
                            if self.par_logger:
                                t0 = time.time()
                        i += 1
                        p.join()
                        p.terminate()
            else:
                with multiprocessing.Pool(initializer=self._initialize_mappers, initargs=(self.mappers_factory,)) \
                        as pool:
                    if first:
                        if self.par_logger:
                            t1 = time.time()
                            self.par_logger.logger.info(
                                f'{self.__class__.__name__}: Mappers initialized in {t1-t0:.2f}s')
                        first = False
                    p_init = False
                    if self.par_logger:
                        t0 = time.time()
                    i = 0
                    while len(self.streamers) > 0:
                        for idx, generator in enumerate(self.streamers):
                            try:
                                batch = next(generator)
                            except StopIteration:
                                del self.streamers[idx]
                                continue
                            if self.par_logger:
                                t1 = time.time()
                                input_time += (t1-t0)
                                t0 = time.time()
                            res = pool.map(self._map_f, batch)
                            if self.par_logger:
                                t1 = time.time()
                                compute_time += (t1-t0)
                            if p_init:
                                p.join()
                                if self.par_logger:
                                    t1_output = time.time()
                                    output_time += (t1_output - t0_output)
                            if self.par_logger:
                                if (idx+1) % self.log_every_iter == 0:
                                    self.par_logger.logger.info(f'{self.__class__.__name__}: Processed batch {idx+1+i}')
                                t0_output = time.time()
                            p = multiprocessing.Process(target=self.output_reducer, args=(res,))
                            p.start()
                            p_init = True
                            if self.par_logger:
                                t0 = time.time()
                        i += 1
                        p.join()
                        p.terminate()
        else:
            self._initialize_mappers(self.mappers_factory)
            if self.par_logger:
                t0 = time.time()
            i = 0
            while len(self.streamers) > 0:
                for idx, generator in enumerate(self.streamers):
                    try:
                        batch = next(generator)
                    except StopIteration:
                        del self.streamers[idx]
                        continue
                    if self.par_logger:
                        t1 = time.time()
                        input_time += (t1-t0)
                        t0 = time.time()
                    res = list(map(self._map_f, batch))
                    if self.par_logger:
                        t1 = time.time()
                        compute_time += (t1-t0)
                        t0 = time.time()
                    self.output_reducer(res)
                    if self.par_logger:
                        t1 = time.time()
                        output_time += (t1-t0)
                        if (idx+1) % self.log_every_iter == 0:
                            self.par_logger.logger.info(f'{self.__class__.__name__}: Processed batch {idx+1+i}')
                        t0 = time.time()
                i += 1

        if self.par_logger:
            input_time += self.streamers_loading
            self.par_logger.logger.info(f'Total input time: {input_time:.2f}s')
            self.par_logger.logger.info(f'Total compute time: {compute_time:.2f}s')
            self.par_logger.logger.info(f'Total output/reduce time: {output_time:.2f}s')
        self.done = True

    @staticmethod
    def background_generator(generator: Generator[R, None, None]) -> Generator[Optional[R], None, None]:
        """
        Credits to https://stackoverflow.com/questions/49185891/make-python-generator-run-in-background
        The new generator will be preparing the next value to be yielded in background.
        In the first iteration, the generator yields None (used for initializing).
        :param generator: Generator that will be run in background.
        :return: The new generator.
        """
        def _bg_gen(gen, conn):
            first = True
            while conn.recv():
                if first:
                    conn.send(None)
                    first = False
                else:
                    try:
                        conn.send(next(gen))
                    except StopIteration:
                        conn.send(StopIteration)
                        return

        parent_conn, child_conn = multiprocessing.Pipe()
        p = multiprocessing.Process(target=_bg_gen, args=(generator, child_conn))
        p.start()
        parent_conn.send(True)
        while True:
            parent_conn.send(True)
            x = parent_conn.recv()
            if x is StopIteration:
                p.join()
                p.terminate()
                return
            else:
                yield x

    @staticmethod
    def batch_generator(gen: Generator[Q, None, None], batch_size: int) -> Generator[List[Q], None, None]:
        """
        A procedure for batching a generator into lists that will be stored in memory. It is needed for applying a
        parallel map to the objects of the generators, batch by batch.
        :param gen: Generator to be batched.
        :param batch_size: Number of elements that will be simultaneously stored in memory. Ideally, it should be as
        big as possible as long as it doesn't generate a memory error (or it consumes too much memory for the
        requirements of the application).
        :return: A generator of lists of the original type.
        """
        while True:
            batch = []
            empty = True
            for idx, e in enumerate(gen):
                empty = False
                batch.append(e)
                if idx == batch_size - 1:
                    break
            if empty:
                break
            yield batch


class MappingPipeline:
    def __init__(self, streams: List[S], mappers_factory: Callable[[], List[Callable[[S], S]]],
                 parallel: bool, logger: Optional[PipelineLogger] = None, log_every_iter: int = 10,
                 backend: str = 'mp'):
        """
        A simple class for parallelizing a set of transformations that are consecutively applied to a stream of data.
        Notice that Multiprocessing's parallel map cannot work with generators, which makes it not usable when data is
        to big to fit in memory. Inspired by MapReduce, but considerably simpler (and less powerful).
        It is assumed that the transformations are independently applied to each object (ie. map-like).
        The output is deterministic (ie. in parallel the result is exactly equal to the one that would be
        obtained sequentially). Specifically, the output will have the following order: batch 1 of streamer 1, batch 1
        of streamer 2,...
        This class tries to handle the needs of severely I/O bound applications by parallelizing a list of streamers.
        The parallelization strategy is as follows:
            - The list of streamers will be used to generate a batch of objects that will be stored in memory.
            - When the batch is ready, a parallel map will be applied to the batch, while the other streams prepare the
            next batch running in background. So, the application iterates round robin the different streamers.
            - Once the parallel map has been applied, the results are reduced (reduced as in folded) and output in
            background.
        :param streamers: A list of generators that yield objects. Typically, it will involve some I/O.
        :param mappers_factory: A callable that returns a list of callable objects (functions or objects with the
        __call__ method), which will be the mappers of the
        :param output_reducer: A callable object or function that receives an iterable collection of objects, optionally
         applies a reduction and outputs it (eg. it writes it to a file).
        :param batch_size: The number of elements that will be stored in memory each time the mappers are applied.
        Ideally, it should be as big as possible such that no out of memory errors are caused.
        :param parallel: Whether to run the pipeline in parallel. By default, set to True.
        :param logger: A standard logger (optional). If set,
        :param log_every_iter: If the logger is set, the pipeline will log every log_every_iter iterations (int).
        """

        assert backend in ['mp', 'ray']
        self.backend = backend

        self.streams = streams
        self.par_logger = logger

        self.mappers_factory = mappers_factory
        self.parallel = parallel
        self.log_every_iter = log_every_iter
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
                t0 = time.time()
                self.par_logger.logger.info(f'{self.__class__.__name__}: Initializing mappers')
            if self.backend == 'mp':
                with multiprocessing.Pool(initializer=self._initialize_mappers, initargs=(self.mappers_factory,)) \
                        as pool:
                            res = pool.map(self._map_f, self.streams)
            else:
                with multiprocessing.Pool(initializer=self._initialize_mappers, initargs=(self.mappers_factory,)) \
                        as pool:
                    res = pool.map(self._map_f, self.streams)
        else:
            self._initialize_mappers(self.mappers_factory)
            res = []
            for e in self.streams:
                res.append(self._map_f(e))

        if self.par_logger:
            pass
        self.done = True
        return res

