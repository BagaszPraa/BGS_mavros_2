import rclpy
import time
from BGS_mavros.bgs_mavros_2 import command  # Pastikan nama paket benar

def main():
    rclpy.init()
    vtol = command()
    vtol.connect()
    vtol.start()
    vtol.takeoff(5.0)
    time.sleep(10)
    vtol.land()
    vtol.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()