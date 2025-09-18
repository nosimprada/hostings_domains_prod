import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

# from api.dynadot import get_user_balance
# from api.hestia import enable_ssl_for_domain
# from api.namecheap import check_available_zones, check_domain, get_domain_info
from api.dynadot import domain_available
from config import API_KEY_NAMECHEAP, API_USER_NAMECHEAP, BOT_TOKEN, CLIENT_IP
from handlers import routers
from middlewares.block_check import BlockCheckMiddleware
# from outboxes.domains import auto_distribute_domains
# from outboxes.sundry import ssl_enable_with_retries
# from utils.database.services.domain import create_domain, update_domain_server_id
# from utils.schemas.domain_db import DomainCreateSchema, DomainProvider


async def main() -> None:
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_routers(*routers)
    dp.message.middleware(BlockCheckMiddleware())
    dp.callback_query.middleware(BlockCheckMiddleware())
    # print(await get_domain_info(api_user=API_USER_NAMECHEAP, 
    #                             api_key=API_KEY_NAMECHEAP,
    #                             api_username=API_USER_NAMECHEAP, 
    #                             api_client_ip=CLIENT_IP, 
    #                             domain="PlayRushWorld.it.com"))

    # domain_data = DomainCreateSchema(
    #                 user_id=1082965579,                    
    #                 domain_name='PlayRushWorld.it.com',
    #                 domain_provider=DomainProvider.NAMECHEAP,
    #                 domain_id=93380052,
    #             )
    
    # crated_domain_in_db = await create_domain(domain_data)
    # print(crated_domain_in_db)  

    # print(await auto_distribute_domains(1082965579, ['93381099', '93385561']))   
    # print(await update_domain_server_id(93385561, 'a315e4b7-008f-4d35-afd2-ca4cd15ea6b8'))
    # asyncio.create_task(
    # ssh_ip: str, ssh_password: str, hestia_username: str, domain: str
    # await enable_ssl_for_domain(
    #         ssh_ip="65.20.103.39",
    #         ssh_password="Vd5]8][jA)UaLT8L",
    #         hestia_username="admin",
    #         domain="arcadegalaxy.site",
    #         # created_domain_id="93380150"
    #     )
    # print(await get_user_balance(api_key='49R6s6h6PRo8Vy07Q9E8dG8Ml7y16X6v7o7C718f'))
    # print(await domain_available(
    #     api_key='49R6s6h6PRo8Vy07Q9E8dG8Ml7y16X6v7o7C718f',
    #     domain='NextLevelFun.vip'
    # ))
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())

