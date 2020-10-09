
"""
General Object-oriented Abstraction and JSON Textual Model of Rankine Cycle 

- SimRankineCycle: The Simulator of Rankine Cycle 

  * Input :json file  

  * output: txt file

 Example Rankine Cycles:
    Michael J . Moran. Fundamentals of Engineering Thermodynamics(7th Edition). John Wiley & Sons, Inc. 2011
    Chapter 8 : Vapour Power Systems Example

         EXAMPLE 8.1 ：An Ideal Regenerative Cycle, Page 438
         EXAMPLE 8.2: Analyzing a Rankine Cycle with Irreversibilities，Page 444
         EXAMPLE 8.5 ：A Regenerative Cycle with Open Feedwater Heater,Page 456

Run: 

python rankine.py
  
Author:Cheng Maohua  Email: cmh@seu.edu.cn

"""
import json
from rankinecycle.cycleobj import RankineCycle
from rankinecycle.cyclehelper import OutFiles


class SimRankineCycle:
    """ Input :json file      """

    def __init__(self, rankinefilename):
        # -5 remove .json
        self.prefixResultFileName =rankinefilename[0:-5].replace("txtcycle", "output")
        with open(rankinefilename, 'r') as f:
            self.idictcycle = json.loads(f.read())
        self.cycle = RankineCycle(self.idictcycle)

    def Simulator(self):
        self.cycle.simulator()

    def SpecifiedSimulator(self, SetPower=None, SetMass=None):
        # Specified Simulating： Power or Mass Flow
        self.cycle.SpecifiedSimulator(SetPower, SetMass)

        # output to files
        if SetPower != None:
            outprefix = self.prefixResultFileName + '-sp'
        else:
            outprefix = self.prefixResultFileName + '-sm'
        # output to text
        OutFiles(self.cycle)
        OutFiles(self.cycle, outprefix + '.txt')


if __name__ == "__main__":
    from platform import *
    import glob
    curpath = os.path.abspath(os.path.dirname(__file__))
    json_filesname_str = curpath+'\\'+'./data/txtcycle/rankine8[0-9].json'
    # json_filesname_str=curpath+'\\'+'./data/txtcycle/rankine85.json'
    json_filesname = glob.glob(json_filesname_str)

    Wcycledot = 100  # MW
    mdot = 150*3600  # kg/h
    for curfile in json_filesname:
        cycle = SimRankineCycle(curfile)
        # 1 1kg
        cycle.Simulator()

        # 2 Specified Net Output Power(MW)
        cycle.SpecifiedSimulator(SetPower=Wcycledot)

        # 3 Specified Mass Flow(kg/h)
        cycle.SpecifiedSimulator(SetMass=mdot)
