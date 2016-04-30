from TxValidateNode import *

class Block:
    def __init__(self, prev):
        self.previoushash = prev
        
recv = {
    1: Block(None),
    2: Block(1),
    3: Block(2),
    4: Block(3),
    5: Block(4),
    6: Block(5)
}

local = {
    1: Block(None),
    2: Block(1),
    9: Block(2),
    10: Block(9)
}

recv_start = 6
local_start = 10
c, l = TxValidateNode.find_chain_intersection(local, recv, recv_start)
print(c)
print(l)
l = TxValidateNode.count_chain_sublen(local, local_start, c)
print(l)