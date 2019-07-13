from datetime import datetime

class Mod(object):
    name = ""
    version = ""
    author = ""
    downloadLink = ""
    type = ""
    class User(object):
        displayName = ""
        id = ""
    firstSeen = datetime.utcnow()

    def fullstr(self):
        return f"""
```yaml
Name: {self.name}
Version: {self.version}
Author: {self.author}
Download: {self.downloadLink}
Type: {self.type}
User: {self.User.displayName} ({self.User.id})
```
        """
    def isSame(self, other):
        if isinstance(other, Mod):
            return (self.name == other.name and
                    self.version == other.version and
                    self.author == other.author and
                    self.downloadLink == other.downloadLink and
                    self.type == other.type)
        return NotImplemented
    def isSameName(self, other):
        if isinstance(other, Mod): return self.name == other.name
        return NotImplemented
    def __repr__(self): return f"{self.name} v{self.version} by {self.author} for {self.type}"