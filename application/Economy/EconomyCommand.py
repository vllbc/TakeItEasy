import json

from graia.application import GraiaMiraiApplication as Slave, GroupMessage
from graia.application.message.chain import MessageChain as MeCh
from graia.application.message.elements.internal import At, Plain

from . import Economy as EconomyAPI

APP_COMMANDS = ['.MM', '.PM']


async def Economy(app: Slave, message: GroupMessage, commands: list):
    if commands[0] in APP_COMMANDS:
        await commandHandler(app, message, commands)


async def commandHandler(app: Slave, message: GroupMessage, commands: list):
    cmd: str = commands[0]
    msg = []
    if cmd == APP_COMMANDS[0]:
        info: dict = await EconomyAPI.Economy.money(message.sender.id)
        b = Plain(f"\n余额:  {info['balance']}只{EconomyAPI.unit}")
        al = info['credit_pay_adjust'] + EconomyAPI.credit_pay['base_balance']
        c = Plain(f"\n{EconomyAPI.unit}呗:\n  已用额度: {info['credit_pay_use']}\n  总额度: {al}")
        p = Plain(f"\n支付方式: {EconomyAPI.payments[info['payment']]}")
        m = Plain(f"\n.pm 切换支付方式")
        msg = [At(message.sender.id), b, c, p, m]
    if cmd == APP_COMMANDS[1]:
        try:
            if (payment := int(commands[1])) in [1, 3, 2, 4]:
                await EconomyAPI.Economy.payment(message.sender.id, payment)
                msg.append(Plain(f"切换到{EconomyAPI.payments[payment]}"))
            else:
                msg.append(Plain(f"\n{json.dumps(EconomyAPI.payments, ensure_ascii=False)}"))
        except (ValueError, IndexError):
            msg.append(Plain('.pm 1|2|3|4'))
    await app.sendGroupMessage(message.sender.group.id, MeCh.create(msg))


async def notEnough(app: Slave, message: GroupMessage, price: int):
    msg = [At(message.sender.id), Plain(f'\n余额不足:) [.mm]查看余额\n单价{price}只{EconomyAPI.unit}')]
    await app.sendGroupMessage(message.sender.group, MeCh.create(msg))
