# -*- coding: utf-8 -*-


class TransformationWrapper:
    """Apply the transformation function ``function`` to each element of ``data``.

    In most cases, transformation functions do not need to have access to the entire group of datasets. In this case, it is more natural to write the function to operate directly on a single dataset, and avoid the ``for ds in data`` boilerplate. This class wraps these functions, and preserves function metadata for reporting.

    Each application of ``function`` should return a list of new datasets which replace the incoming dataset. The input data can be optionally filtered by ``filter_function``, which should take a dataset and return a boolean.

    Usage:

    .. code-block:: python

        filter_function = lambda dataset: dataset['name'] == 'foo'
        new_function = ApplyTransformation(transformation_function_with_single_dataset_input, filter_function)
        changed_data = new_function(old_data)

    """
    def __init__(self, function, filter_function=None):
        self.func = function
        self.filter = (lambda x: True) if filter_function is None else filter_function
        self.__name__ = function.__name__
        self.__doc__ = function.__doc__
        self.__table__ = getattr(function, "__table__", None)

    def __call__(self, data):
        _ = lambda ds: self.func(ds) if self.filter(ds) else [ds]
        return [ds for elem in data for ds in _(elem)]
