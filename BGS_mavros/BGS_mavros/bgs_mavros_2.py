import rclpy
from rclpy.node import Node

import sys
import time
from std_msgs.msg import String
from geometry_msgs.msg import Twist
from mavros_msgs.msg import State
from mavros_msgs.srv import CommandTOL, CommandLong, CommandBool, SetMode, CommandHome

# from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy
# qos_profile = QoSProfile(
#     reliability=QoSReliabilityPolicy.BEST_EFFORT,  # MAVROS biasanya pakai BEST_EFFORT
#     history=QoSHistoryPolicy.KEEP_ALL,
#     depth=10
# )

class command(Node):

    def __init__(self):
        super().__init__('bgs_mavros_2')
        self.get_logger().info('PREPARING FUNCTION')
        #===== PUBLISHER ===========
        self.kontrol_pub = self.create_publisher(Twist,"/mavros/setpoint_velocity/cmd_vel_unstamped",10)
        #===== SUBSCRIBER ==========
        self.state_sub = self.create_subscription(State ,'/mavros/state',self.state_cb, 10)
        #===== SERVICES ============
        self.arming_client = self.create_client(CommandBool, "/mavros/cmd/arming")
        while not self.arming_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().warn("Waiting for /mavros/cmd/arming service...")

        self.takeoff_client = self.create_client(CommandTOL, "mavros/cmd/takeoff")
        while not self.takeoff_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().warn("Waiting for /mavros/cmd/takeoff service...")

        self.land_client = self.create_client(CommandTOL, "mavros/cmd/land")
        while not self.land_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().warn("Waiting for /mavros/cmd/land service...")
        
        #===== OBJECT IMPORT =======
        self.kontrol = Twist()
        self.status = State()
    
    def state_cb(self, msg):
        self.status = msg

    def loading_animation(self):
        chars = ['-', '/', '|',"\\",'-']
        index = 0
        while True:
            sys.stdout.write(f"\rIn Progress {chars[index]}")
            if index == 4:
                break
            sys.stdout.flush()
            time.sleep(0.2)
            index = (index + 1) % len(chars)

    def connect(self):
        self.get_logger().info('Tunggu Koneksi FCU Boss')
        while rclpy.ok() and not self.status.connected:
            rclpy.spin_once(self, timeout_sec=0.1)
            self.loading_animation()
        else:     
            if self.status.connected:
                self.get_logger().info('FCU Connected')
                return 0
            else:
                self.get_logger().warn('Error Connection')
                return -1
     
    def start(self):
        self.get_logger().info("Switch ke GUIDED untuk Start")
        while rclpy.ok() and self.status.mode != "GUIDED":
            rclpy.spin_once(self, timeout_sec=0.1)
            self.loading_animation()
        else:
            if self.status.mode == "GUIDED":
                self.get_logger().info("GUIDED , Start Misi")
                return 0
            else:
                self.get_logger().error("Misi Start Error")
                return -1
        
    def arm(self):
        self.get_logger().info("ARMING Drone")
        arm_request = CommandBool.Request()
        arm_request.value = True  
        future = self.arming_client.call_async(arm_request)
        rclpy.spin_until_future_complete(self, future)
        if future.result() and future.result().success:
            self.get_logger().info("ARMING Success")
            return 0
        else:
            self.get_logger().error("ARMING Failed")
            return -1
  
    def takeoff(self, takeoff_alt):
        self.get_logger().info("Initiating TAKEOFF")
        self.arm()
        takeoff_req = CommandTOL.Request()
        takeoff_req.altitude = takeoff_alt
        takeoff_req.latitude = 0.0
        takeoff_req.longitude = 0.0
        takeoff_req.min_pitch = 0.0
        takeoff_req.yaw = 0.0
        future = self.takeoff_client.call_async(takeoff_req)
        rclpy.spin_until_future_complete(self, future)
        if future.result() and future.result().success:
            self.get_logger().info("TAKEOFF Success")
            return 0
        else:
            self.get_logger().error("TAKEOFF Failed")
            return -1

    def land(self):
        self.get_logger().info("Initiating LANDING")
        land_request = CommandTOL.Request()
        land_request.altitude = 0.0
        land_request.latitude = 0.0
        land_request.longitude = 0.0
        land_request.min_pitch = 0.0
        land_request.yaw = 0.0
        future = self.land_client.call_async(land_request)
        rclpy.spin_until_future_complete(self, future)
        if future.result() and future.result().success:
            self.get_logger().info("LANDING Success")
            return 0
        else:
            self.get_logger().error("LANDING Failed")
            return -1
            
    def maju(self, speed):
        rate = self.create_rate(10)
        mov = self.kontrol
        while rclpy.ok():
            rclpy.spin_once(self)  # Agar callback subscriber tetap berjalan
            self.get_logger().info('maju')
            mov.linear.x = speed
            mov.linear.y = 0
            mov.linear.z = 0
            self.kontrol_pub.publish(mov)
            rate.sleep()  # Tidur sesuai rate

# def main():
#     print("bgs_mavros_2 script running")

# if __name__ == '__main__':
#     main()
