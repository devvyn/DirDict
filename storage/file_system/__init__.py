from io import BufferedReader, BufferedWriter
from typing import TypeVar, Union

Text = TypeVar('Text', Union[str, bytes])
BufferedIO = Union[BufferedWriter, BufferedReader]
