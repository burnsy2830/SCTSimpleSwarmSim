import threading
import time
from transitions import Machine

# ======= FSM ========
class FSM:
    def on_enter_s0(self):
        print(f"{self.name} → Moving forward")

    def on_enter_s2(self):
        print(f"{self.name} → Turning left")
        self.To()

    def on_exit_s2(self):
        print(f"{self.name} ← Finished turn")

    def on_enter_s3(self):
        print(f"{self.name} → Obstacle or received turn req")
        self.To()

    def on_enter_s1(self):
        print(f"{self.name} → Forward again")


# ======= FSM Setup ========
fsm1 = FSM(); fsm1.name = "drone1"
fsm2 = FSM(); fsm2.name = "drone2"
fsm3 = FSM(); fsm3.name = "drone3"
fsm4 = FSM(); fsm4.name = "drone4"
fsm5 = FSM(); fsm5.name = "drone5"

states = ['s0', 's1', 's2', 's3']
transitions = [
    {'trigger': 'Mf', 'source': 's0', 'dest': 's0'},
    {'trigger': 'No', 'source': 's1', 'dest': 's0'},
    {'trigger': 'Od', 'source': 's0', 'dest': 's1'},
    {'trigger': 'Mf', 'source': 's1', 'dest': 's1'},
    {'trigger': 'Si', 'source': 's0', 'dest': 's2'},
    {'trigger': 'Ri', 'source': 's0', 'dest': 's2'},
    {'trigger': 'To', 'source': 's2', 'dest': 's0'},
    {'trigger': 'Tl', 'source': 's2', 'dest': 's2'},
    {'trigger': 'No', 'source': 's3', 'dest': 's2'},
    {'trigger': 'Od', 'source': 's2', 'dest': 's3'},
    {'trigger': 'Tl', 'source': 's3', 'dest': 's3'},
    {'trigger': 'Si', 'source': 's1', 'dest': 's3'},
    {'trigger': 'Ri', 'source': 's1', 'dest': 's3'},
    {'trigger': 'To', 'source': 's3', 'dest': 's1'},
]

Machine(model=fsm1, states=states, transitions=transitions, initial='s0')
Machine(model=fsm2, states=states, transitions=transitions, initial='s0')
Machine(model=fsm3, states=states, transitions=transitions, initial='s0')
Machine(model=fsm4, states=states, transitions=transitions, initial='s0')
Machine(model=fsm5, states=states, transitions=transitions, initial='s0')



# ======= Shared State Setup ========
state_lock = threading.Lock()
chan_lock = threading.Lock()
shared_state_queue = []
drone_queue = []          
noti1 = [False]
noti2 = [False]
noti3 = [False]
noti4 = [False]
noti5 = [False]
     
def notify(sender):
    if sender == "drone1":
        noti2[0] = True
        noti3[0] = True
        noti4[0] = True
        noti5[0] = True
    
    if sender == "drone2":
        noti1[0] = True
        noti3[0] = True
        noti4[0] = True
        noti5[0] = True

    if sender == "drone3":
        noti1[0] = True
        noti2[0] = True
        noti4[0] = True
        noti5[0] = True

    if sender == "drone4":
        noti1[0] = True
        noti2[0] = True
        noti3[0] = True
        noti5[0] = True

    if sender == "drone5":
        noti1[0] = True
        noti2[0] = True
        noti3[0] = True
        noti4[0] = True





# ======= Threads ========
def simMaster():
    while True:
        event = input("Block? (y/n):")
        if event == "y":
            with state_lock:
                shared_state_queue.append(("Od", "sim"))
        time.sleep(0.5)

def drone1(fsm):
    while True:
        print(f"[drone1] Current state: {fsm.state}")
        with state_lock:
            if noti1[0] and fsm.state == "s0":
                fsm.Ri()
                noti1[0] = False  # reset
                continue  
            if noti1[0] and fsm.state == "s1":
                fsm.Ri()
                noti1[0] = False  # reset
                continue  
            for ev, sender in shared_state_queue:
                if sender != "drone1" and ev == "Sl":
                    print(f"[drone1] Reacting to Sl")
                    fsm.Ri()
                    continue  
                elif sender == "sim" and ev == "Od":
                    print(f"[drone1] Reacting to Od")
                    notify("drone1")
                    fsm.Od()
                    continue 
            if fsm.state == "s1" or fsm.state == "s3":  
                fsm.No() 
            shared_state_queue.clear()
        time.sleep(0.5)

def drone2(fsm):
    while True:
        print(f"[drone2] Current state: {fsm.state}")
        with state_lock:
        
            if noti2[0] and fsm.state == "s0":
                fsm.Ri()
                noti2[0] = False  
                continue  
            if noti2[0] and fsm.state == "s1":
                fsm.Ri()
                noti2[0] = False  
                continue  
            for ev, sender in shared_state_queue:
                if sender != "drone2" and ev == "Sl":
                    print(f"[drone2] Reacting to Sl")
                    fsm.Ri()
                    continue  
                elif sender == "sim" and ev == "Od":
                    print(f"[drone2] Reacting to Od")
                    fsm.Od()
                    notify("drone2")
                    continue  
                else:
                    fsm.No()
                    continue
            if fsm.state == "s1" or fsm.state == "s3":  
                fsm.No()   
            shared_state_queue.clear()
        time.sleep(0.5)


def drone3(fsm):
    while True:
        print(f"[drone3] Current state: {fsm.state}")
        with state_lock:
            if noti3[0] and fsm.state == "s0":
                fsm.Ri()
                noti3[0] = False  # reset
                continue  
            if noti3[0] and fsm.state == "s1":
                fsm.Ri()
                noti3[0] = False  # reset
                continue  
            for ev, sender in shared_state_queue:
                if sender != "drone3" and ev == "Sl":
                    print(f"[drone3] Reacting to Sl")
                    fsm.Ri()
                    continue  
                elif sender == "sim" and ev == "Od":
                    print(f"[drone3] Reacting to Od")
                    notify("drone3")
                    fsm.Od()
                    continue 
            if fsm.state == "s1" or fsm.state == "s3":  
                fsm.No() 
            shared_state_queue.clear()
        time.sleep(0.5)


def drone4(fsm):
    while True:
        print(f"[drone4] Current state: {fsm.state}")
        with state_lock:
            if noti4[0] and fsm.state == "s0":
                fsm.Ri()
                noti4[0] = False  # reset
                continue  
            if noti4[0] and fsm.state == "s1":
                fsm.Ri()
                noti4[0] = False  # reset
                continue  
            for ev, sender in shared_state_queue:
                if sender != "drone41" and ev == "Sl":
                    print(f"[drone4] Reacting to Sl")
                    fsm.Ri()
                    continue  
                elif sender == "sim" and ev == "Od":
                    print(f"[drone4] Reacting to Od")
                    notify("drone4")
                    fsm.Od()
                    continue 
            if fsm.state == "s1" or fsm.state == "s3":  
                fsm.No() 
            shared_state_queue.clear()
        time.sleep(0.5)

def drone5(fsm):
    while True:
        print(f"[drone5] Current state: {fsm.state}")
        with state_lock:
            if noti5[0] and fsm.state == "s0":
                fsm.Ri()
                noti5[0] = False  # reset
                continue  
            if noti5[0] and fsm.state == "s1":
                fsm.Ri()
                noti5[0] = False  # reset
                continue  
            for ev, sender in shared_state_queue:
                if sender != "drone5" and ev == "Sl":
                    print(f"[drone5] Reacting to Sl")
                    fsm.Ri()
                    continue  
                elif sender == "sim" and ev == "Od":
                    print(f"[drone5] Reacting to Od")
                    notify("drone5")
                    fsm.Od()
                    continue 
            if fsm.state == "s1" or fsm.state == "s3":  
                fsm.No() 
            shared_state_queue.clear()
        time.sleep(0.5)





# ======= Start Threads ========
if __name__ == "__main__":
    t1 = threading.Thread(target=simMaster)
    t2 = threading.Thread(target=drone1, args=(fsm1,))
    t3 = threading.Thread(target=drone2, args=(fsm2,))
    t4 = threading.Thread(target=drone3, args=(fsm3,))
    t5 = threading.Thread(target=drone4, args=(fsm4,))
    t6 = threading.Thread(target=drone5, args=(fsm5,))

    
    t1.start()
    t2.start()
    t3.start()
    t4.start()
    t5.start()
    t6.start()