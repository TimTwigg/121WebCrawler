import requests
import cbor
import time

from utils.response import Response

def download(url, config, logger=None):
    host, port = config.cache_server
    try:
        resp = requests.get(
            f"http://{host}:{port}/",
            params=[("q", f"{url}"), ("u", f"{config.user_agent}")])

        try:
            if resp and resp.content:
                return Response(cbor.loads(resp.content))
        except (EOFError, ValueError) as e:
            pass
    except:
        # requests.get didn't succeed
        # Special status code, will retry this url later?
        logger.error(f"Failed to make request: {url}")
        return Response({"error": f"Failed to make request: {url}",
                         "status": -1,
                         "url": url})

    logger.error(f"Spacetime Response error {resp} with url {url}.")
    return Response({
        "error": f"Spacetime Response error {resp} with url {url}.",
        "status": resp.status_code,
        "url": url})
