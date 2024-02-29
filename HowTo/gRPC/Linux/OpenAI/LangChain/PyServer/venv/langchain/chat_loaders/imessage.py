"""IMessage Chat Loader.

This class is used to load chat sessions from the iMessage chat.db SQLite file.
It only works on macOS when you have iMessage enabled and have the chat.db file.

The chat.db file is likely located at ~/Library/Messages/chat.db. However, your
terminal may not have permission to access this file. To resolve this, you can
copy the file to a different location, change the permissions of the file, or
grant full disk access for your terminal emulator in System Settings > Security
and Privacy > Full Disk Access.
"""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Iterator, List, Optional, Union

from langchain import schema
from langchain.chat_loaders import base as chat_loaders

if TYPE_CHECKING:
    import sqlite3


class IMessageChatLoader(chat_loaders.BaseChatLoader):
    def __init__(self, path: Optional[Union[str, Path]] = None):
        """
        Initialize the IMessageChatLoader.

        Args:
            path (str or Path, optional): Path to the chat.db SQLite file.
                Defaults to None, in which case the default path
                ~/Library/Messages/chat.db will be used.
        """
        if path is None:
            path = Path.home() / "Library" / "Messages" / "chat.db"
        self.db_path = path if isinstance(path, Path) else Path(path)
        if not self.db_path.exists():
            raise FileNotFoundError(f"File {self.db_path} not found")
        try:
            import sqlite3  # noqa: F401
        except ImportError as e:
            raise ImportError(
                "The sqlite3 module is required to load iMessage chats.\n"
                "Please install it with `pip install pysqlite3`"
            ) from e

    def _load_single_chat_session(
        self, cursor: "sqlite3.Cursor", chat_id: int
    ) -> chat_loaders.ChatSession:
        """
        Load a single chat session from the iMessage chat.db.

        Args:
            cursor: SQLite cursor object.
            chat_id (int): ID of the chat session to load.

        Returns:
            ChatSession: Loaded chat session.
        """
        results: List[schema.HumanMessage] = []

        query = """
        SELECT message.date, handle.id, message.text
        FROM message
        JOIN chat_message_join ON message.ROWID = chat_message_join.message_id
        JOIN handle ON message.handle_id = handle.ROWID
        WHERE chat_message_join.chat_id = ?
        ORDER BY message.date ASC;
        """
        cursor.execute(query, (chat_id,))
        messages = cursor.fetchall()

        for date, sender, text in messages:
            if text:  # Skip empty messages
                results.append(
                    schema.HumanMessage(
                        role=sender,
                        content=text,
                        additional_kwargs={
                            "message_time": date,
                            "sender": sender,
                        },
                    )
                )

        return chat_loaders.ChatSession(messages=results)

    def lazy_load(self) -> Iterator[chat_loaders.ChatSession]:
        """
        Lazy load the chat sessions from the iMessage chat.db
        and yield them in the required format.

        Yields:
            ChatSession: Loaded chat session.
        """
        import sqlite3

        try:
            conn = sqlite3.connect(self.db_path)
        except sqlite3.OperationalError as e:
            raise ValueError(
                f"Could not open iMessage DB file {self.db_path}.\n"
                "Make sure your terminal emulator has disk access to this file.\n"
                "   You can either copy the DB file to an accessible location"
                " or grant full disk access for your terminal emulator."
                "  You can grant full disk access for your terminal emulator"
                " in System Settings > Security and Privacy > Full Disk Access."
            ) from e
        cursor = conn.cursor()

        # Fetch the list of chat IDs
        cursor.execute("SELECT ROWID FROM chat")
        chat_ids = [row[0] for row in cursor.fetchall()]

        for chat_id in chat_ids:
            yield self._load_single_chat_session(cursor, chat_id)

        conn.close()
