from launch import LaunchDescription
from launch_ros.actions import Node
from hexapod_interfaces.msg import LegReferencing
import numpy as np


def generate_launch_description():
    # Robot constants
    COXA_LEN = 71.5
    FEMUR_LEN = 100.02
    FOOT_HEIGHT = 0.0
    TIBIA_LEN = 150 + FOOT_HEIGHT
    BASE_ALTITUDE = 90.0
    BASE_WIDTH = 65.0
    GAIT_ALTITUDE = 80.0
    STEP_LENGTH = 75.0
    GAIT_WIDTH = 300.0
    
    # Setting the leg referencing system. Used to make the launch file a lot more readable!
    RF = setLegReferencing(True, 30.0, BASE_WIDTH * round(np.sin(np.pi/6.0),2), BASE_WIDTH * round(np.cos(np.pi/6.0),2), 0, 1, 2, 1, "Leg: <Right Front>")
    RM = setLegReferencing(True, 90.0, BASE_WIDTH * round(np.sin(np.pi/2.0),2), BASE_WIDTH * round(np.cos(np.pi/2.0),2), 4, 5, 6, 2, "Leg: <Right Middle>")
    RB = setLegReferencing(True, 150.0, BASE_WIDTH * round(np.sin(5.0*np.pi/6.0),2), BASE_WIDTH * round(np.cos(5.0*np.pi/6.0),2), 8, 9, 10, 3, "Leg: <Right Back>")
    LB = setLegReferencing(False, 210.0, BASE_WIDTH * round(np.sin(7.0*np.pi/6.0),2), BASE_WIDTH * round(np.cos(7*np.pi/6.0),2),0, 1, 2, 4, "Leg: <Left Back>")
    LM = setLegReferencing(False, 270.0, BASE_WIDTH * round(np.sin(3.0*np.pi/2.0),2), BASE_WIDTH * round(np.cos(3.0*np.pi/2.0),2), 4, 5, 6, 5, "Leg: <Left Middle>")
    LF = setLegReferencing(False, 330.0, BASE_WIDTH * round(np.sin(11.0*np.pi/6.0),2), BASE_WIDTH * round(np.cos(11.0*np.pi/6.0),2), 8, 9, 10, 6, "Leg: <Left Front>")
    
    ld = LaunchDescription()

    servo_node = Node(
        package = "leg_controller",
        executable = "servo_node",
        parameters=[
            {"LB": [LB.hip_port, LB.shoulder_port, LB.knee_port]},
            {"LM": [LM.hip_port, LM.shoulder_port, LM.knee_port]},
            {"LF": [LF.hip_port, LF.shoulder_port, LF.knee_port]},
            {"RF": [RF.hip_port, RF.shoulder_port, RF.knee_port]},
            {"RM": [RM.hip_port, RM.shoulder_port, RM.knee_port]},
            {"RB": [RB.hip_port, RB.shoulder_port, RB.knee_port]}
        ],
        output = 'screen'
    )

    kin_node = Node(
        package = "leg_controller",
        executable = "kin_node",
        parameters = [
            {"coxa_len": COXA_LEN},
            {"femur_len": FEMUR_LEN},
            {"tibia_len": TIBIA_LEN},
            {"base_altitude": BASE_ALTITUDE},
            {"base_width": BASE_WIDTH},
            {"origin_RF": [RF.origin_x, RF.origin_y]},
            {"origin_RM": [RM.origin_x, RM.origin_y]},
            {"origin_RB": [RB.origin_x, RB.origin_y]},
            {"origin_LB": [LB.origin_x, LB.origin_y]},
            {"origin_LM": [LM.origin_x, LM.origin_y]},
            {"origin_LF": [LF.origin_x, LF.origin_y]}
        ],
        output = 'screen'
    )

    gait_waypoint_node = Node(
        package = "gait_controller",
        executable = "waypointer_node",
        parameters = [
            {"origin_RF": [RF.origin_x, RF.origin_y]},
            {"origin_RM": [RM.origin_x, RM.origin_y]},
            {"origin_RB": [RB.origin_x, RB.origin_y]},
            {"origin_LB": [LB.origin_x, LB.origin_y]},
            {"origin_LM": [LM.origin_x, LM.origin_y]},
            {"origin_LF": [LF.origin_x, LF.origin_y]},
            {"leg_angular_orientation": [RF.base_angle, RM.base_angle, RB.base_angle, LB.base_angle, LM.base_angle, LF.base_angle]},
            {"base_width": BASE_WIDTH},
            {"gait_width": GAIT_WIDTH},
            {"gait_altitude": GAIT_ALTITUDE},
            {"step_length": STEP_LENGTH}
        ]
    )

    bezier_node = Node(
        package="gait_controller",
        executable="bezier_traj_node",
        
    )

    ctrl_node = Node(
        package = "leg_controller",
        executable = "ctrl_node",
        parameters = [
            {"coxa_len": COXA_LEN},
            {"femur_len": FEMUR_LEN},
            {"tibia_len": TIBIA_LEN},
            {"gait_altitude": BASE_ALTITUDE},
            {"base_width": BASE_WIDTH},
            {"gait_width": GAIT_WIDTH}
        ],
        output = 'screen'
    )

    ld.add_action(servo_node)
    ld.add_action(kin_node)
    ld.add_action(bezier_node)
    ld.add_action(gait_waypoint_node)
    
    #ld.add_action(ctrl_node)
    
    return ld

def setLegReferencing(side, base_angle, origin_x, origin_y, 
                      hip_port, shoulder_port, knee_port, 
                      index, description):
    temp = LegReferencing()
    
    temp.side = side
    temp.base_angle = base_angle
    temp.origin_x = origin_x
    temp.origin_y = origin_y
    temp.hip_port = hip_port
    temp.shoulder_port = shoulder_port
    temp.knee_port = knee_port
    temp.index = index
    temp.description = description

    return temp
