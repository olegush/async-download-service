import os.path
import datetime
import argparse
import logging
import asyncio
from functools import partial

from aiohttp import web
import aiofiles


LOGGING_LEVELS = [logging.CRITICAL, logging.INFO]


def get_args():
    parser = argparse.ArgumentParser(description='Async downloader')
    parser.add_argument(
        '--logs',
        help='Logging the process (0 or 1, 0 by default)',
        type=int, default=0
        )
    parser.add_argument(
        '--delay',
        help='Delay response, sec (0.001 by default)',
        type=float,
        default=0.001
        )
    parser.add_argument(
        '--dir',
        help='Folder with photos',
        type=str,
        )
    args = parser.parse_args()
    return args


async def archivate(delay, dir, request):
    '''Asynchronously archive directory on the fly and send it to client.'''

    dir_path = '{}/{}'.format(dir, request.match_info['archive_hash'])

    if not os.path.exists(dir_path):
        return web.HTTPNotFound(text='Error 404: archive does not exists.')

    # Create stream object
    resp = web.StreamResponse()

    # Send headers.
    resp.headers['Content-Type'] = 'application/zip'
    resp.headers['Content-Disposition'] = 'attachment; filename="archive.zip"'
    await resp.prepare(request)

    # Create async subprocess for archive directory.
    cmd = 'zip -r - {}'.format(dir_path)
    process = await asyncio.create_subprocess_shell(
                                cmd,
                                stdout=asyncio.subprocess.PIPE,
                                stderr=asyncio.subprocess.PIPE
                                )

    try:

        while True:

            # Get chunks from process stdout, check if exists,
            # write it to response, log and delay.
            archive_chunk = await process.stdout.readline()
            if not archive_chunk:
                break
            await resp.write(archive_chunk)
            logging.info(
                'Sending archive {}, chunk {} bytes'.format(
                    request.match_info['archive_hash'],
                    len(archive_chunk)
                    )
                )
            await asyncio.sleep(delay)

        await resp.write_eof()
        process.kill()
        process.wait()

    except asyncio.CancelledError as e:
        resp.force_close()

    finally:
        resp.force_close()
        return resp


async def handle_index_page(request):
    async with aiofiles.open('index.html', mode='r') as index_file:
        index_contents = await index_file.read()
    return web.Response(text=index_contents, content_type='text/html')


if __name__ == '__main__':
    args = get_args()
    logs, delay, dir = args.logs, args.delay, args.dir

    if not dir:
        exit('Script argument required (path to folder with photos)')
    if not os.path.isdir(dir):
        exit('Folder does not exists')

    logging.basicConfig(
        level=LOGGING_LEVELS[logs],
        format='%(asctime)s,%(msecs)d %(levelname)s: %(message)s',
        datefmt='%H:%M:%S',
        )

    archivate_with_args = partial(archivate, delay, dir)

    app = web.Application()
    app.add_routes([
        web.get('/', handle_index_page),
        web.get('/archive/{archive_hash}/', archivate_with_args),
    ])
    web.run_app(app)
