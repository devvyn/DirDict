from io import BufferedWriter, BufferedReader
from typing import TypeVar, Union

BytesOrText = TypeVar('BytesOrText', Union[bytes, str])
BufferedIO = Union[BufferedWriter, BufferedReader]
