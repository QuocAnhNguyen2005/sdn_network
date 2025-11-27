# monitor.py
from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.recoco import Timer

log = core.getLogger()

class Monitor:
    def __init__(self, connection):
        self.connection = connection
        # Gui request moi 5s
        Timer(5, self._request_stats, recurring=True)

    def _request_stats(self):
        # Gui yeu cau thong ke port/flow
        self.connection.send(of.ofp_stats_request(body=of.ofp_flow_stats_request()))
        # self.connection.send(of.ofp_stats_request(body=of.ofp_port_stats_request()))

    def handle_flow_stats(self, event):
        # Xu ly ket qua tra ve
        for f in event.stats:
            # In ra so bytes gui nhan cua cac flow
            if f.match.nw_src and f.match.nw_dst:
                 log.info("Stats: %s -> %s : %s bytes, %s packets", 
                          f.match.nw_src, f.match.nw_dst, f.byte_count, f.packet_count)