# what_to_watch/opinions_app/dropbox.py

import asyncio
import os
from urllib import parse

import aiohttp
from dotenv import load_dotenv

API_HOST = 'https://cloud-api.yandex.net/'
API_VERSION = 'v1'
DISK_INFO_URL = f'{API_HOST}{API_VERSION}/disk/'
DOWNLOAD_LINK_URL = f'{API_HOST}{API_VERSION}/disk/resources/download'
REQUEST_UPLOAD_URL = f'{API_HOST}{API_VERSION}/disk/resources/upload'

load_dotenv()
DISK_TOKEN = os.environ.get('DISK_TOKEN')
APP_NAME = os.environ.get('APP_NAME')

AUTH_HEADERS = {
    'Authorization': f'OAuth {DISK_TOKEN}'
}


async def async_upload_files_to_yadisk(files):
    if files is not None:
        tasks = []
        async with aiohttp.ClientSession() as session:
            for file in files:
                tasks.append(
                    asyncio.ensure_future(
                        upload_file_and_get_url(session, file)
                    )
                )
            urls = await asyncio.gather(*tasks)
        return urls


async def upload_file_and_get_url(session, file):
    yadisk_args = {
        'path': f'app:/{file.filename}',
        'overwrite': 'True'
    }

    async with session.get(
            url=REQUEST_UPLOAD_URL,
            headers=AUTH_HEADERS,
            params=yadisk_args
    ) as response:
        data_link = await response.json()
        upload_url = data_link['href']

    async with session.put(
            url=upload_url,
            data=file.stream,
    ) as response:
        location = response.headers['Location']
        location = parse.unquote(location)
        location = location.replace('/disk', '')

    async with session.get(
        headers=AUTH_HEADERS,
        url=DOWNLOAD_LINK_URL,
        params={'path': f'{location}'}
    ) as response:
        data_download_link = await response.json()
        link = data_download_link['href']
        return link
