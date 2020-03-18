# simulating corona differential equation
# Modell:
#
# dN_INF = N_INF * REPR_RATE * (1 - N_INF/N_ALL)^(SCALE)
# dREPR_RATE = - N_INF ^ (CAUTION_FACTOR)
# dN_DEAD = DEATH_RATE * N_INF - TICK * EXPERTISE_FACTOR
# dN_ALL = - dN_DEAD

# Imports


from typing import IO

from dataclasses import dataclass

@dataclass
class SimState:
    """
    Struct to store Simulation Data
    """
    now_dat: float #Abs. Current Data
    differentials: list[float] #[0]: old differential, [1]: new differntial


class Population:
    """
    Population of a country infected by Virus
    """

    # Definition of Constants
    BASE_REPR_RATE: float = 10/50  # wieviele Infektionen durch einen Infizierten
    CAUTION_FACTOR: float = 0  # wie stark reagieren Leute
    SCALE: float = 100  # Skalierung, wie stark Vermehrung je nach Durchseuchung in Bevoelkerung
    TICK: int = 1  # Zeiteinheit. Entspricht einem Tag
    DEATH_RATE: float = 4e-2  # Def aus Studie ueber Corona
    SimTime: int = 150
    SimFileName: str = "sim.dat"
    FILE_COLUMN_DELIMITER: str = "\t,"
    FILE_ROW_DELIMITER: str = "\t;"
    EXPERTISE_FACTOR: float = 0

    def __init__(self, N_ALL: float = 85e6, N_START: float = 3100) -> None:
        # Definition of Starting Condition
        self.N_START: float = 85e6

        self.N_All: SimState = SimState(now_dat=85e6,
                                        differentials=[0, 0])
        self.N_INF: SimState = SimState(now_dat=9700,
                                        differentials=[0, 0])
        self.N_DEAD: SimState = SimState(now_dat=0,
                                         differentials=[0, 0])
        self.REPR_RATE: SimState = SimState(now_dat=Population.BASE_REPR_RATE,
                                            differentials=[0, 0])

        try:
            # write Header
            self.fd: IO = open(Population.SimFileName, "w+")
            self.fd.write("TICK{COL_DELIM}N_ALL{COL_DELIM}N_INF{COL_DELIM}N_DEAD{COL_DELIM}REPR_RATE{ROW_DELIM}\n"
            .format(COL_DELIM=Population.FILE_COLUMN_DELIMITER,
                    ROW_DELIM=Population.FILE_ROW_DELIMITER))
            self.__writeData()

            while Population.TICK < Population.SimTime:
                print("Simulating day {TICK}".format(TICK=Population.TICK))
                self.__makeSim()
            self.fd.close()
            print("Done!")

        except IOError:
            print("Couldn't write to {FileName}\n"
                .format(FileName=Population.SimFileName))
            self.fd.close()
            exit

    def __writeData(self) -> None:
        # Write Data formatted to @cls.FileName
        self.fd.write("{TICK}{COL_DELIM}{N_ALL}{COL_DELIM}{N_INF}{COL_DELIM}{N_DEAD}{COL_DELIM}{REPR_RATE}{ROW_DELIM}\n"
                      .format(TICK=Population.TICK,
                              COL_DELIM=Population.FILE_COLUMN_DELIMITER,
                              N_INF=self.N_INF,
                              N_ALL=self.N_ALL,
                              REPR_RATE=self.REPR_RATE,
                              N_DEAD=self.N_DEAD,
                              ROW_DELIM=Population.FILE_ROW_DELIMITER))

    def __makeSim(self) -> None:
        #  Simulate according to simulation modell one tick of new data
        Population.TICK += 1
        # Swap stored information
        self.N_DEAD.differentials[0] = self.N_DEAD.differentials[1]
        self.N_All.differentials[0] = self.N_All.differentials[1]
        self.N_INF.differentials[0] = self.N_INF.differentials[1]
        self.REPR_RATE.differentials[0] = self.REPR_RATE.differentials[1]

        #  Define change Rates
        self.N_INF.differentials[1] = self.N_INF.now_dat \
                                      * self.REPR_RATE.now_dat \
                                      * pow((1-self.N_INF.now_dat/self.N_All.now_dat), Population.SCALE) \
                                      - self.N_DEAD.differentials[0]

        self.N_DEAD.differentials[1] = (self.N_INF.differentials[0] + self.N_INF.differentials[1]) \
                                        * Population.DEATH_RATE 
        
        self.REPR_RATE.differentials[1] = self.N_INF.differentials[0] * Population.CAUTION_FACTOR

        # write
        self.__writeData()

# ----------------------------------------------------------------------
if __name__ == "__main__":
    Population()