import rclpy
from rclpy.node import Node
from rclpy.duration import Duration

import sys
import time
from std_msgs.msg import String, Bool, Float64
from geometry_msgs.msg import Twist, PoseStamped
from mavros_msgs.msg import State
from mavros_msgs.srv import CommandTOL, CommandLong, CommandBool, SetMode, CommandHome

from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy
qos_profile = QoSProfile(
    reliability=QoSReliabilityPolicy.BEST_EFFORT,  # MAVROS biasanya pakai BEST_EFFORT
    history=QoSHistoryPolicy.KEEP_ALL,
    depth=10
)

class command(Node):

    def __init__(self):
        super().__init__('bgs_mavros_2')
        self.get_logger().info('PREPARING FUNCTION')
        #===== PUBLISHER ===========
        self.kontrol_pub = self.create_publisher(Twist,"/mavros/setpoint_velocity/cmd_vel_unstamped",10)
        #===== SUBSCRIBER ==========
        self.pos_sub = self.create_subscription(PoseStamped, '/mavros/local_position/pose', self.pos_cb, qos_profile)
        self.state_sub = self.create_subscription(State ,'/mavros/state',self.state_cb, qos_profile)
        self.alt_sub = self.create_subscription(Float64, "/mavros/global_position/rel_alt", self.alt_cb, qos_profile)
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
        self.alt = Float64()
        self.posisi = PoseStamped()
    
    def state_cb(self, msg):
        self.status = msg
    def alt_cb(self, msg):
        self.alt = msg
    def pos_cb(self, msg):
        self.posisi = msg

    def loading_animation(self):
        chars = ['-', '/', '|',"\\",'-']
        index = 0
        while True:
            sys.stdout.write(f"\rIn Progress {chars[index]}")
            if index == 4:
                break
            sys.stdout.flush()
            time.sleep(0.1)
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
        arm_request = CommandBool.Request()
        arm_request.value = True  
        future = self.arming_client.call_async(arm_request)
        rclpy.spin_until_future_complete(self, future)
        if future.result() is not None:
            response: CommandBool.Response = future.result()
            if response.success:
                self.get_logger().info(f"ARMING Success: {response.success}")
                return 0
            else:
                self.get_logger().error(f"ARMING Failed: {response.success}")
                return -1
        else:
            self.get_logger().error("No response from arming service")
            return -1
        
    def takeoff(self, takeoff_alt):
        self.arm()
        takeoff_req = CommandTOL.Request()
        takeoff_req.altitude = takeoff_alt
        takeoff_req.latitude = 0.0
        takeoff_req.longitude = 0.0
        takeoff_req.min_pitch = 0.0
        takeoff_req.yaw = 0.0
        future = self.takeoff_client.call_async(takeoff_req)
        rclpy.spin_until_future_complete(self, future)
        if future.result() is not None:
            response: CommandTOL.Response = future.result()
            if response.success:
                self.get_logger().info(f"TAKEOFF Success: {response.success}")
                return 0
            else:
                self.get_logger().error(f"TAKEOFF Failed: {response.success}")
                return -1
        else:
            self.get_logger().error("No response from takeoff service")
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
        if future.result() is not None:
            response: CommandTOL.Response = future.result()
            if response.success:
                time.sleep(5)
                self.get_logger().info(f"LAND Success: {response.success}")
                return 0
            else:
                self.get_logger().error(f"LAND Failed: {response.success}")
                return -1
        else:
            self.get_logger().error("No response from land service")
            return -1

    def gps_hover(self, alt, vel):
        max = alt + 0.25
        min = alt - 0.25
        mov = self.kontrol
        status = ""
        while rclpy.ok():
            rclpy.spin_once(self, timeout_sec=0.1)
            self.kontrol_pub.publish(mov)
            if min < self.alt.data < max:
                mov.linear.x = 0.0
                mov.linear.y = 0.0
                mov.linear.z = 0.0
                status = "STOP"
                break
            if self.alt.data > max:
                mov.linear.x = 0.0
                mov.linear.y = 0.0
                mov.linear.z = -vel
                status = "TURUN"
            if 0 < self.alt.data < min:
                mov.linear.x = 0.0 
                mov.linear.y = 0.0
                mov.linear.z = vel
                status = "NAIK"
            print(f"ALT_REL: {self.alt.data:.2f} meters || STATUS: {str(status)}")

    
    def stop(self):
        mov = self.kontrol
        while rclpy.ok():
            rclpy.spin_once(self, timeout_sec=0.1)
            self.get_logger().info("STOPPED")
            mov.linear.x = 0.0
            mov.linear.y = 0.0
            mov.linear.z = 0.0
            self.kontrol_pub.publish(mov)
            break
    
    def yawcorrect(self, threshold):
        mov = self.kontrol
        status = ""
        while rclpy.ok():
            rclpy.spin_once(self, timeout_sec=0.1)
            self.kontrol_pub.publish(mov)
            if -threshold < self.posisi.pose.orientation.z < threshold:
                mov.angular.z = 0.0
                mov.linear.x = 0.0
                mov.linear.y = 0.0
                mov.linear.z = 0.0
                status = "YAWCORRECT : LURUS"
                break
            if self.posisi.pose.orientation.z < -threshold:
                mov.angular.z = -0.4
                mov.linear.x = 0.0
                mov.linear.y = 0.0
                mov.linear.z = 0.0
                status = "YAWCORRECT : YAW_RIGHT"
            if self.posisi.pose.orientation.z > threshold:
                mov.angular.z = 0.4
                mov.linear.x = 0.0
                mov.linear.y = 0.0
                mov.linear.z = 0.0
                status = "YAWCORRECT : YAW_LEFT"
            print(f"POSE Z : {self.posisi.pose.orientation.z:.2f} || STATUS : {str(status)}")

            
    def majumundur(self,korx,vel,yaw):
        min = korx - 0.1
        max = korx + 0.1
        mov = self.kontrol
        status = ""
        while rclpy.ok():
            rclpy.spin_once(self, timeout_sec=0.1)
            self.kontrol_pub.publish(mov)
            if -yaw < self.posisi.pose.orientation.z < yaw:
                if min < self.posisi.pose.position.x <max:
                    self.stop()
                    break
                if self.posisi.pose.position.x <= min:
                    status = "MAJU"
                    mov.linear.x = vel
                    mov.linear.y = 0.0
                    mov.linear.z = 0.0
                if self.posisi.pose.position.x >= max:
                    status = "MUNDUR"
                    mov.linear.x = -vel
                    mov.linear.y = 0.0
                    mov.linear.z = 0.0
            else:
                self.yawcorrect(yaw)
            print(f"KOORDINAT X : {self.posisi.pose.position.x:.2f} || POSE Z : {self.posisi.pose.orientation.z:.2f} || STATUS : {str(status)}")

    def kanankiri(self,kory,vel,yaw):
        min = kory + 0.1
        max = kory - 0.1
        mov = self.kontrol
        status = ""
        while rclpy.ok():
            rclpy.spin_once(self, timeout_sec=0.1)
            self.kontrol_pub.publish(mov)
            if -yaw < self.posisi.pose.orientation.z < yaw:
                if min > self.posisi.pose.position.y > max:
                    self.stop()
                    break
                if self.posisi.pose.position.y >= min:
                    status = "KANAN"
                    mov.linear.x = 0.0
                    mov.linear.y = -vel
                    mov.linear.z = 0.0
                if self.posisi.pose.position.y <= max:
                    status = "KIRI"
                    mov.linear.x = 0.0
                    mov.linear.y = vel
                    mov.linear.z = 0.0 
            else:
                self.yawcorrect(yaw)
            print(f"KOORDINAT Y : {self.posisi.pose.position.y:.2f} || POSE Z : {self.posisi.pose.orientation.z:.2f} || STATUS : {str(status)}")


