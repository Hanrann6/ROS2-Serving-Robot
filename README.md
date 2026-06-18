# ROS2 기반 카페 서빙 로봇 시스템 (ROS2 Serving Robot)

> **ROS2 Humble**과 **Nav2**를 활용하여 카페 환경(Gazebo) 내에서 지정된 테이블로 안전하고 정확하게 음식을 배달하는 자율주행 서빙 로봇 프로젝트입니다.

---

## 프로젝트 개요

본 프로젝트는 터틀봇3 버거(TurtleBot3 Burger) 모델을 커스텀하여, 가상 카페 환경 내에서 사용자의 테이블 요청 명령어(`std_msgs/msg/String`)에 따라 실시간으로 최적의 경로를 생성하고 목적지까지 주행하는 스마트 서빙 시스템입니다.

### 핵심 구현 기능
* **정밀 초기 위치 동기화:** Gazebo 시뮬레이션 시작 시 로봇의 스폰 좌표(`x: -2.86, y: 4.09, yaw: -1.7`)를 Nav2 AMCL의 `initial_pose`로 강제 주입하여, 별도의 수동 위치 지정(`2D Pose Estimate`) 없이 **오차 0.00%의 실시간 위치 동기화**를 실현했습니다.
* **코스트맵 격자 해상도 최적화:** 글로벌/로컬 코스트맵의 해상도(`resolution: 0.05`)와 팽창 반지름(`inflation_radius: 0.25`)을 물리 맵 환경에 맞춰 슬림하게 매칭함으로써, 좁은 카페 통로에서도 로봇이 갇히거나 맵 밖으로 탈조(순간이동)하는 현상을 완벽히 해결했습니다.
* **방향성 자율주행 (Orientation Matching):** `2D Nav Goal` 데이터의 쿼터니언 회전 값($z, w$)을 서빙 노드 파이썬 코드에 정밀 반영하여, 로봇이 테이블 앞에 도착했을 때 벽을 들이받지 않고 손님을 올바르게 바라보도록 구현했습니다.

---

## AI 활용 기술 및 범위

본 프로젝트 개발 과정에서 AI 기술(LLM)을 다음과 같이 활용하였습니다.

* **활용 툴:** ChatGPT / Gemini
* **활용 범위 및 비중:** **소규모 활용 (Little bit, 약 15~20%)**
* **상세 활용 내용:** - ROS2 Nav2의 뇌라 할 수 있는 글로벌/로컬 코스트맵 패닉 현상(`RTPS_TRANSPORT_SHM Error` 등) 발생 시 공유 메모리 찌꺼기 삭제 공식을 도출하는 디버깅 조언자로 활용했습니다.
  - 가제보 월드 좌표계와 맵 좌표계 불일치로 인한 오차 계산 아이디어를 검증하는 브레인스토밍 파트너로 활용했습니다. 현업 개발의 코드 무결성을 위해 메인 알고리즘 및 맵 좌표 튜닝은 직접 수동 매칭을 통해 정밀 제어했습니다.

---

## 참고 자료

프로젝트 구현 및 Nav2 튜닝 과정에서 아래의 공식 문서와 기술 블로그를 참고하여 문제를 해결했습니다.

### Official Documentation
* [ROS 2 Humble 공식 문서](https://docs.ros.org/en/humble/index.html)
* [Nav2 (Navigation2) 공식 도큐멘트](https://navigation.ros.org/](https://docs.nav2.org/)
* [ROBOTIS TurtleBot3 매뉴얼](https://emanual.robotis.com/docs/en/platform/turtlebot3/overview/)

### Open Source & Communities
* [ROS 2 Navigation2 GitHub Repository](https://github.com/ros-navigation/navigation2)
* [TurtleBot3 공식 GitHub 저장소](https://github.com/ROBOTIS-GIT/turtlebot3)
* [오로카(OROKA) 로봇공학 커뮤니티 네이버 카페](https://cafe.naver.com/openrt)
