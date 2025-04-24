import rclpy
import time
from bgs_mavros2.bgs_mavros_2 import command  # Pastikan nama paket benar

wp_1    = (-35.3597680,149.1647155)

def main():
    rclpy.init()
    vtol = command()
    vtol.connect()
    vtol.ambilkordinat()
    vtol.set_mode("GUIDED")
    vtol.start()
    vtol.takeoff(1.0)
    time.sleep(4)
    vtol.gps_hover(2.0,0.5)
    # vtol.set_waypoint(wp_1,20.0)
    # vtol.cek_kordinat(1.0,wp_1)
    vtol.majumundur(4.0,0.5,0.05)
    # vtol.kanankiri(-4.0,0.5,0.05)
    # vtol.majumundur(-4.0,0.5,0.05)
    # vtol.kanankiri(0.0,0.5,0.05)
    vtol.majumundur(0.0,0.5,0.05)
    vtol.land()
    vtol.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()