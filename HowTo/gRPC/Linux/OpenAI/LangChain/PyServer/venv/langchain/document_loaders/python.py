import tokenize

from langchain.document_loaders.text import TextLoader


class PythonLoader(TextLoader):
    """Load `Python` files, respecting any non-default encoding if specified."""

    def __init__(self, file_path: str):
        """Initialize with a file path.

        Args:
            file_path: The path to the file to load.
        """
        with open(file_path, "rb") as f:
            encoding, _ = tokenize.detect_encoding(f.readline)
        super().__init__(file_path=file_path, encoding=encoding)
