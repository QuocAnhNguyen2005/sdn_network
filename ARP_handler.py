# arp_handler.py
from pox.lib.packet.ethernet import ethernet
from pox.lib.packet.arp import arp
from pox.lib.addresses import EthAddr, IPAddr
from pox.core import core

log = core.getLogger()

class ARPHandler:
    def __init__(self):
        # ARP Cache: {IPAddr: EthAddr}
        self.arp_table = {}
        # Queue cho cac goi tin cho ARP reply: {IPAddr: [packet_event]}
        self.packet_queue = {}

    def handle_arp(self, packet, event, router_ip, router_mac):
        arp_packet = packet.find('arp')
        
        # 1. Hoc MAC tu goi tin den (Learn sender info)
        self.arp_table[arp_packet.protosrc] = arp_packet.hwsrc

        # 2. Xu ly ARP Request (Hoi MAC cua Router Gateway)
        if arp_packet.opcode == arp.REQUEST:
            if arp_packet.protodst == router_ip:
                # Tao ARP Reply
                reply = arp()
                reply.opcode = arp.REPLY
                reply.hwdst = arp_packet.hwsrc
                reply.protodst = arp_packet.protosrc
                reply.hwsrc = router_mac
                reply.protosrc = router_ip
                
                eth = ethernet(type=ethernet.ARP_TYPE, src=router_mac, dst=arp_packet.hwsrc)
                eth.set_payload(reply)
                
                # Gui goi tin di
                msg = of.ofp_packet_out()
                msg.data = eth.pack()
                msg.actions.append(of.ofp_action_output(port = event.port))
                event.connection.send(msg)
                
        # 3. Xu ly ARP Reply (Nhan duoc MAC can tim)
        elif arp_packet.opcode == arp.REPLY:
            # Check xem co packet nao dang doi MAC nay khong
            if arp_packet.protosrc in self.packet_queue:
                waiting_packets = self.packet_queue[arp_packet.protosrc]
                del self.packet_queue[arp_packet.protosrc]
                # Tra ve danh sach packet de Controller xu ly tiep
                return waiting_packets
                
        return None