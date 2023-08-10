from abc import abstractmethod
from collections.abc import Iterable

from seahorse.utils.custom_exceptions import MethodNotImplementedError


class Serializable:

    @abstractmethod
    def to_json(self)->dict:
        raise MethodNotImplementedError()

    @classmethod
    @abstractmethod
    def from_json(cls,data,**kwargs)->"Serializable":
        raise MethodNotImplementedError()

    @classmethod
    def sub_serialize(cls):
        def method(x):
            if isinstance(x,Serializable):
                return x.to_json()
            elif isinstance(x,Iterable):
                return [method(w) for w in x]
            elif isinstance(x,dict):
                return {str(i):j for i,j in x.items()}
            else:
                return x.__dict__
        return method
