"""
The PyRankine: the  hybrid steady-state simulator of Rankine Cycle

class ClosedheaterDw0

  without drain water inlet 
 
                         (No.i)  
                         │ iPort extracted steam
                    ┌────┴────┐
  feedwater outlet  │         │
  oPort_FW        ← ┼────N────┼← iPort_FW (No.j node)
      (No.k)        │         │    feedwater inlet
    tdelta          └────┬────┘  
                         ↓ oPort_dw      tdeltadw 
                          (No. m )

 json object example:
    {    
        "devtype": "FWH-CLOSE-DW0",
        "iPort": {},
        "iPort_fw": {"p":30.38,"t":249.33},
        "oPort_fw": {"p":30.38,"fdot": 1.0},
        "oPort_dw": {},
        "tdelta": -1.7,
        "tdeltadw": 5.6,
        "eta":0.99
    }

 Rows:
   1. steam mass balance row
   2. feedwater mass balance  row
   3. energy balance  row
      
 Author:Cheng Maohua  Email: cmh@seu.edu.cn 
"""
from .port import Port
from seuif97 import px2t


class ClosedHeaterDw0:
    """ sm and eo """

    energy = 'internel'
    devtype = 'FWH-CLOSE-DW0'

    def __init__(self, dictDev):
        """
        Initializes the closed feed water heater with the ports
        """
        self.name = dictDev['name']

        self.iPort = [Port(dictDev['iPort'])]
        self.iPort_fw = [Port(dictDev['iPort_fw'])]
        self.oPort_fw = [Port(dictDev['oPort_fw'])]
        self.oPort_dw = [Port(dictDev['oPort_dw'])]

        # map the name of port to the port obj
        self.portdict = {
            "iPort": self.iPort,
            "iPort_fw": self.iPort_fw,
            "oPort_fw": self.oPort_fw,
            "oPort_dw": self.oPort_dw
        }
        if ("tdelta" in dictDev):
            self.tdelta = dictDev['tdelta']
        else:
            self.tdelta = None
        if ("tdeltadw" in dictDev):
            self.tdeltadw = dictDev['tdeltadw']
        else:
            self.tdeltadw = None
        if ("eta" in dictDev):
            self.eta = dictDev['eta']
        else:
            self.eta = 1.00

        self.heatAdded = None
        self.heatExtracted = None
        self.QExtracted = None
        self.QAdded = None

    def state_fw(self):
        """ oFW """
        if self.iPort_fw[0].p is not None:
            self.oPort_fw[0].p = self.iPort_fw[0].p
        elif self.oPort_fw[0].p is not None:
            self.iPort_fw[0].p = self.oPort_fw[0].p

        self.p_sm_side = self.iPort[0].p
        self.t_sat = px2t(self.p_sm_side, 0)

        self.oPort_fw[0].t = self.t_sat - self.tdelta
        self.oPort_fw[0].pt()

    def state_dw(self):
        """ oDW self.iPort_fw[0].t """
        self.oPort_dw[0].p = self.p_sm_side
        self.oPort_dw[0].t = self.iPort_fw[0].t + self.tdeltadw
        self.oPort_dw[0].pt()

    def state(self):
        """ oFW,oDW """
        if self.tdelta is not None:
            self.state_fw()
        if self.tdeltadw is not None:
            self.state_dw()

    # sequential-modular approach
    def balance(self):
        """  balance the closed feed water heater  """
        if (self.oPort_fw[0].fdot != None):
            self.iPort_fw[0].fdot = self.oPort_fw[0].fdot
        elif (self.iPort_fw[0].fdot != None):
            self.oPort_fw[0].fdot = self.iPort_fw[0].fdot

        self.heatAdded = self.oPort_fw[0].fdot * \
            (self.oPort_fw[0].h - self.iPort_fw[0].h)
        # eta
        self.heatExtracted = self.heatAdded/self.eta
        # self.iPort[0].fdot
        self.iPort[0].fdot = self.heatExtracted / \
            (self.iPort[0].h - self.oPort_dw[0].h)
        self.oPort_dw[0].fdot = self.iPort[0].fdot

    #  equation-oriented approach
    def equation_rows(self):
        """ each row {"a":[(colid,val)] "b":val} """
        # 1 steam mass balance row:
        colidms = [(self.iPort[0].id, 1),
                   (self.oPort_dw[0].id, -1)]
        rowms = {"a": colidms, "b": 0}

        # 2 feedwater mass balance  row:
        colidmw = [(self.iPort_fw[0].id, 1),
                   (self.oPort_fw[0].id, -1)]
        rowmw = {"a": colidmw, "b": 0}

        # 3 energy balance row
        colide = [(self.iPort[0].id, self.iPort[0].h),
                  (self.iPort_fw[0].id, self.iPort_fw[0].h),
                  (self.oPort_dw[0].id, -self.oPort_dw[0].h),
                  (self.oPort_fw[0].id, -self.oPort_fw[0].h)]
        rowe = {"a": colide, "b": 0}
        self.rows = [rowms, rowmw, rowe]

    #  equation-oriented approach

    def energy_fdot(self):
        """  Simulates the closed feed water heater  """
        self.heatAdded = self.oPort_fw[0].fdot * \
            (self.oPort_fw[0].h - self.iPort_fw[0].h)
        # eta
        self.heatExtracted = self.iPort[0].fdot * \
            (self.iPort[0].h - self.oPort_dw[0].h)

    def calmdot(self, totalmass):
        pass

    def sm_energy(self):
        """ mdot """
        ucovt = 3600.0*1000.0
        self.QExtracted = self.iPort[0].mdot * \
            (self.iPort[0].h - self.oPort_dw[0].h) / ucovt
        self.QAdded = self.oPort_fw[0].mdot * \
            (self.oPort_fw[0].h - self.iPort_fw[0].h) / ucovt

    def __str__(self):
        result = '\n'+self.name
        result += '\n'+" PORT "+Port.title
        result += '\n'+"iES"+self.iPort[0].__str__()
        result += '\n'+"oDW"+self.oPort_dw[0].__str__()
        result += '\n'+"iFW"+self.iPort_fw[0].__str__()
        result += '\n'+"oFW"+self.oPort_fw[0].__str__()
        if self.tdelta is not None:
            result += '\ndelta(C) \t%.2f' % (self.tdelta)
        if self.tdeltadw is not None:
            result += '\ndeltadw(C) \t%.2f' % (self.tdeltadw)
        result += '\neta(%%) \t%.2f' % (self.eta*100)
        result += ('{} {:.2f}').format('\n\nheatAdded(kJ)):',
                                       self.heatAdded)
        result += ('{} {:.2f}').format('\nheatExtracted(kJ):',
                                       self.heatExtracted)
        try:
            result += ('{} {:.2f}').format('\n\nQdded(MW):', self.QAdded)
            result += ('{} {:.2f}').format('\nQExtracted(MW)):',
                                           self.QExtracted)
        except:
            pass
        return result
