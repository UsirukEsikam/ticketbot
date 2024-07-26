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
        self.name = config.get("ghost_name")

class BuyerConfig(object):
    def __init__(self, config) -> None:
        self.info = dict(zip(config.get("buyer_name"), config.get("buyer_id")))

class TicketConfig(object):
    def __init__(self, config) -> None:
        self.price = config.get("ticket_price")
        self.tier = config.get("ticket_tier")
        self.date = config.get("ticket_date")

class SchedulerConfig(object):
    def __init__(self, config) -> None:
        self.trigger = datetime.strptime(config.get("trigger"), "%Y-%m-%d %H:%M:%S.%f")