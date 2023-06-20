import argparse
from loguru import logger
import requests
from urllib.parse import urljoin
from retry import retry
import sqlite3
import time
from typing import Dict, Optional


class BaseUrlSession(requests.Session):
    def __init__(self, base_url: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_url = base_url

    def request(self, method, url, *args, **kwargs):
        url = urljoin(self.base_url, url)
        return super().request(method, url, *args, **kwargs)


def prepare_session(
    base_url: str,
    headers: Dict[str, str],
    proxy: Optional[str] = None
):
    session = BaseUrlSession(base_url)
    session.headers.update(headers)
    if proxy:
        session.proxies.update({"http": proxy, "https": proxy})
    return session


class TopicV3:
    def __init__(
        self,
        session: BaseUrlSession,
    ):
        self.session = session

    @retry(tries=3, delay=5)
    def create(
        self,
        cid: int,
        title: str,
        content: str,
        **kwargs,
    ) -> requests.Response:
        return self.session.post(
            "/api/v3/topics",
            json={
                "cid": cid,
                "title": title,
                "content": content,
                **kwargs,
            },
        )

    @retry(tries=3, delay=5)
    def get(
        self,
        tid: int,
    ) -> requests.Response:
        return self.session.get(
            f"/api/v3/topics/{tid}",
        )

    @retry(tries=3, delay=5)
    def reply(
        self,
        content: str,
        **kwargs,
    ) -> requests.Response:
        return self.session.post(
            f"/api/v3/topics/{tid}",
            json={
                "content": content,
                **kwargs,
            },
        )


class NodeBBClientV3:
    def __init__(
        self,
        uri: str,
        api_key: str,
        proxy: str,
    ):
        self.session = prepare_session(
            base_url=uri,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            proxy=proxy,
        )

        self.topics = TopicV3(session=self.session)


class UserV1:
    def __init__(
        self,
        session: BaseUrlSession,
    ):
        self.session = session

    @retry(tries=3, delay=5)
    def get_by_username(
        self,
        username: str,
    ) -> requests.Response:
        return self.session.get(
            f"/api/user/username/{username}",
            params={"_uid": 4},
        )


class NodeBBClientV1:
    def __init__(
        self,
        uri: str,
        api_key: str,
        proxy: str,
    ):
        self.session = prepare_session(
            base_url=uri,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            proxy=proxy,
        )

        self.users = UserV1(session=self.session)


class SQLiteDB:
    def __init__(
        self,
        db_path: str,
    ):
        self.con = sqlite3.connect(db_path)
        self.cur = self.con.cursor()

    def iter(self, cond: str = "1 = 1"):
        self.cur.execute(f"SELECT * FROM memory WHERE {cond}")
        for row in self.cur:
            yield row


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--uri", type=str, required=True)
    parser.add_argument("--api-key", type=str, required=True)
    parser.add_argument("--proxy", type=str, required=False)
    parser.add_argument("--db-path", type=str, required=True)
    parser.add_argument("--topic-title", type=str, required=True)
    parser.add_argument("--username", type=str, required=True)
    parser.add_argument("--interval", type=int, required=False, default=5)
    args = parser.parse_args()

    client_write = NodeBBClientV3(
        uri=args.uri,
        api_key=args.api_key,
        proxy=args.proxy,
    )
    client_read = NodeBBClientV1(
        uri=args.uri,
        api_key=args.api_key,
        proxy=args.proxy,
    )
    db = SQLiteDB(
        args.db_path,
    )

    logger.info(f"creating topic {args.topic_title} by {args.username}")
    tid = client_write.topics.create(
        cid=7,  # hardcoded
        title=args.topic_title,
        content="",
        _uid=client_read.users.get_by_username(args.username).json()["uid"],
    ).json()["response"]["tid"]

    current_message_id_sqlite = 0
    message_id_sqlite = 0
    pid_to_message_id_sqlite = {}
    message_id_sqlite_to_pid = {}
    while True:
        logger.info(f"searching for new messages where id > {current_message_id_sqlite}")
        for row in db.iter(
            cond=f"id > {current_message_id_sqlite}"
        ):
            timestamp, name, role, topic, message, parent, message_id_sqlite = row

            if role == "system":
                logger.info(f"Skipping system message {message_id_sqlite}")
                continue

            uid = client_read.users.get_by_username(name).json()["uid"]
            toPid = None
            if parent != -1:
                toPid = message_id_sqlite_to_pid.get(parent)

            kwargs = {
                "tid": tid,
                "content": f"{topic}\n{message}",
                "_uid": uid,
            }
            if toPid:
                kwargs["toPid"] = toPid
            
            pid = client_write.topics.reply(**kwargs).json()["response"]["pid"]
            pid_to_message_id_sqlite[pid] = message_id_sqlite
            message_id_sqlite_to_pid[message_id_sqlite] = pid

            logger.info(f"Posted message {message_id_sqlite} as pid {pid}")

        current_message_id_sqlite = message_id_sqlite
        time.sleep(args.interval)
