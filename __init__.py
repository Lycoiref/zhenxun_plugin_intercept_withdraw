# 通过将撤回的消息发送给超级用户，让超级用户处理撤回的消息
import json

from nonebot import get_bot
from nonebot.log import logger
from nonebot import on_message, on_notice
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, Message, GroupMessageEvent, GroupRecallNoticeEvent
from nonebot.params import CommandArg
from utils.utils import get_message_img

# 真寻规范
__zx_plugin_name__ = "消息防撤回"
__plugin_usage__ = """
usage：
    消息防撤回：
    当消息被撤回或收到闪照时自动触发；
    将撤回的消息/闪照发送给超级用户；
    ————麻麻再也不怕我错过群里的女装照片了！
""".strip()
__plugin_des__ = "保存撤回的消息，收到闪照时，将闪照发送给超级用户"
__plugin_settings__ = {
    "limit_superuser": True,
    "cmd": ["防撤回", "闪照解析"],
}
__plugin_type__ = ("常规插件",)
__plugin_version__ = 0.1
__plugin_author__ = "HDU_Nbsp"
__plugin_task__ = {"intercept_withdraw", "消息防撤回"}

if_withdraw = on_notice(priority=1, block=False)
flash_pic = on_message(priority=1, block=False)  # 闪照事件监听


# 检测撤回消息
@if_withdraw.handle()
async def if_withdraw_handle(bot: Bot, event: GroupRecallNoticeEvent):  # 此处event不知道应该调用哪个，所以暂时不用
    if event.notice_type == "group_recall":
        # 获取撤回消息的消息id
        recall_message_id = event.message_id
        # 获取撤回消息的消息内容
        recall_message_content = await bot.get_msg(message_id=recall_message_id)
        print(recall_message_content["message"])
        # 将撤回消息发送给所有超级用户
        for superuser in bot.config.superusers:
            await bot.send_private_msg(
                user_id=superuser,
                message=f"{event.user_id} 在群聊 {event.group_id} 撤回了一条消息\n"
                        f"撤回消息内容：\n{recall_message_content['message']}"
            )


# 检测闪照
@flash_pic.handle()
async def if_withdraw_handle(bot: Bot, event: GroupMessageEvent):
    # 检测是否是闪照
    message_dict = json.loads(event.json())
    print(message_dict)
    msg_type = message_dict["raw_message"]
    # 正则对比字符串中是否有type=flash
    if "type=flash" in msg_type:
        print("收到闪照")
        msg_id = message_dict["message_id"]  # 消息id
        # 获取闪照地址
        flash_url = await bot.get_msg(message_id=msg_id)
        flash_url = flash_url["message"]
        # 将闪照转换为图片
        # 使用,对字符串进行分割
        flash_url_list = flash_url.split(",")
        filename = flash_url_list[1].split("=")[-1]
        img_url = flash_url_list[2].split("url=")[-1]
        print(filename, img_url)
        # 生成消息
        msg = {
            'type': 'image',
            'data': {
                'file': filename,
                'url': img_url,
                'subType': '0'
            }
        }
        #  将图片发送给超级用户
        for superuser in bot.config.superusers:
            await bot.send_private_msg(
                user_id=superuser,
                message=f"收到来自群{message_dict['group_id']}的闪照"
            )
            await bot.send_private_msg(
                user_id=superuser,
                message=msg
            )
