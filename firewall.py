# firewall.py
from pox.lib.packet.ipv4 import ipv4
from pox.lib.packet.tcp import tcp
from pox.lib.packet.udp import udp

class Firewall:
    def __init__(self):
        # Rule format: (DIRECTION, PROTOCOL, PORT, ACTION)
        # DIRECTION o day minh xu ly logic dua vao in_port
        self.rules = [
            ("TCP", 22, "DENY"),   # Block SSH
            ("TCP", 80, "DENY"),   # Block HTTP
            ("UDP", 53, "ALLOW")   # Allow DNS
        ]

    def check_access(self, packet, in_port):
        # Chi check IP packets
        ip_packet = packet.find('ipv4')
        if not ip_packet:
            return True # Allow non-IP (like ARP)

        protocol = None
        dst_port = 0
        
        tcp_packet = packet.find('tcp')
        udp_packet = packet.find('udp')

        if tcp_packet:
            protocol = "TCP"
            dst_port = tcp_packet.dstport
        elif udp_packet:
            protocol = "UDP"
            dst_port = udp_packet.dstport
        else:
            return True # Allow ICMP or others not in rules

        # Logic kiem tra Rules
        for r_proto, r_port, r_action in self.rules:
            if protocol == r_proto and dst_port == r_port:
                if r_action == "DENY":
                    print "Firewall: BLOCKED %s port %s" % (protocol, dst_port)
                    return False
                elif r_action == "ALLOW":
                    return True
        
        # Mac dinh Allow neu khong match rule Deny nao
        return True