# multi_router_topo.py
from mininet.topo import Topo

class MultiRouterTopo(Topo):
    def build(self):
        # Tao 3 Switch (Router)
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')

        # Tao Hosts cho Subnet A (10.0.1.x)
        h1 = self.addHost('h1', ip='10.0.1.10/24', defaultRoute='via 10.0.1.1')
        h2 = self.addHost('h2', ip='10.0.1.11/24', defaultRoute='via 10.0.1.1')
        
        # Tao Hosts cho Subnet B (10.0.2.x)
        h3 = self.addHost('h3', ip='10.0.2.10/24', defaultRoute='via 10.0.2.1')
        h4 = self.addHost('h4', ip='10.0.2.11/24', defaultRoute='via 10.0.2.1')

        # Tao Hosts cho Subnet C (10.0.3.x)
        h5 = self.addHost('h5', ip='10.0.3.10/24', defaultRoute='via 10.0.3.1')
        h6 = self.addHost('h6', ip='10.0.3.11/24', defaultRoute='via 10.0.3.1')

        # Lien ket Host vao Switch
        # s1: port 1->h1, port 2->h2
        self.addLink(s1, h1)
        self.addLink(s1, h2)

        # s2: port 1->h3, port 2->h4
        self.addLink(s2, h3)
        self.addLink(s2, h4)

        # s3: port 1->h5, port 2->h6
        self.addLink(s3, h5)
        self.addLink(s3, h6)

        # Lien ket giua cac Switch (Backbone)
        # s1-eth3 <-> s2-eth3
        self.addLink(s1, s2) 
        # s2-eth4 <-> s3-eth3 (Luu y port number co the thay doi, can check bang lenh net trong mininet)
        self.addLink(s2, s3)

topos = { 'multirouter': ( lambda: MultiRouterTopo() ) }