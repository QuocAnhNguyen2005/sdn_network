# ip_handler.py
from pox.lib.addresses import IPAddr

class IPHandler:
    def __init__(self, dpid):
        self.dpid = dpid
        # Routing Table don gian (Static)
        # Format: {Subnet: (NextHop_IP, Out_Port)}
        # Luu y: Port phai match voi Topology Mininet
        self.routing_table = {}
        self.setup_routes()

    def setup_routes(self):
        # Cau hinh dua theo topology s1-s2-s3
        if self.dpid == 1: # S1 (10.0.1.1)
            self.routing_table['10.0.1.0/24'] = (None, 1) # Local subnet (Host h1, h2 o port 1,2) - Logic o duoi se xu ly
            self.routing_table['10.0.2.0/24'] = (IPAddr('10.0.2.1'), 3) # Via S2
            self.routing_table['10.0.3.0/24'] = (IPAddr('10.0.2.1'), 3) # Via S2

        elif self.dpid == 2: # S2 (10.0.2.1)
            self.routing_table['10.0.2.0/24'] = (None, 1) # Local
            self.routing_table['10.0.1.0/24'] = (IPAddr('10.0.1.1'), 3) # Via S1
            self.routing_table['10.0.3.0/24'] = (IPAddr('10.0.3.1'), 4) # Via S3

        elif self.dpid == 3: # S3 (10.0.3.1)
            self.routing_table['10.0.3.0/24'] = (None, 1) # Local
            self.routing_table['10.0.1.0/24'] = (IPAddr('10.0.2.1'), 3) # Via S2 (qua S2)
            self.routing_table['10.0.2.0/24'] = (IPAddr('10.0.2.1'), 3) # Via S2

    def get_next_hop(self, dst_ip):
        # Longest prefix match (Simplified for this lab)
        for subnet, (next_hop, port) in self.routing_table.items():
            # Kiem tra neu IP thuoc subnet (day la gia lap, ban can dung thu vien IPNetwork de chinh xac hon)
            # O day check don gian prefix
            nw_prefix = subnet.split('.')[0:3] # ['10','0','1']
            dst_prefix = str(dst_ip).split('.')[0:3]
            
            if nw_prefix == dst_prefix:
                if next_hop is None:
                    return "LOCAL", port # Packet cho host trong mang LAN cua router
                return next_hop, port # Packet can forward sang Router khac
        
        return None, None