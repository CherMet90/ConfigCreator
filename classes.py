class Port:

    def __repr__(self):
        return str("Port: " + self.number + " Desc: " + self.description + " Serv: " + self.service)

    def __str__(self):
        return str(self.number + ";" + self.description + ";" + self.service)

    def __init__(self, port, description: str, service_type=""):
        """Constructor"""
        self.number = str(port)
        self.description = description
        self.service = service_type

    def create_port(self):
        command = 'config ports ' + self.number + ' state enable description "' + self.description + '"\n'
        return command

    def addServiceType(self, service_type: str):
        self.service = service_type


class Vlan:

    def __init__(self, name, vlan_id, untagged="", tagged=""):
        self.name = name
        self.vlan_id = vlan_id
        self.untagged = untagged
        self.tagged = tagged

    def add_tag(self, port):
        self.tagged = port

    def add_untag(self, port):
        self.untagged = port

    def create_vlan(self):
        configVlans = 'create vlan ' + self.name + ' tag ' + self.vlan_id + '\n'
        if self.untagged != "":
            configVlans += 'config vlan ' + self.name + ' add untag ' + self.untagged + '\n'
        if self.tagged != "":
            configVlans += 'config vlan ' + self.name + ' add tag ' + self.tagged + '\n'
        return configVlans

