# controller.py
from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.packet.ethernet import ethernet
from pox.lib.packet.ipv4 import ipv4
from pox.lib.packet.arp import arp
from pox.lib.addresses import IPAddr, EthAddr

# Import modules
from firewall import Firewall
from arp_handler import ARPHandler
from ip_handler import IPHandler
from flow_installer import FlowInstaller
from monitor import Monitor

log = core.getLogger()

class SDNRouter(object):
    def __init__(self, connection):
        self.connection = connection
        self.dpid = connection.dpid
        self.mac = EthAddr("00:00:00:00:00:0%s" % self.dpid) # Fake MAC cho Router s1=..01
        
        # Dinh nghia IP Gateway cho tung switch
        if self.dpid == 1: self.ip = IPAddr("10.0.1.1")
        elif self.dpid == 2: self.ip = IPAddr("10.0.2.1")
        elif self.dpid == 3: self.ip = IPAddr("10.0.3.1")
        
        # Khoi tao modules
        self.firewall = Firewall()
        self.arp_handler = ARPHandler()
        self.ip_handler = IPHandler(self.dpid)
        self.flow_installer = FlowInstaller()
        self.monitor = Monitor(connection)
        
        # Lang nghe su kien
        connection.addListeners(self)

    def _handle_PacketIn(self, event):
        packet = event.parsed
        if not packet.parsed: return
        
        # 1. Firewall Check
        if not self.firewall.check_access(packet, event.port):
            return # Drop packet

        # 2. Xu ly ARP
        if packet.type == ethernet.ARP_TYPE:
            # Goi ham xu ly ARP
            queued_packets = self.arp_handler.handle_arp(packet, event, self.ip, self.mac)
            if queued_packets:
                # Neu co packet dang doi ARP reply nay, gui chung di
                for pkt_event in queued_packets:
                    self._forward_packet(pkt_event.parsed, pkt_event)
            return

        # 3. Xu ly IP (Routing)
        if packet.type == ethernet.IP_TYPE:
            ip_packet = packet.payload
            
            # Kiem tra Routing Table
            next_hop, out_port = self.ip_handler.get_next_hop(ip_packet.dstip)
            
            if out_port is None:
                log.debug("No route to %s", ip_packet.dstip)
                return

            # Xac dinh Next Hop IP (Neu la LOCAL thi next_hop chinh la dich den)
            target_ip = next_hop if next_hop != "LOCAL" else ip_packet.dstip
            
            # Tra cuu MAC cua target_ip trong ARP Table
            if target_ip in self.arp_handler.arp_table:
                dst_mac = self.arp_handler.arp_table[target_ip]
                self._send_packet(packet, out_port, self.mac, dst_mac, event)
            else:
                # Chua co MAC -> Queue packet va gui ARP Request
                if target_ip not in self.arp_handler.packet_queue:
                    self.arp_handler.packet_queue[target_ip] = []
                self.arp_handler.packet_queue[target_ip].append(event)
                
                # Gui ARP Request
                self._send_arp_request(target_ip, out_port)

    def _send_packet(self, packet, out_port, src_mac, dst_mac, event):
        # Rewrite MAC
        packet.src = src_mac
        packet.dst = dst_mac
        
        msg = of.ofp_packet_out()
        msg.data = packet.pack()
        msg.actions.append(of.ofp_action_output(port=out_port))
        self.connection.send(msg)
        
        # Install Flow de toi uu cho cac goi tin sau
        self.flow_installer.install_flow(self.connection, packet, out_port, src_mac, dst_mac)

    def _send_arp_request(self, target_ip, out_port):
        r = arp()
        r.opcode = arp.REQUEST
        r.hwdst = EthAddr("ff:ff:ff:ff:ff:ff")
        r.protodst = target_ip
        r.hwsrc = self.mac
        r.protosrc = self.ip
        
        eth = ethernet(type=ethernet.ARP_TYPE, src=self.mac, dst=r.hwdst)
        eth.set_payload(r)
        
        msg = of.ofp_packet_out()
        msg.data = eth.pack()
        msg.actions.append(of.ofp_action_output(port=out_port))
        self.connection.send(msg)

    def _handle_FlowStatsReceived (self, event):
        self.monitor.handle_flow_stats(event)

def launch():
    def start_switch(event):
        SDNRouter(event.connection)
    core.openflow.addListenerByName("ConnectionUp", start_switch)