import asyncio
import logging

from services.data_processor import DataProcessor

logging.basicConfig(
  level=logging.INFO,
  format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def main():
  processor = DataProcessor()
  await processor.run()

if __name__ == "__main__":
  asyncio.run(main())