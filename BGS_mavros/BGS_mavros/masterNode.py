import rclpy
import time
from BGS_mavros.bgs_mavros_2 import command  # Pastikan nama paket benar

def main():
    rclpy.init()
    vtol = command()
    vtol.connect()
    vtol.start()
    vtol.takeoff(1.0)
    time.sleep(4)
    vtol.gps_hover(10.0,0.5)
    vtol.majumundur(4.0,0.5,0.05)
    vtol.kanankiri(-4.0,0.5,0.05)
    vtol.majumundur(-4.0,0.5,0.05)
    vtol.kanankiri(0.0,0.5,0.05)
    vtol.majumundur(0.0,0.5,0.05)
    vtol.land()
    vtol.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()