import json
# from sched import scheduler
from time import time, sleep
from datetime import datetime
from urllib import request
from os import path
from Mod import Mod
from discord_webhooks import DiscordWebhooks
from config import webhook_url, api_url
print("START")

SLEEP_S = 5 * 60

class DiscordColor(object):
    Red = 0xFB0000
    Green = 0x2ABD26

def saveJSON(file, data, encoder = None):
    with open(file, 'w') as outfile:
        json.dump(data, outfile, cls=encoder, indent=4)
def loadJSON(file):
    if not path.isfile(file):
        return dict()
    with open(file) as json_file:
        return json.load(json_file)

class MyEncoder(json.JSONEncoder):
    def default(self, o):
        return o.__dict__

def modfromMod(mod, client = None):
    modClass = Mod()
    if "name" in mod: modClass.name = mod["name"]
    if "version" in mod: modClass.version = mod["version"]
    if "author" in mod: modClass.author = mod["author"]
    if "downloadLink" in mod: modClass.downloadLink = mod["downloadLink"]
    if "type" in mod: modClass.type = mod["type"]
    if client:
        modClass.User.displayName = client["displayname"]
        modClass.User.id = client["id"]
    return modClass

class VRCMNWatcher(object):
    webhook = DiscordWebhooks(webhook_url)

    last_stats = dict()
    last_mods = list()
    run = 0

    last_stats_file = "stats.cache.json"
    last_mods_file = "mods.json"

    def __init__(self):
        print("INIT")
        self.last_stats = loadJSON(self.last_stats_file)
        self.last_mods = loadJSON(self.last_mods_file)

    # s = scheduler(time, sleep); sched_delay = 3
    def do_something(self, sc = None):
        self.run += 1
        print("Scheduler triggered (", self.run, ")")
        newStats = self.getStats()
        # if self.run == 3: newStats["clientCount"] = 0 # Todo: remove
        self.checkStats(newStats) # if self.run > 1:
        self.last_stats = newStats
        if self.last_stats: saveJSON(self.last_stats_file, self.last_stats)
        if self.last_mods and len(self.last_mods) > 0: saveJSON(self.last_mods_file, self.last_mods, encoder=MyEncoder)
        # s.enter(sched_delay, 1, do_something, (sc,))

    def checkStats(self, stats):
        print("LastStats:", self.last_stats)
        if "clientCount" not in self.last_stats: return
        possible_outage = False
        if stats["clientCount"] < 1 and self.last_stats["clientCount"] > 0: possible_outage = True
        if stats["serverCount"] < 1 and self.last_stats["serverCount"] > 0: possible_outage = True
        if possible_outage:
            keys = ["time", "clientCount", "serverCount", "rolebackCount", "currentRequestsAlive", "currentUpdatesAlive"]
            content = "```diff"
            for key in keys: content += f"\n{key}:\n- {self.last_stats[key]}\n+ {stats[key]}"
            title = "Possible Server Outage detected!"
            self.sendWH(content=title+"\n<@&548161183186812958>", description=content+"\n```", title=title, color=DiscordColor.Red) # 440095897679036416
        self.checkMods(stats)

    def checkMods(self, stats):
        print("Last Mods:", len(self.last_mods), self.last_mods)
        newMods = (self.parseMods(stats))
        print("Mods:", len(newMods), newMods)
        printMods = (len(self.last_mods) > 0)
        for mod in newMods:
            nameExists = any(mod.isSameName(d) for d in self.last_mods)
            print(mod, nameExists)
            if not nameExists:
                self.last_mods.append(mod)
                if printMods: self.sendWH(mod.fullstr(), title="New mod found", color=DiscordColor.Green)

    def parseMods(self, stats):
        mods = list()
        # key = frozenset(dict_key.items())
        for client in stats["clients"]:
            if not "modlist" in client: continue
            for mod in client["modlist"]:
                if not "name" in mod: continue
                if not any(d.name == mod["name"] for d in mods):
                    mods.append(modfromMod(mod, client))
        return mods

    def getStats(self):
        with request.urlopen(api_url) as url:
            string = url.read().decode()
            print("Got new stats:", string)
            return json.loads(string)

    def sendWH(self, description="", title="", content="", url="", color=0x00000):
        self.webhook.set_content(content=content, title=title, description=description, url=url,color=color, timestamp=str(datetime.utcnow()))
        self.webhook.send()

vrcnmwatcher = VRCMNWatcher()
active = True
while active:
    vrcnmwatcher.do_something()
    sleep(SLEEP_S)

# s.enter(sched_delay, 1, do_something, (s,)); s.run()
print("END")