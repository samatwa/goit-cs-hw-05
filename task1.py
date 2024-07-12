import argparse
import asyncio
from aiopath import AsyncPath
import logging
from aiofile import async_open

# Налаштування логування
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def copy_file(src_path, dest_path):
    try:
        async with async_open(src_path, 'rb') as src_file:
            async with async_open(dest_path, 'wb') as dest_file:
                while True:
                    chunk = await src_file.read(1024)
                    if not chunk:
                        break
                    await dest_file.write(chunk)
        logger.info(f'Copied {src_path} to {dest_path}')
    except Exception as e:
        logger.error(f'Error copying {src_path} to {dest_path}: {e}')

async def read_folder(src_folder, dest_folder):
    tasks = []
    async for src_path in AsyncPath(src_folder).rglob('*'):
        if await src_path.is_file():
            ext = src_path.suffix.lstrip('.').lower()
            dest_dir = AsyncPath(dest_folder) / ext
            await dest_dir.mkdir(parents=True, exist_ok=True)
            dest_path = dest_dir / src_path.name
            tasks.append(copy_file(src_path, dest_path))
    await asyncio.gather(*tasks)

async def main():
    parser = argparse.ArgumentParser(description='Async file sorter based on file extensions')
    parser.add_argument('source_folder', type=str, help='Source folder to read files from')
    parser.add_argument('output_folder', type=str, help='Output folder to store sorted files')

    args = parser.parse_args()
    src_folder = AsyncPath(args.source_folder)
    dest_folder = AsyncPath(args.output_folder)

    if not await src_folder.is_dir():
        logger.error(f'Source folder {src_folder} does not exist or is not a directory')
        return

    if not await dest_folder.exists():
        await dest_folder.mkdir(parents=True)

    await read_folder(src_folder, dest_folder)

if __name__ == '__main__':
    asyncio.run(main())