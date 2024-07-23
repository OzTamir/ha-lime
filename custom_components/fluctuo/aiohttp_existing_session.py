import aiohttp
from gql.transport.aiohttp import AIOHTTPTransport


class AIOHTTPTransportExistingSession(AIOHTTPTransport):
    # https://github.com/graphql-python/gql/issues/91#issuecomment-632048790
    def __init__(self, *args, client_session: aiohttp.ClientSession, **kwargs):
        super().__init__(*args, **kwargs)
        self.session = client_session

    async def connect(self) -> None:
        pass

    async def close(self) -> None:
        pass
