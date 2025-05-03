import json
import threading
import time




class Food_bowl:
  def __init__(self, name, state, weight, cat, ready):
    self.name = name
    self.state = state
    self.weight = weight
    self.cat = cat
    self.ready = ready

  def __str__(self):
    return f"{self.name}"
  

fA = Food_bowl("A", "closed", 0, False, True)

fB = Food_bowl("B", "closed", 0, False, True)


class Cat:
  def __init__(self, name, ratio_per_day):
    self.name = name
    self.ratio_per_day = ratio_per_day

bruno = Cat("Bruno", 200)
flaekli = Cat("Flaekli", 200)


def load_cats():
    with open("cats.json", "r") as f:
        return json.load(f)

    

cats = load_cats()

def movement_detected():
    pass

def camera_A_cat_YOLO():
    pass

def camera_B_cat_YOLO():
    pass

def camera_A_detected_cat():
    pass

def camera_B_detected_cat():
    pass

def open_bowl():
    pass

def close_bowl():
    pass

def close_bowl_A():
    pass

def close_bowl_B():
    pass

def weigh_bowl_A():
    pass

def weigh_bowl_B():
    pass

def fill_bowl_A():
    pass

def fill_bowl_B():
    pass

all_cats = ["bruno", "flaekli"]

def fill_bowl():
    while True:
        if fA.state=="closed" and fA.weight < 200:
            fA.ready = False
            fill_bowl_A()
        if fB.state=="closed" and fB.weight < 200:
            fB.ready = False
            fill_bowl_B()
        fA.ready = True
        fB.ready = True
        time.sleep(0.5)


def give_food_A():
    while True:
        if movement_detected():
            if camera_A_cat_YOLO() and not fA.state=="open":
                if camera_A_detected_cat() in all_cats:
                    cat_A = camera_A_detected_cat()
                    cat_A = "bruno"
                    if cats.get(cat_A, {}).get("ration_left") > 0 and fA.ready:
                        open_bowl()
                        fA.state="open"
                        fB.state="open"
                        while fA.state=="open":
                            if fA.weight-weigh_bowl_A()>cats.get(cat_A, {}).get("ration_left") or camera_A_detected_cat() not in all_cats:
                                close_bowl_A()
                                fA.state="closed"
                                fA.weight=fA.weight-weigh_bowl_A()
                                cats[cat_A]["ration_left"] = cats[cat_A]["ration_left"]-(fA.weight-weigh_bowl_A())
                        if fA.cat==False:
                            close_bowl()
                            fB.state="closed"

        time.sleep(0.5)

def give_food_B():
    while True:
        if movement_detected():
            if camera_B_cat_YOLO() and not fB.state=="open":
                if camera_B_detected_cat() in all_cats:
                    cat_B = camera_B_detected_cat()
                    cat_B = "flaekli"
                    if cats.get(cat_B, {}).get("ration_left") > 0 and fB.ready:
                        open_bowl()
                        fB.state="open"
                        fA.state="open"
                        while fB.state=="open":
                            if fB.weight-weigh_bowl_B()>cats.get(cat_B, {}).get("ration_left") or camera_B_detected_cat() not in all_cats:
                                close_bowl_B()
                                fB.state="closed"
                                fB.weight=fB.weight-weigh_bowl_A()
                                cats[cat_B]["ration_left"] = cats[cat_B]["ration_left"]-(fB.weight-weigh_bowl_B())
                        if fB.cat==False:
                            close_bowl()
                            fA.state="closed"

        time.sleep(0.5)

t1 = threading.Thread(target=give_food_A, name='t1')
t2 = threading.Thread(target=give_food_B, name='t2')
t3 = threading.Thread(target=fill_bowl, name='t2')

 

t1.start()
t2.start()
t3.start()

t1.join()
t2.join()
t3.join()




   