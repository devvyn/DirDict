from io import BufferedWriter, BufferedReader
from typing import TypeVar, Union

T = TypeVar('T', Union[str, bytes])
BufferedIO = Union[BufferedWriter, BufferedReader]
