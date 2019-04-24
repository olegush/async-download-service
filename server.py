import os.path
import datetime
import argparse
import logging
import asyncio

from aiohttp import web
import aiofiles


def get_arg_parser():
    parser = argparse.ArgumentParser(description='Async downloader')
    parser.add_argument(
        '--do_logging',
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
        default='test_photos'
        )
    args = parser.parse_args()
    return args


async def archivate(request):
    '''Archive and send photos to user'''

    user_args = get_arg_parser()
    do_logging = user_args.do_logging
    INTERVAL_SECS = user_args.delay
    dir_path = user_args.dir

    if not dir_path:
        exit('Script argument required (path to folder with photos)')
    if not os.path.isdir(dir_path):
        exit('Folder does not exists')

    dir_path = '{}/{}'.format(dir_path, request.match_info['archive_hash'])

    if os.path.exists(dir_path):
        # Create stream object
        resp = web.StreamResponse()
        resp.force_close()

        # Send headers.
        resp.headers['Content-Type'] = 'application/zip'
        resp.headers['Content-Disposition'] = 'attachment; filename="archive.zip"'
        await resp.prepare(request)

        # Create async subprocess for zipping.
        cmd = 'zip -r - {}'.format(dir_path)
        process = await asyncio.create_subprocess_shell(
                                    cmd,
                                    stdout=asyncio.subprocess.PIPE,
                                    stderr=asyncio.subprocess.PIPE
                                    )

        try:

            # Get chunks from process stdout.
            while True:
                archive_chunk = await process.stdout.readline()

                # Check for end of the file.
                if archive_chunk:

                    # Write chunk to response.
                    await resp.write(archive_chunk)

                    # Logging
                    if bool(do_logging):
                        logging.info(
                            'Sending archive {}, chunk {} bytes'.format(
                                request.match_info['archive_hash'],
                                len(archive_chunk)
                                )
                            )

                else:
                    # Write end of the file, kill the process and out from loop.
                    await resp.write_eof()
                    process.kill()
                    process.wait()
                    break

                await asyncio.sleep(INTERVAL_SECS)

        except asyncio.CancelledError as e:
            raise

        finally:
            resp.force_close()
            return resp

    else:
        return web.HTTPNotFound(text='Error 404: archive does not exists.')


async def handle_index_page(request):
    async with aiofiles.open('index.html', mode='r') as index_file:
        index_contents = await index_file.read()
    return web.Response(text=index_contents, content_type='text/html')


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s,%(msecs)d %(levelname)s: %(message)s',
        datefmt='%H:%M:%S',
        )
    app = web.Application()
    app.add_routes([
        web.get('/', handle_index_page),
        web.get('/archive/{archive_hash}/', archivate),
    ])
    web.run_app(app)
