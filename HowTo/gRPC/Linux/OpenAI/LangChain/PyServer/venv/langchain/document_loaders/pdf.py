import json
import logging
import os
import tempfile
import time
from abc import ABC
from io import StringIO
from pathlib import Path
from typing import Any, Iterator, List, Mapping, Optional, Sequence, Union
from urllib.parse import urlparse

import requests

from langchain.docstore.document import Document
from langchain.document_loaders.base import BaseLoader
from langchain.document_loaders.blob_loaders import Blob
from langchain.document_loaders.parsers.pdf import (
    AmazonTextractPDFParser,
    PDFMinerParser,
    PDFPlumberParser,
    PyMuPDFParser,
    PyPDFium2Parser,
    PyPDFParser,
)
from langchain.document_loaders.unstructured import UnstructuredFileLoader
from langchain.utils import get_from_dict_or_env

logger = logging.getLogger(__file__)


class UnstructuredPDFLoader(UnstructuredFileLoader):
    """Load `PDF` files using `Unstructured`.

    You can run the loader in one of two modes: "single" and "elements".
    If you use "single" mode, the document will be returned as a single
    langchain Document object. If you use "elements" mode, the unstructured
    library will split the document into elements such as Title and NarrativeText.
    You can pass in additional unstructured kwargs after mode to apply
    different unstructured settings.

    Examples
    --------
    from langchain.document_loaders import UnstructuredPDFLoader

    loader = UnstructuredPDFLoader(
        "example.pdf", mode="elements", strategy="fast",
    )
    docs = loader.load()

    References
    ----------
    https://unstructured-io.github.io/unstructured/bricks.html#partition-pdf
    """

    def _get_elements(self) -> List:
        from unstructured.partition.pdf import partition_pdf

        return partition_pdf(filename=self.file_path, **self.unstructured_kwargs)


class BasePDFLoader(BaseLoader, ABC):
    """Base Loader class for `PDF` files.

    Defaults to check for local file, but if the file is a web path, it will download it
    to a temporary file, use it, then clean up the temporary file after completion
    """

    def __init__(self, file_path: str):
        """Initialize with a file path."""
        self.file_path = file_path
        self.web_path = None
        if "~" in self.file_path:
            self.file_path = os.path.expanduser(self.file_path)

        # If the file is a web path or S3, download it to a temporary file, and use that
        if not os.path.isfile(self.file_path) and self._is_valid_url(self.file_path):
            self.temp_dir = tempfile.TemporaryDirectory()
            _, suffix = os.path.splitext(self.file_path)
            temp_pdf = os.path.join(self.temp_dir.name, f"tmp{suffix}")
            if self._is_s3_url(self.file_path):
                self.web_path = self.file_path
            else:
                r = requests.get(self.file_path)

                if r.status_code != 200:
                    raise ValueError(
                        "Check the url of your file; returned status code %s"
                        % r.status_code
                    )

                self.web_path = self.file_path
                with open(temp_pdf, mode="wb") as f:
                    f.write(r.content)
                self.file_path = str(temp_pdf)
        elif not os.path.isfile(self.file_path):
            raise ValueError("File path %s is not a valid file or url" % self.file_path)

    def __del__(self) -> None:
        if hasattr(self, "temp_dir"):
            self.temp_dir.cleanup()

    @staticmethod
    def _is_valid_url(url: str) -> bool:
        """Check if the url is valid."""
        parsed = urlparse(url)
        return bool(parsed.netloc) and bool(parsed.scheme)

    @staticmethod
    def _is_s3_url(url: str) -> bool:
        """check if the url is S3"""
        try:
            result = urlparse(url)
            if result.scheme == "s3" and result.netloc:
                return True
            return False
        except ValueError:
            return False

    @property
    def source(self) -> str:
        return self.web_path if self.web_path is not None else self.file_path


class OnlinePDFLoader(BasePDFLoader):
    """Load online `PDF`."""

    def load(self) -> List[Document]:
        """Load documents."""
        loader = UnstructuredPDFLoader(str(self.file_path))
        return loader.load()


class PyPDFLoader(BasePDFLoader):
    """Load `PDF using `pypdf` and chunks at character level.

    Loader also stores page numbers in metadata.
    """

    def __init__(
        self, file_path: str, password: Optional[Union[str, bytes]] = None
    ) -> None:
        """Initialize with a file path."""
        try:
            import pypdf  # noqa:F401
        except ImportError:
            raise ImportError(
                "pypdf package not found, please install it with " "`pip install pypdf`"
            )
        self.parser = PyPDFParser(password=password)
        super().__init__(file_path)

    def load(self) -> List[Document]:
        """Load given path as pages."""
        return list(self.lazy_load())

    def lazy_load(
        self,
    ) -> Iterator[Document]:
        """Lazy load given path as pages."""
        blob = Blob.from_path(self.file_path)
        yield from self.parser.parse(blob)


class PyPDFium2Loader(BasePDFLoader):
    """Load `PDF` using `pypdfium2` and chunks at character level."""

    def __init__(self, file_path: str):
        """Initialize with a file path."""
        super().__init__(file_path)
        self.parser = PyPDFium2Parser()

    def load(self) -> List[Document]:
        """Load given path as pages."""
        return list(self.lazy_load())

    def lazy_load(
        self,
    ) -> Iterator[Document]:
        """Lazy load given path as pages."""
        blob = Blob.from_path(self.file_path)
        yield from self.parser.parse(blob)


class PyPDFDirectoryLoader(BaseLoader):
    """Load a directory with `PDF` files using `pypdf` and chunks at character level.

    Loader also stores page numbers in metadata.
    """

    def __init__(
        self,
        path: str,
        glob: str = "**/[!.]*.pdf",
        silent_errors: bool = False,
        load_hidden: bool = False,
        recursive: bool = False,
    ):
        self.path = path
        self.glob = glob
        self.load_hidden = load_hidden
        self.recursive = recursive
        self.silent_errors = silent_errors

    @staticmethod
    def _is_visible(path: Path) -> bool:
        return not any(part.startswith(".") for part in path.parts)

    def load(self) -> List[Document]:
        p = Path(self.path)
        docs = []
        items = p.rglob(self.glob) if self.recursive else p.glob(self.glob)
        for i in items:
            if i.is_file():
                if self._is_visible(i.relative_to(p)) or self.load_hidden:
                    try:
                        loader = PyPDFLoader(str(i))
                        sub_docs = loader.load()
                        for doc in sub_docs:
                            doc.metadata["source"] = str(i)
                        docs.extend(sub_docs)
                    except Exception as e:
                        if self.silent_errors:
                            logger.warning(e)
                        else:
                            raise e
        return docs


class PDFMinerLoader(BasePDFLoader):
    """Load `PDF` files using `PDFMiner`."""

    def __init__(self, file_path: str) -> None:
        """Initialize with file path."""
        try:
            from pdfminer.high_level import extract_text  # noqa:F401
        except ImportError:
            raise ImportError(
                "`pdfminer` package not found, please install it with "
                "`pip install pdfminer.six`"
            )

        super().__init__(file_path)
        self.parser = PDFMinerParser()

    def load(self) -> List[Document]:
        """Eagerly load the content."""
        return list(self.lazy_load())

    def lazy_load(
        self,
    ) -> Iterator[Document]:
        """Lazily load documents."""
        blob = Blob.from_path(self.file_path)
        yield from self.parser.parse(blob)


class PDFMinerPDFasHTMLLoader(BasePDFLoader):
    """Load `PDF` files as HTML content using `PDFMiner`."""

    def __init__(self, file_path: str):
        """Initialize with a file path."""
        try:
            from pdfminer.high_level import extract_text_to_fp  # noqa:F401
        except ImportError:
            raise ImportError(
                "`pdfminer` package not found, please install it with "
                "`pip install pdfminer.six`"
            )

        super().__init__(file_path)

    def load(self) -> List[Document]:
        """Load file."""
        from pdfminer.high_level import extract_text_to_fp
        from pdfminer.layout import LAParams
        from pdfminer.utils import open_filename

        output_string = StringIO()
        with open_filename(self.file_path, "rb") as fp:
            extract_text_to_fp(
                fp,  # type: ignore[arg-type]
                output_string,
                codec="",
                laparams=LAParams(),
                output_type="html",
            )
        metadata = {"source": self.file_path}
        return [Document(page_content=output_string.getvalue(), metadata=metadata)]


class PyMuPDFLoader(BasePDFLoader):
    """Load `PDF` files using `PyMuPDF`."""

    def __init__(self, file_path: str) -> None:
        """Initialize with a file path."""
        try:
            import fitz  # noqa:F401
        except ImportError:
            raise ImportError(
                "`PyMuPDF` package not found, please install it with "
                "`pip install pymupdf`"
            )

        super().__init__(file_path)

    def load(self, **kwargs: Optional[Any]) -> List[Document]:
        """Load file."""

        parser = PyMuPDFParser(text_kwargs=kwargs)
        blob = Blob.from_path(self.file_path)
        return parser.parse(blob)


# MathpixPDFLoader implementation taken largely from Daniel Gross's:
# https://gist.github.com/danielgross/3ab4104e14faccc12b49200843adab21
class MathpixPDFLoader(BasePDFLoader):
    """Load `PDF` files using `Mathpix` service."""

    def __init__(
        self,
        file_path: str,
        processed_file_format: str = "mmd",
        max_wait_time_seconds: int = 500,
        should_clean_pdf: bool = False,
        **kwargs: Any,
    ) -> None:
        """Initialize with a file path.

        Args:
            file_path: a file for loading.
            processed_file_format: a format of the processed file. Default is "mmd".
            max_wait_time_seconds: a maximum time to wait for the response from
             the server. Default is 500.
            should_clean_pdf: a flag to clean the PDF file. Default is False.
            **kwargs: additional keyword arguments.
        """
        super().__init__(file_path)
        self.mathpix_api_key = get_from_dict_or_env(
            kwargs, "mathpix_api_key", "MATHPIX_API_KEY"
        )
        self.mathpix_api_id = get_from_dict_or_env(
            kwargs, "mathpix_api_id", "MATHPIX_API_ID"
        )
        self.processed_file_format = processed_file_format
        self.max_wait_time_seconds = max_wait_time_seconds
        self.should_clean_pdf = should_clean_pdf

    @property
    def headers(self) -> dict:
        return {"app_id": self.mathpix_api_id, "app_key": self.mathpix_api_key}

    @property
    def url(self) -> str:
        return "https://api.mathpix.com/v3/pdf"

    @property
    def data(self) -> dict:
        options = {"conversion_formats": {self.processed_file_format: True}}
        return {"options_json": json.dumps(options)}

    def send_pdf(self) -> str:
        with open(self.file_path, "rb") as f:
            files = {"file": f}
            response = requests.post(
                self.url, headers=self.headers, files=files, data=self.data
            )
        response_data = response.json()
        if "pdf_id" in response_data:
            pdf_id = response_data["pdf_id"]
            return pdf_id
        else:
            raise ValueError("Unable to send PDF to Mathpix.")

    def wait_for_processing(self, pdf_id: str) -> None:
        """Wait for processing to complete.

        Args:
            pdf_id: a PDF id.

        Returns: None
        """
        url = self.url + "/" + pdf_id
        for _ in range(0, self.max_wait_time_seconds, 5):
            response = requests.get(url, headers=self.headers)
            response_data = response.json()
            status = response_data.get("status", None)

            if status == "completed":
                return
            elif status == "error":
                raise ValueError("Unable to retrieve PDF from Mathpix")
            else:
                print(f"Status: {status}, waiting for processing to complete")
                time.sleep(5)
        raise TimeoutError

    def get_processed_pdf(self, pdf_id: str) -> str:
        self.wait_for_processing(pdf_id)
        url = f"{self.url}/{pdf_id}.{self.processed_file_format}"
        response = requests.get(url, headers=self.headers)
        return response.content.decode("utf-8")

    def clean_pdf(self, contents: str) -> str:
        """Clean the PDF file.

        Args:
            contents: a PDF file contents.

        Returns:

        """
        contents = "\n".join(
            [line for line in contents.split("\n") if not line.startswith("![]")]
        )
        # replace \section{Title} with # Title
        contents = contents.replace("\\section{", "# ").replace("}", "")
        # replace the "\" slash that Mathpix adds to escape $, %, (, etc.
        contents = (
            contents.replace(r"\$", "$")
            .replace(r"\%", "%")
            .replace(r"\(", "(")
            .replace(r"\)", ")")
        )
        return contents

    def load(self) -> List[Document]:
        pdf_id = self.send_pdf()
        contents = self.get_processed_pdf(pdf_id)
        if self.should_clean_pdf:
            contents = self.clean_pdf(contents)
        metadata = {"source": self.source, "file_path": self.source}
        return [Document(page_content=contents, metadata=metadata)]


class PDFPlumberLoader(BasePDFLoader):
    """Load `PDF` files using `pdfplumber`."""

    def __init__(
        self, file_path: str, text_kwargs: Optional[Mapping[str, Any]] = None
    ) -> None:
        """Initialize with a file path."""
        try:
            import pdfplumber  # noqa:F401
        except ImportError:
            raise ImportError(
                "pdfplumber package not found, please install it with "
                "`pip install pdfplumber`"
            )

        super().__init__(file_path)
        self.text_kwargs = text_kwargs or {}

    def load(self) -> List[Document]:
        """Load file."""

        parser = PDFPlumberParser(text_kwargs=self.text_kwargs)
        blob = Blob.from_path(self.file_path)
        return parser.parse(blob)


class AmazonTextractPDFLoader(BasePDFLoader):
    """Load `PDF` files from a local file system, HTTP or S3.

    To authenticate, the AWS client uses the following methods to
    automatically load credentials:
    https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html

    If a specific credential profile should be used, you must pass
    the name of the profile from the ~/.aws/credentials file that is to be used.

    Make sure the credentials / roles used have the required policies to
    access the Amazon Textract service.

    Example:
        .. code-block:: python
            from langchain.document_loaders import AmazonTextractPDFLoader
            loader = AmazonTextractPDFLoader(
                file_path="s3://pdfs/myfile.pdf"
            )
            document = loader.load()
    """

    def __init__(
        self,
        file_path: str,
        textract_features: Optional[Sequence[str]] = None,
        client: Optional[Any] = None,
        credentials_profile_name: Optional[str] = None,
        region_name: Optional[str] = None,
        endpoint_url: Optional[str] = None,
    ) -> None:
        """Initialize the loader.

        Args:
            file_path: A file, url or s3 path for input file
            textract_features: Features to be used for extraction, each feature
                               should be passed as a str that conforms to the enum
                               `Textract_Features`, see `amazon-textract-caller` pkg
            client: boto3 textract client (Optional)
            credentials_profile_name: AWS profile name, if not default (Optional)
            region_name: AWS region, eg us-east-1 (Optional)
            endpoint_url: endpoint url for the textract service (Optional)

        """
        super().__init__(file_path)

        try:
            import textractcaller as tc  # noqa: F401
        except ImportError:
            raise ModuleNotFoundError(
                "Could not import amazon-textract-caller python package. "
                "Please install it with `pip install amazon-textract-caller`."
            )
        if textract_features:
            features = [tc.Textract_Features[x] for x in textract_features]
        else:
            features = []

        if credentials_profile_name or region_name or endpoint_url:
            try:
                import boto3

                if credentials_profile_name is not None:
                    session = boto3.Session(profile_name=credentials_profile_name)
                else:
                    # use default credentials
                    session = boto3.Session()

                client_params = {}
                if region_name:
                    client_params["region_name"] = region_name
                if endpoint_url:
                    client_params["endpoint_url"] = endpoint_url

                client = session.client("textract", **client_params)

            except ImportError:
                raise ModuleNotFoundError(
                    "Could not import boto3 python package. "
                    "Please install it with `pip install boto3`."
                )
            except Exception as e:
                raise ValueError(
                    "Could not load credentials to authenticate with AWS client. "
                    "Please check that credentials in the specified "
                    "profile name are valid."
                ) from e
        self.parser = AmazonTextractPDFParser(textract_features=features, client=client)

    def load(self) -> List[Document]:
        """Load given path as pages."""
        return list(self.lazy_load())

    def lazy_load(
        self,
    ) -> Iterator[Document]:
        """Lazy load documents"""
        # the self.file_path is local, but the blob has to include
        # the S3 location if the file originated from S3 for multi-page documents
        # raises ValueError when multi-page and not on S3"""

        if self.web_path and self._is_s3_url(self.web_path):
            blob = Blob(path=self.web_path)
        else:
            blob = Blob.from_path(self.file_path)
            if AmazonTextractPDFLoader._get_number_of_pages(blob) > 1:
                raise ValueError(
                    f"the file {blob.path} is a multi-page document, \
                    but not stored on S3. \
                    Textract requires multi-page documents to be on S3."
                )

        yield from self.parser.parse(blob)

    @staticmethod
    def _get_number_of_pages(blob: Blob) -> int:
        try:
            import pypdf
            from PIL import Image, ImageSequence

        except ImportError:
            raise ModuleNotFoundError(
                "Could not import pypdf or Pilloe python package. "
                "Please install it with `pip install pypdf Pillow`."
            )
        if blob.mimetype == "application/pdf":
            with blob.as_bytes_io() as input_pdf_file:
                pdf_reader = pypdf.PdfReader(input_pdf_file)
                return len(pdf_reader.pages)
        elif blob.mimetype == "image/tiff":
            num_pages = 0
            img = Image.open(blob.as_bytes())
            for _, _ in enumerate(ImageSequence.Iterator(img)):
                num_pages += 1
            return num_pages
        elif blob.mimetype in ["image/png", "image/jpeg"]:
            return 1
        else:
            raise ValueError(f"unsupported mime type: {blob.mimetype}")
