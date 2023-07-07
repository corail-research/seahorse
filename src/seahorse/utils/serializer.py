from abc import abstractmethod
from collections.abc import Iterable
import json
from seahorse.utils.custom_exceptions import MethodNotImplementedError
class Serializable:

    @abstractmethod
    def toJson(self)->str:
        raise MethodNotImplementedError()

    @classmethod
    @abstractmethod
    def fromJson(cls,data,**kwargs)->'Serializable':
        raise MethodNotImplementedError()
    
    @classmethod
    def subSerialize(cls):
        def method(x):
            if isinstance(x,Serializable):
                return x.toJson()
            elif isinstance(x,Iterable):
                return [method(w) for w in x]
            elif isinstance(x,dict):
                return {str(i):j for i,j in x.items()}
            else:
                return json.dumps(x.__dict__,default=lambda _:'_')
        return method
