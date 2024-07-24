import time
from core.ticketbot import TicketBot
from logger.logger import logger

class MaoyanBot(TicketBot):
    """
    猫眼Bot
    看起来用text都能定位，先写出来之后来更新

    """

    def __init__(self, app="maoyan", serial=None) -> None:
        super().__init__(app, serial)

    def alert_check(self, hint=[], timeout=10):
        """检测弹窗，默认timeout=10s"""
        now_time = time.time
        start_time = now_time()
        while True:
            for word in hint:
                if self.sel_by_text(word).exists:
                    return word
            if now_time() - start_time >= timeout:
                logger.info("弹窗检测超时")
                return None

    def maoyan_presale(self):
        """
        猫眼预售流程
        1、预先选好场次、票档、观演人
        2、进入预售页面
        3、运行脚本
        
        """
        logger.info("=== 猫眼预售流程 ===")
        if self.trigger(self.config.scheduler.trigger):
            # 点击购票（看起来会有几种情况：立即购票、特惠购票；先观察观察，以后更新）
            self.sel_by_text("立即预订").click()
            while True:
                # 点击确定
                self.sel_by_text("确认").click()
                while True:
                    # 等待页面载入
                    self.sel_by_text("应付").wait(10)
                    # 点击提交
                    self.sel_by_text("立即支付").click()
                    # 记得回来改
                    hint = self.alert_check(["继续尝试", "我知道了"], 10)
                    if hint == "继续尝试":
                        logger.info("出现'{0}'弹窗，继续运行...".format(hint))
                        self.dev.screenshot("./image/{0}.jpg".format(time.strftime("%Y%m%d-%H%M%S")))
                        self.sel_by_text(hint).click()
                        continue
                    elif hint == "我知道了":
                        logger.info("出现'{0}'弹窗，继续运行...".format(hint))
                        self.dev.screenshot("./image/{0}.jpg".format(time.strftime("%Y%m%d-%H%M%S")))
                        self.sel_by_text(hint).click()
                        break
                    # 还少支付界面的提示
                    else:
                        logger.info("未知情况（可能抢到了，可能出错了），请查看截图")
                        self.dev.screenshot("./image/{0}.jpg".format(time.strftime("%Y%m%d-%H%M%S")))
                        return

    def ticket_check(self, ticket_tier, target_tier, coop_tier, magic_word):
        """
        刷票程序V2
        V1：先用点击票价来试试（缺票的票价点起来是直接弹窗的，实际上没有作用）
        V2：点击场次刷票，点击场次和票价都会出loading，猜测都会做余票检测

        """
        while True:
            # 点击场次
            self.sel_by_text(ticket_tier).click()
            # 上滑
            self.dev.swipe_ext("up", scale=0.9)
            # 点击目标票价
            self.sel_by_text(target_tier).click()
            time.sleep(0.1)
            # 弹缺票提示：无票，否则可下单
            if self.sel_by_text("若不是您的常用手机号").exists:
                # 这个值有点儿怪，估计是随机的，再观察观察
                self.sel_by_text("QcFQlwZ+7fcxb+GN3Y6bdOtQkI8JRe2ROKg9Poe6R+0f8AF8Bj7VhD492QAAAABJRU5ErkJggg==").click()
                self.dev.swipe_ext("down", scale=0.9)
            else:
                logger.info("刷出票价：{0}，尝试进入下单页面".format(target_tier))
                return True

    def maoyan_encore(self):
        """
        猫眼回流票流程
        1、预售时选好观演人
        2、进入选票（刷票）页面
        3、运行脚本

        """
        logger.info("=== 猫眼回流票流程 ===")
        while True:
            if self.ticket_check(self.config.ticket.ticket_tier, self.config.ticket.target_tier, self.config.ticket.coop_tier, "总计"):
                # 点确认
                self.sel_by_text("确认").click()
                # 等待页面载入
                self.sel_by_text("应付").wait(10)
                # 点击提交
                self.sel_by_text("立即支付").click()
                # 记得回来改
                hint = self.alert_check(["继续尝试", "我知道了"], 10)
                if hint == "继续尝试":
                    logger.info("出现'{0}'弹窗，继续运行...".format(hint))
                    self.dev.screenshot("./image/{0}.jpg".format(time.strftime("%Y%m%d-%H%M%S")))
                    self.sel_by_text(hint).click()
                    continue
                elif hint == "我知道了":
                    logger.info("出现'{0}'弹窗，继续运行...".format(hint))
                    self.dev.screenshot("./image/{0}.jpg".format(time.strftime("%Y%m%d-%H%M%S")))
                    self.sel_by_text(hint).click()
                    break
                # 还少支付界面的提示
                else:
                    logger.info("未知情况（可能抢到了，可能出错了），请查看截图")
                    self.dev.screenshot("./image/{0}.jpg".format(time.strftime("%Y%m%d-%H%M%S")))
                    return

    def maoyan_add_buyer(self):
        """添加用户函数，需要从'我的'页面开始"""
        self.dev.swipe_ext("up", scale=0.9)
        # 点击观影人信息
        self.sel_by_text("观演人信息").click()
        for name, info in self.config.buyer.info.items():
            self.sel_by_resid("com.sankuai.movie:id/dmh").wait(10)
            time.sleep(2)
            logger.info("开始添加观演人，姓名：{0}，身份证：{1}".format(name, info[0]))
            # 点击添加
            self.sel_by_text("添加").click()
            # 输入姓名
            input = self.dev(textContains="演出").child(index=0, className="android.view.View").child(index=1, className="android.widget.EditText")
            input.click()
            input.send_keys(name)
            self.dev.press("back")
            # 输入身份证
            input = self.dev(textContains="演出").child(index=2, className="android.view.View").child(index=1, className="android.widget.EditText")
            input.click()
            input.send_keys(info[0])
            self.dev.press("back")
            # 点击确定
            self.sel_by_text("确定").click()