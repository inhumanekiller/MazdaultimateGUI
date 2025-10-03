{\rtf1\ansi\ansicpg1252\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 # mazda_tool/simulators/dyno_simulator.py\
import numpy as np\
import matplotlib.pyplot as plt\
\
class DynoSimulator:\
    """Simulate wheel HP, torque, and load for Mazdaspeed 3"""\
\
    def __init__(self, rpm_range=(1000, 7200)):\
        self.rpm = np.arange(rpm_range[0], rpm_range[1]+1, 100)\
        self.hp = np.zeros_like(self.rpm, dtype=float)\
        self.torque = np.zeros_like(self.rpm, dtype=float)\
\
    def simulate(self, boost_psi=18.5, ignition_offset=0):\
        """Simple dyno simulation based on boost and ignition timing"""\
        # Base torque curve (factory-ish)\
        self.torque = 200 * (1 + (boost_psi-14.7)/14.7) * np.exp(-((self.rpm-4500)/2500)**2)\
        self.torque += ignition_offset  # Apply timing offset\
        self.hp = (self.torque * self.rpm) / 5252\
        return self.rpm, self.hp, self.torque\
\
    def plot(self):\
        plt.figure(figsize=(10,5))\
        plt.plot(self.rpm, self.hp, label='HP', color='red')\
        plt.plot(self.rpm, self.torque, label='Torque', color='blue')\
        plt.title("Dyno Simulator - Mazdaspeed 3")\
        plt.xlabel("RPM")\
        plt.ylabel("HP / Torque (lb-ft)")\
        plt.legend()\
        plt.grid(True)\
        plt.show()\
}