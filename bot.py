import nonebot
from nonebot.adapters.onebot.v11 import Adapter as ONEBOT_V11Adapter

nonebot.init()
app = nonebot.get_asgi()

driver = nonebot.get_driver()

driver.register_adapter(ONEBOT_V11Adapter)

nonebot.load_plugin("src.plugins.master_bot")

if __name__ == "__main__":
    nonebot.run(app="__mp_main__:app", host="0.0.0.0", port=64000)