import time
from core.ticketbot import TicketBot
from logger.logger import logger

class DaimaiBot(TicketBot):
    """
    大麦Bot
    绝大部分依靠resource id、上下层关系来定位

    """

    def __init__(self, app="damai", serial=None) -> None:
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

    def ticket_check(self, ticket_tier, target_tier, coop_tier, magic_word):
        """
        刷票程序V3（V1点票价，好像没用）
        V1: 循环点击两个门票（好像是没作用，文件最下面留了个备份）
        V2：循环点击两个场次（有用，但是需要sleep至少4-5s，不知道是不是个例，待验证）
        V3：最原始的法子：出去再进来

        """
        ticket_num = len(self.config.buyer.info)
        total_price = ticket_num * self.config.ticket.target_price
        while True:
            # 点击场次
            self.sel_children(self.damai_perform_flow, ticket_tier, "android.view.ViewGroup").click()
            # 点击票价
            self.sel_children(self.damai_price_flow, target_tier, "android.widget.FrameLayout").click()
            time.sleep(0.05)
            if self.sel_by_text(magic_word).exists:
                if ticket_num > 1:
                    if not self.sel_by_text(total_price).exists:
                        logger.info("余票不足{0}张，跳过".format(ticket_num))
                        self.dev.press("back")
                        self.sel_by_resid("cn.damai:id/trade_project_detail_purchase_status_bar_container_fl").click()
                        continue
                logger.info("刷出票价：{0}档，尝试进入下单页面".format(target_tier))
                return True
            else:
                self.dev.press("back")
                self.sel_by_resid("cn.damai:id/trade_project_detail_purchase_status_bar_container_fl").click()

    def order_workflow(self):
        """
        下单流程的函数
        主要功能：点击确定→下单→alter check（需再循环一次return False，下单完成、出错etc return True）

        """
        # 点击确定
        self.sel_by_resid("cn.damai:id/btn_buy_view").click()
        # 等待loading消失
        if self.sel_by_resid("cn.damai:id/uikit_loading_icon").exists:
            self.sel_by_resid("cn.damai:id/uikit_loading_icon").wait_gone(10)
        while True:
            # 点击提交订单
            self.sel_by_text("实名观演人").wait(10)
            self.sel_by_resid("cn.damai:id/bottom_layout").child(index=7, className="android.widget.FrameLayout").click()
            hint = self.alert_check(["继续尝试", "我知道了"], 10)
            if hint == "继续尝试":
                logger.info("出现'{0}'弹窗，继续运行...".format(hint))
                self.screenshot()
                self.sel_by_text(hint).click()
                continue
            elif hint == "我知道了":
                logger.info("出现'{0}'弹窗，继续运行...".format(hint))
                self.screenshot()
                self.sel_by_text(hint).click()
                return False
            # 还少支付界面的提示
            else:
                logger.info("未知情况（可能抢到了，可能出错了），请查看截图")
                self.screenshot()
                return True

    def damai_presale(self):
        """
        大麦预售流程
        0、预先选好场次、票档、观演人
        1、进入预售页面
        2、运行脚本
        
        """
        logger.info("=== 大麦预售流程 ===")
        # 定时运行
        if self.trigger(self.config.scheduler.trigger):
            # 点击立即预定
            self.sel_by_resid("cn.damai:id/trade_project_detail_purchase_status_bar_container_fl").click()
            while True:
                # 开始下单
                if self.order_workflow():
                    return

    def damai_encore(self):
        """
        大麦回流票流程V2（预售时填好人数的话，不用再选票数和观演人的，去掉相关流程）
        1、预售时选好观演人
        2、进入选票（刷票）页面
        3、运行脚本
        
        """
        logger.info("=== 大麦回流票流程 ===")
        while True:
            # 查库存
            if self.ticket_check(self.config.ticket.ticket_tier, self.config.ticket.target_tier, self.config.ticket.coop_tier, "价格明细"):
                # 开始下单
                if self.order_workflow():
                    return

    def damai_add_buyer(self):
        """添加观演人，需从'我的'界面开始"""
        self.sel_by_text("观演人").click()
        for name, info in self.config.buyer.info.items():
            logger.info("开始添加观演人，姓名：{0}，身份证：{1}".format(name, info[0]))
            self.sel_by_text("添加新观演人").click()
            self.sel_by_text("请填写观演人姓名").click()
            self.sel_by_text("请填写观演人姓名").send_keys(name)
            self.sel_by_text("请填写证件号码").click()
            self.sel_by_text("请填写证件号码").send_keys(info[0])
            self.dev.press("back")
            self.sel_by_index(0, "android.widget.CheckBox").click()
            self.sel_by_text("确定").click()
            time.sleep(1)