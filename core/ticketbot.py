import time
import uiautomator2 as u2
from datetime import datetime
from config.config import Config
from logger.logger import logger

class TicketBot(object):
    """抢票脚本基类"""

    def __init__(self, serial, app) -> None:
        # app可选：livelab, damai
        self.app = app
        self.read_config()
        self.init_dev(serial)
        self.init_damai()
        self.init_livelab()

    def read_config(self):
        self.config = Config("config.yaml")
        self.show_initialization_prompt()

    def init_dev(self, serial):
        self.dev = u2.connect(serial)

    def init_damai(self):
        # 场次的layout
        self.damai_perform_flow = self.sel_by_resid("cn.damai:id/project_detail_perform_flowlayout")
        # 价格的layout
        self.damai_price_flow = self.sel_by_resid("cn.damai:id/project_detail_perform_price_flowlayout")

    def init_livelab(self):
        pass

    def sel_by_text(self, text):
        return self.dev(textContains=text)

    def sel_by_desc(self, desc):
        return self.dev(descriptionContains=desc)

    def sel_by_resid(self, resource_id):
        return self.dev(resourceId=resource_id)

    def sel_by_index(self, index, class_name):
        return self.dev(index=index, className=class_name)

    def sel_children(self, parent, index, class_name):
        return parent.child(index=index, className=class_name)

    def trigger(self, trigger):
        now_time = datetime.now
        while True:
            if now_time() >= trigger:
                logger.info("到达预定时间，开始抢票...")
                self.dev.screen_on()
                return True
            else:
                time.sleep(0.2)

    def show_initialization_prompt(self):
        # ASCII Art
        print(r"""


___________.__        __              __ __________        __   
\__    ___/|__| ____ |  | __ ____   _/  |\______   \ _____/  |_ 
  |    |   |  |/ ___\|  |/ // __ \  \   __\    |  _//  _ \   __\
  |    |   |  \  \___|    <\  ___/   |  | |    |   (  <_> )  |  
  |____|   |__|\___  >__|_ \\___  >  |__| |______  /\____/|__|  
                   \/     \/    \/               \/             


        """)
        # 输出配置信息，二次确认用
        logger.info("请认真核对配置信息：")
        logger.info("用户信息：{0}".format(self.config.ghost.info))
        logger.info("金主信息：{0}".format(self.config.buyer.info))
        if self.app == "damai":
            logger.info("目标票价：{0}({1}档)".format(self.config.damai.target_price, self.config.damai.target_tier))
            logger.info("场次：{0}档".format(self.config.damai.ticket_tier))
        elif self.app == "livelab":
            logger.info("目标票价：{0}({1})".format(self.config.livelab.target_price, self.config.livelab.target_tier))
            logger.info("场次：{0}".format(self.config.livelab.ticket_tier))
        else:
            logger.error("app模式选择错误")
        logger.info("开枪时间：{0}".format(self.config.scheduler.trigger))