import rclpy
from rclpy.node import Node
import numpy as np
from time import *
from leg_controller.legInfo import LB, LM, LF, RB, RM, RF, Point, legReferencing
from hexapod_interfaces.msg import TargetAngles, TargetPositions

class inverseKinematics(Node):    
    ## Node Constructor
    def __init__(self):
        super().__init__("inverse_kinematics_node")
        self.targetAngles = TargetAngles()
        self.angles = self.create_publisher(TargetAngles, 'HexAngles', 10)
        self.posSub = self.create_subscription(TargetPositions, 'HexLegPos', self.posCallback, 10)

    ## This function takes the position subscription and publishes the computed angles
    def posCallback(self, hexPos = TargetPositions):
        self.getLegAngles(Point(hexPos.x_pos[1], hexPos.y_pos[1], hexPos.z_pos[1]), RF)
        self.getLegAngles(Point(hexPos.x_pos[2], hexPos.y_pos[2], hexPos.z_pos[2]), RM)
        self.getLegAngles(Point(hexPos.x_pos[3], hexPos.y_pos[3], hexPos.z_pos[3]), RB)
        self.getLegAngles(Point(hexPos.x_pos[4], hexPos.y_pos[4], hexPos.z_pos[4]), LB)
        self.getLegAngles(Point(hexPos.x_pos[5], hexPos.y_pos[5], hexPos.z_pos[5]), LM)
        self.getLegAngles(Point(hexPos.x_pos[6], hexPos.y_pos[6], hexPos.z_pos[6]), LF)

        self.angles.publish(self.targetAngles)

    ## Function solving the inverse kinematic model for a given specific leg and point 
    def getLegAngles(self, point = Point, leg = legReferencing, publish = False):
        # Constants
        COXA_LEN = 71.5
        FEMUR_LEN = 100.02
        FOOT_HEIGHT = 0
        TIBIA_LEN = 150 + FOOT_HEIGHT
        GAIT_ALTITUDE = 90
        BASE_WIDTH = 65.0 # mm

        self.get_logger().info("Leg origin: " + str(leg.originX) + " | " + str(leg.originY))
        # Distance from the leg origin to the point in a planar view
        D = np.sqrt((point.x - leg.originX) * (point.x - leg.originX) + (point.y - leg.originY) * (point.y - leg.originY))
        # Distance without the coxa
        L = D - COXA_LEN
        # Triangle height from the input point and the desired gait altitude
        A = point.z - GAIT_ALTITUDE
    
        # Distance the origin to the tip of the leg
        Lprime = np.sqrt(A * A + L * L)
        self.get_logger().info("Kin Distances: " + str(D) + " | " + str(L) + " | " + str(Lprime))

        # (x, y) plane. z is projected on this plane
        T = np.sqrt(point.x * point.x + point.y * point.y)
        alphaPrime = np.arccos(self.limiter((D * D + BASE_WIDTH * BASE_WIDTH - T * T) / (2 * D * BASE_WIDTH), -1.0, 1.0))
        alpha = self.limiter(np.rad2deg(alphaPrime) - 90.0)

        # (z, D) plane. x and y are projected on the D-plane
        delta = np.arcsin(L / Lprime)
        beta = np.arccos(self.limiter((TIBIA_LEN * TIBIA_LEN - FEMUR_LEN * FEMUR_LEN - Lprime * Lprime) / (-2.0 * FEMUR_LEN * Lprime), -1.0, 1.0))
        sigma = np.arccos(self.limiter((Lprime * Lprime - FEMUR_LEN * FEMUR_LEN - TIBIA_LEN * TIBIA_LEN) / (-2.0 * FEMUR_LEN * TIBIA_LEN), -1.0, 1.0))

        # There are two cases as the triangle switches side when the leg goes over the robot's base level
        tetha1 = self.limiter(180.0 - np.rad2deg(beta + delta) if point.z < GAIT_ALTITUDE else np.rad2deg(delta - beta))
        tetha2 = self.limiter(90.0 + (180.0 - (np.rad2deg(sigma) + 45.0))) # Note that the 45 represents the assembly offset between the tibia and femur!

        self.get_logger().info("Angles: " + str(alpha) + " | " + str(tetha1) + " | " + str(tetha2) + "\n")

        # Setting the target angles for the leg the inverse kinematics were computed for
        self.targetAngles.shoulder_angle[leg.index] = alpha
        self.targetAngles.hip_angle[leg.index] = tetha1
        self.targetAngles.knee_angle[leg.index] = tetha2

        # If we want to publish from here, publish must be set to true
        if (publish == True):
            self.angles.publish(self.targetAngles)

    ## Simple function to set the limits of the angles for the servos in order to not get out of bounds or to limit the servo movement. Also used to keep trig values within ranges
    def limiter(self, value, minLimit = 0.0, maxLimit = 180.0):
        if value > maxLimit:
            value = maxLimit
        if value < minLimit:
            value = minLimit

        return value

def main(args = None):
    rclpy.init(args = args)
    invKinNode = inverseKinematics()
    
    # test height movement
    #for heigth in range(0,250):
    #    invKinNode.getLegAngles(Point(200, 200, heigth), RF)
    #    sleep(0.01)

    #for length in range(150,250):
    #    invKinNode.getLegAngles(Point(length, 200, 0), RF)
    #    sleep(0.01)

    #for width in range(150,250):
    #    invKinNode.getLegAngles(Point(200, width, 0), RF)
    #    sleep(0.01)

    rclpy.spin(invKinNode)

    rclpy.shutdown()

if __name__ == '__main__':
    main()
