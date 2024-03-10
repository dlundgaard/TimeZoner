import pathlib
import sys

# pip.exe install -r ./requirements.txt -t ./lib
sys.path.append(str(pathlib.Path(__file__).parent.parent.joinpath("lib")))

import flowlauncher
import requests
import datetime
import logging
import json

logging.basicConfig(
    level=logging.INFO,
    filename="plugin.log",
    encoding="utf-8",
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

TIME_ZONES = [
    "Europe/London",
    "America/Indianapolis",
    "America/New_York",
    "America/Los_Angeles",
    "America/Toronto",
]
API_RESOURCE = "http://worldtimeapi.org/api/timezone/"

class DisplayTimeZones(flowlauncher.FlowLauncher):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.overwrite_existing = bool(self.settings.get("overwrite_existing"))

    def retrieve_data(self, zone):
        response = requests.get(API_RESOURCE + zone).json()
        logging.info(json.dumps(response, indent = 4))
        return response

    def get_zone_info(self, zone):
        response = self.retrieve_data(zone)
        timestamp = datetime.datetime.strptime(response["datetime"], "%Y-%m-%dT%H:%M:%S.%f%z")
        return dict(
            Title = f"""{str(timestamp.strftime("%H:%M"))} ({(int(datetime.datetime.now().astimezone().utcoffset().total_seconds()) + response["raw_offset"]) // 3600:+})""",
            SubTitle = f"""{zone.split("/")[1].replace("_", " ")} ({response["abbreviation"]})""",
            IcoPath = "assets/icon.png",
            JsonRPCAction = dict(
                method = "Flow.Launcher.ChangeQuery",
                parameters = [zone, True]
            ),
            ContextData = zone,
            score = 0
        )

    def query(self, query):
        return [self.get_zone_info(zone) for zone in TIME_ZONES]

    def context_menu(self, zone):
        response = self.retrieve_data(zone)
        return [
            dict(
                Title = f"""{zone.split("/")[1].replace("_", " ")} ({response["abbreviation"]})""",
                SubTitle = "Daylight savings active" if response["dst"] else "Daylight savings inactive",
                IcoPath = "assets/icon.png",
                JsonRPCAction = dict(
                    method = "Flow.Launcher.ChangeQuery",
                    parameters = [zone, True]
                ),
                ContextData = zone,
                score = 0
            )
        ]
