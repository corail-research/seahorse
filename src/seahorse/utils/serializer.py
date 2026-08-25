from abc import abstractmethod
from collections.abc import Iterable, Callable

from seahorse.utils.custom_exceptions import MethodNotImplementedError


class Serializable:
    """
    Abstract base class for objects that can be serialized to and from JSON.

    This class defines the interface for objects
    that need to be converted to JSON format and reconstructed from JSON data.
    Subclasses must implement the serialization and deserialization methods.

    Example:
        Concrete implementation of a serializable class

        ``` py
        class MyGameObject(Serializable):

            ...

            def to_json(self) -> dict:
                return {"id": self.id, "name": self.name}

            @classmethod
            def from_json(cls, data, **kwargs):
                return cls(id=data["id"], name=data["name"])
        ```
    """

    @abstractmethod
    def to_json(self) -> dict:
        """
        Converts the object to a JSON-serializable dictionary.

        Returns:
            dict:
                A dictionary representation of the object
                that can be serialized to JSON.

        Raises:
            MethodNotImplementedError:
                If the subclass does not implement this method.
        """
        raise MethodNotImplementedError()

    @classmethod
    @abstractmethod
    def from_json(cls, data: dict | str, **kwargs) -> "Serializable":
        """
        Creates an instance of the class from JSON data.

        Args:
            data (dict | str):
                Dictionary or stringified dictionary
                containing the serialized object data.
            **kwargs (dict[str, _]):
                Additional keyword arguments
                that may be needed for reconstruction.

        Returns:
            Serializable:
                An instance of the class reconstructed from the data.

        Raises:
            MethodNotImplementedError:
                If the subclass does not implement this method.
        """
        raise MethodNotImplementedError()

    @classmethod
    def sub_serialize(cls) -> Callable:
        """
        Returns a function that recursively serializes objects to JSON format.

        The returned function handles nested serialization of objects:

        - Serializable objects ([to_json][..to_json] method)
        - Iterables ([list][], [tuple][], etc.)
        - Dictionaries
        - Other objects (`__dict__` attribute)

        Returns:
            Callable:
                A function that takes an object and returns a JSON-serializable
                representation of it and its nested structures.
        """
        def method(x):
            if isinstance(x, Serializable):
                return x.to_json()
            elif isinstance(x, Iterable):
                return [method(w) for w in x]
            elif isinstance(x, dict):
                return {str(i): j for i, j in x.items()}
            else:
                return x.__dict__
        return method
