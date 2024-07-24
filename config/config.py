import yaml
from datetime import datetime

class Config(object):
    def __init__(self, config_path) -> None:
        self.config = self.read_config(config_path)
        self.ghost = GhostConfig(self.config.get("ghost", {}))
        self.buyer = BuyerConfig(self.config.get("buyer", {}))
        self.ticket = TicketConfig(self.config.get("ticket", {}))
        self.scheduler = SchedulerConfig(self.config.get("scheduler", {}))

    def read_config(self, path):
        with open(path, 'r', encoding="utf8") as file:
            return yaml.safe_load(file)

class GhostConfig(object):
    def __init__(self, config) -> None:
        self.info = dict(zip([config.get("ghost_name")], [config.get("ghost_mobile")]))

class BuyerConfig(object):
    def __init__(self, config) -> None:
        self.info = dict(zip(config.get("buyer_name"), zip(config.get("buyer_id"), config.get("buyer_mobile"))))

class TicketConfig(object):
    def __init__(self, config) -> None:
        self.target_price = config.get("target_price")
        self.target_tier = config.get("target_tier")
        self.ticket_tier = config.get("ticket_tier")
        self.coop_tier = config.get("coop_tier")

class SchedulerConfig(object):
    def __init__(self, config) -> None:
        self.trigger = datetime.strptime(config.get("trigger"), "%Y-%m-%d %H:%M:%S.%f")