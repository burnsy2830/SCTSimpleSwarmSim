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


# ======= Shared State Setup ========
state_lock = threading.Lock()
chan_lock = threading.Lock()
shared_state_queue = []
drone_queue = []          
noti = [False]           

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
            if noti[0] and fsm.state == "s0":
                fsm.Ri()
                noti[0] = False  # reset
                continue  
            if noti[0] and fsm.state == "s1":
                fsm.Ri()
                noti[0] = False  # reset
                continue  
            for ev, sender in shared_state_queue:
                if sender != "drone1" and ev == "Sl":
                    print(f"[drone1] Reacting to Sl")
                    fsm.Ri()
                    continue  
                elif sender == "sim" and ev == "Od":
                    print(f"[drone1] Reacting to Od")
                    noti[0] = True
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
        
            if noti[0] and fsm.state == "s0":
                fsm.Ri()
                noti[0] = False  
                continue  
            if noti[0] and fsm.state == "s1":
                fsm.Ri()
                noti[0] = False  
                continue  
            for ev, sender in shared_state_queue:
                if sender != "drone2" and ev == "Sl":
                    print(f"[drone2] Reacting to Sl")
                    fsm.Ri()
                    continue  
                elif sender == "sim" and ev == "Od":
                    print(f"[drone2] Reacting to Od")
                    fsm.Od()
                    noti[0] = True
                    continue  
                else:
                    fsm.No()
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
    t1.start()
    t2.start()
    t3.start()
