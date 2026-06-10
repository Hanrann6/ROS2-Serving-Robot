import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from std_msgs.msg import String
from nav2_msgs.action import NavigateToPose
import time

class CafeServingRobot(Node):
    def __init__(self):
        super().__init__('cafe_serving_robot')
        
        self.table_coordinates = {
            'home':    {'x': 0.0,  'y': 0.0,  'z': 0.0, 'w': 1.0},
            'table_1': {'x': 0.5,  'y': 1.5,  'z': 0.0, 'w': 1.0},
            'table_2': {'x': 2.5,  'y': 0.5, 'z': 0.0, 'w': 1.0},
            'table_3': {'x': 3.5, 'y': 2.6,  'z': 0.0, 'w': 1.0},
            'table_4': {'x': 1.7, 'y': 3.8, 'z': 0.0, 'w': 1.0}
        }
        
        self.is_busy = False # 로봇이 이동 중일 때 중복 주문을 막는 플래그
        
        # 1. Subscriber: /table_request 토픽으로 들어오는 주문 수신
        self.request_sub = self.create_subscription(String, '/table_request', self.request_callback, 10)
        
        # 2. Publisher: 목적지 도착 시 상태를 외부에 알림
        self.status_pub = self.create_publisher(String, '/delivery_status', 10)
        
        # 3. Action Client: Nav2에 자율주행 명령을 내리기 위한 클라이언트
        self.nav_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        
        self.get_logger().info('[카페 서빙 로봇 노드] 주문 대기 중...')

    def request_callback(self, msg):
        table_id = msg.data
        
        if self.is_busy:
            self.get_logger().warn(f'로봇이 현재 배송 중입니다! 요청 무시: {table_id}')
            return
            
        if table_id in self.table_coordinates:
            self.get_logger().info(f'주문 접수! {table_id}번 테이블로 출발합니다.')
            self.is_busy = True
            self.send_goal(table_id)
        else:
            self.get_logger().error(f'존재하지 않는 테이블 ID입니다: {table_id}')

    def send_goal(self, target_id):
        # Nav2 액션 서버가 켜질 때까지 대기
        self.get_logger().info('Nav2 주행 서버 연결 대기 중...')
        self.nav_client.wait_for_server()
        
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
        
        # 딕셔너리에서 목적지 좌표 매핑
        coord = self.table_coordinates[target_id]
        goal_msg.pose.pose.position.x = coord['x']
        goal_msg.pose.pose.position.y = coord['y']
        goal_msg.pose.pose.orientation.z = coord['z']
        goal_msg.pose.pose.orientation.w = coord['w']
        
        self.get_logger().info(f'Nav2에 목표 좌표 전송 완료 ({target_id})')
        future = self.nav_client.send_goal_async(goal_msg)
        future.add_done_callback(lambda f: self.goal_response_callback(f, target_id))

    def goal_response_callback(self, future, target_id):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error('Nav2가 목표 경로 생성을 거부했습니다.')
            self.is_busy = False
            return
            
        self.get_logger().info('글로벌 경로 탐색 성공. 로봇 주행 시작.')
        res_future = goal_handle.get_result_async()
        res_future.add_done_callback(lambda f: self.result_callback(f, target_id))

    def result_callback(self, future, target_id):
        status_msg = String()
        
        if target_id != 'home':
            self.get_logger().info(f'{target_id}번 테이블 도착 완료! 손님께 음료를 전달합니다.')
            
            # /delivery_status 토픽 발행
            status_msg.data = f'arrived_{target_id}'
            self.status_pub.publish(status_msg)
            
            # 5초 동안 손님이 음료를 내리는 시간 대기 (음료 전달 시뮬레이션)
            self.get_logger().info('5초 후 복귀 주행을 시작합니다...')
            time.sleep(5.0)
            
            # 카운터(home) 위치로 자동 복귀 명령
            self.send_goal('home')
        else:
            self.get_logger().info('카운터(Home)에 안전하게 복귀했습니다. 다음 주문을 기다립니다.')
            status_msg.data = 'returned_home'
            self.status_pub.publish(status_msg)
            self.is_busy = False # 플래그 해제하여 새 주문을 받을 수 있는 상태로 전환

def main(args=None):
    rclpy.init(args=args)
    node = CafeServingRobot()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
