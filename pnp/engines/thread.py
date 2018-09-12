from .parallel import ParallelEngine


# Re-use the ParallelEngine which is already implemented via threads.
class ThreadEngine(ParallelEngine):
    pass
