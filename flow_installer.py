# flow_installer.py
import pox.openflow.libopenflow_01 as of

class FlowInstaller:
    def install_flow(self, connection, packet, out_port, src_mac, dst_mac):
        msg = of.ofp_flow_mod()
        
        # Match fields
        msg.match = of.ofp_match.from_packet(packet)
        msg.idle_timeout = 10
        msg.hard_timeout = 30
        
        # Actions: Rewrite MAC src/dst va Output
        msg.actions.append(of.ofp_action_dl_addr.set_src(src_mac))
        msg.actions.append(of.ofp_action_dl_addr.set_dst(dst_mac))
        msg.actions.append(of.ofp_action_output(port=out_port))
        
        # Send to switch
        connection.send(msg)