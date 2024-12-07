class PipelineError(Exception):
    pass


class DataUnavailableError(PipelineError):
    pass


class DataUnchangedError(PipelineError):
    pass
