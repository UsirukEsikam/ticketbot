import time
from itertools import cycle
from core.ticketbot import TicketBot
from logger.logger import logger

class LivelabBot(TicketBot):
    """
    纷玩岛Bot
    基本都依靠description字段来定位

    """

    def __init__(self, app="livelab", serial=None) -> None:
        super().__init__(app, serial)

    def alert_check(self, hint=[], timeout=10):
        """检测弹窗，默认timeout=10s"""
        now_time = time.time
        start_time = now_time()
        while True:
            for word in hint:
                if self.sel_by_desc(word).exists:
                    return word
            if now_time() - start_time >= timeout:
                logger.info("弹窗检测超时")
                return None

    def ticket_check(self, ticket_tier, target_tier, coop_tier, magic_word):
        """刷票程序（不断点击两个票价，出现break_word后break，返回True"""
        ticket_num = len(self.config.buyer.info)
        total_price = "￥{0}.00".format(ticket_num * self.config.ticket.target_price)
        # 点击场次
        self.sel_by_desc(ticket_tier).click()
        # 上滑
        self.dev.swipe_ext("up", scale=0.9)
        # 循环池子
        tier_pool = cycle([target_tier, coop_tier])
        # 开始循环
        while True:
            next_tier = next(tier_pool)
            # 点击对应的票价
            self.sel_by_desc(next_tier).click()
            # 如果tier == target_tier，则判断是否出现magic word（可以触发点击确定的提示）
            if next_tier == target_tier:
                time.sleep(0.05)
                if self.sel_by_desc(magic_word).exists:
                    if ticket_num > 1:
                        if not self.sel_by_desc(total_price).exists:
                            logger.info("余票不足{0}张，跳过".format(ticket_num))
                            continue
                    logger.info("刷出票价：{0}，尝试进入下单页面".format(target_tier))
                    return True

    def order_workflow(self):
        """
        下单流程的函数
        主要功能：点击确定→下单→alter check（需再循环一次return False，下单完成、出错etc return True）

        """
        # 点击确认
        self.sel_by_desc("确认").click()
        # 点击提交订单
        self.sel_by_desc("提交订单").click()
        # 查弹窗
        hint = self.alert_check(["请求人数多", "数量不足", "订单中包含已购买"], 10)
        if hint == "请求人数多":
            logger.info("出现'{0}'弹窗，继续运行...".format(hint))
            # self.sel_by_desc("重新选择").click()
            self.dev.click(534, 1538)
            return False
        elif hint == "数量不足":
            logger.info("出现'{0}'弹窗，继续运行...".format(hint))
            # self.sel_by_desc("重新选择").click()
            self.dev.click(534, 1538)
            return True
        elif hint == "订单中包含已购买":
            logger.info("出现'{0}'弹窗，脚本结束".format(hint))
            return True
        elif self.sel_by_desc("确认并支付").exists:
            logger.info("出现支付窗口，脚本结束")
            return True
        else:
            logger.info("未知情况，请查看截图")
            self.screenshot()
            return True

    def livelab_presale(self):
        """
        纷玩岛预售流程
        1、预先选好场次、票档、观演人
        2、进入预售页面
        3、运行脚本

        """
        logger.info("=== 纷玩岛预售流程 ===")
        # 定时启动
        if self.trigger(self.config.scheduler.trigger):
            # 点击立即购买
            self.sel_by_desc("立即购买").click()
            while True:
                # 下单流程
                if self.order_workflow():
                    return

    def livelab_encore(self):
        """
        纷玩岛回流票流程V2（先去掉V1的选票数和选观演人的步骤，八成会记忆，不行再改回来）
        1、预售时选好观演人
        2、进入选票（刷票）页面
        3、运行脚本

        """
        logger.info("=== 纷玩岛回流票流程 ===")
        while True:
            # 查余票
            if self.ticket_check(self.config.ticket.ticket_tier, self.config.ticket.target_tier, self.config.ticket.coop_tier, "购买数量"):
                # 下单流程
                if self.order_workflow():
                    return

    def livelab_add_buyer(self):
        """添加用户函数，需要从'我的'页面开始"""
        self.sel_by_desc("持票人").click()
        for name, info in self.config.buyer.info.items():
            logger.info("开始添加观演人，姓名：{0}，身份证：{1}".format(name, info[0]))
            self.sel_by_desc("新增持票人").click()
            # 输入姓名
            input = self.dev(index=1, className="android.view.View").child(index=2, className="android.view.View").child(className="android.widget.EditText")
            input.click()
            input.send_keys(name)
            self.dev.press("back")
            # 选择身份证类型
            self.dev(index=4, className="android.view.View").click()
            self.sel_by_desc("确认").click()
            # 输入身份证
            input = self.dev(index=1, className="android.view.View").child(index=6, className="android.view.View").child(className="android.widget.EditText")
            input.click()
            input.send_keys(info[0])
            self.dev.press("back")
            # 勾选协议
            self.dev(index=9, className="android.view.View").click()
            # 确定
            self.sel_by_desc("确定").click()
            time.sleep(1)

# if __name__ == "__main__":
#     bot = LivelabBot("6fe00acd")
    # bot.livelab_presale()
    # bot.livelab_encore()
    # bot.livelab_add_buyer()