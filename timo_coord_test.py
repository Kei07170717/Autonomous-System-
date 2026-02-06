import time
from pymycobot import MyCobot280, PI_PORT, PI_BAUD

mc = MyCobot280(PI_PORT, PI_BAUD)

# --- Bring robot into a known runnable state ---
mc.power_on()
time.sleep(0.8)
mc.resume()
time.sleep(0.2)

print("power:", mc.is_power_on())
print("paused:", mc.is_paused())
print("moving:", mc.is_moving())

cur = mc.get_coords()
ang = mc.get_angles()
print("coords:", cur)
print("angles:", ang)

if not cur:
    print("get_coords() returned nothing -> comms issue or controller not ready.")
    raise SystemExit

# --- Small reachable move: keep orientation the same, nudge X by +20mm ---
target = [cur[0] + 20, cur[1], cur[2], cur[3], cur[4], cur[5]]
print("\nSending coords target:", target)

ret = mc.send_coords(target, 30, 0)   # try mode 0 first
print("send_coords returned:", ret)

# Watch for change
t0 = time.time()
last = None
while time.time() - t0 < 10:
    moving = mc.is_moving()
    now = mc.get_coords()
    if now != last:
        print(f"{time.time()-t0:4.1f}s  moving:{moving}  coords:{now}")
        last = now
    time.sleep(0.2)
