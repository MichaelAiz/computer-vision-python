# external dependencies
from filelock import FileLock

# built-in modules
import json
import logging
import sys
import os
import time

class CommandModule:
    """
    Provides communication between CV system and telemetry manager to send data and instructions

    ...

    Attributes
    ----------
    pogiData : dict
        dictionary of ground-in plane-out (POGI) data to be read from the POGI json file
    pigoData : dict
        dictionary of plane-in ground-out (PIGO) data to be written to the PIGO json file
    pogiFileDirectory : str
        string containing directory to POGI file
    pigoFileDirectory : str
        string containing directory to PIGO file
    pogiLock : filelock.FileLock
        FileLock used to lock the POGI file when being read
    pigoLock : filelock.FileLock
        FileLock used to lock the PIGO file when being written
    logger : logging.Logger
        Logger for outputing log messages

    note: pogiData and pigoData are currently specified in https://docs.google.com/document/d/1j7zZJAirZ91-UeNFV-kRFMhTaT8Swr9J8PcyvD0fPpo/edit


    Methods
    -------
    __init__(pogiFileDirectory="", pigoFileDirectory="")
    __read_from_pogi_file()
    __write_to_pigo_file()
    __is_null(value)

    get_error_code() -> int
    get_current_altitude() -> float
    get_current_latitude() -> float
    get_current_longitude() -> float
    get_sensor_status() -> float

    set_gps_coordinates(gpsCoordinates: dict)
    set_ground_commands(groundCommands: dict)
    set_gimbal_commands(gimbalCommands: dict)
    set_begin_landing(beginLanding: bool)
    set_begin_takeoff(beginTakeoff: bool)
    set_disconnect_autopilot(disconnectAutoPilot: bool)

    @property pogiDirectory()
    @pogiDirectory.setter pogiDirectory(pogiFileDirectory: str)
    @property pigoDirectory()
    @pigoDirectory.setter pigoDirectory(pigoFileDirectory: str)
    """

    def __init__(self, pogiFileDirectory: str, pigoFileDirectory: str):
        """
        Initializes POGI & PIGO empty dictionaries, POGI & PIGO file directories, PIGO file lock, and logger

        Parameters
        ----------
        pogiFileDirectory: str
            String of POGI file directory by default set to empty string
        pigoFileDirectory: str
            String of POGI file directory by default set to empty string
        """
        self.__logger = logging.getLogger()
        self.__pogiData = dict()
        self.__pigoData = dict()
        self.__pogiFileDirectory = pogiFileDirectory
        self.__pigoFileDirectory = pigoFileDirectory
        self.__pogiLock = FileLock(pogiFileDirectory + ".lock")
        self.__pigoLock = FileLock(pigoFileDirectory + ".lock")

    def __read_from_pogi_file(self):
        """
        Decodes JSON data from pogiFileDirectory JSON file and stores it in pogiData dictionary
        """
        try:
            with self.__pogiLock, open(self.pogiFileDirectory, "r") as pogiFile:
                self.__pogiData = json.load(pogiFile)
        except json.decoder.JSONDecodeError:
            self.__logger.error("The given GPIO json file at: " + self.pogiFileDirectory + " has no data to read. Exiting...")
            sys.exit(1)

    def __write_to_pigo_file(self):
        """
        Encodes pigoData dictionary as JSON and stores it in pigoFileDirectory JSON file
        """
        if not bool(self.__pigoData):
            raise ValueError("The current PIGO data dictionary is empty")

        with self.__pigoLock, open(self.pigoFileDirectory, "w") as pigoFile:
            json.dump(self.__pigoData, pigoFile, ensure_ascii=False, indent=4, sort_keys=True)

    def __is_null(self, value) -> bool:
        """
        Logs an error if value is None and returns boolean indicating if it is None

        Parameters
        ----------
        value:
            Value to evaluate

        Returns
        -------
        bool:
            True if None, else False
        """
        if value is None:
            self.__logger.error("Value that was passed is null.")
            return True
        else:
            return False

    def get_error_code(self) -> int:
        """
        Returns the error code from the POGI file

        Returns
        -------
        int:
            Error code
        """
        self.__pogi_file_reader()
        errorCode = self.pogiData.get("errorCode")
        if type(errorCode) == int:
            return errorCode
        else:
            if errorCode == None:
                self.__logger.error("Error code not found in the GIPO json file. Exiting...")
            elif type(errorCode) != int:
                self.__logger.error("Error code found in the GIPO json file is not an int. Exiting...")
            sys.exit(1)

    def get_current_altitude(self) -> int:
        """
        Returns the altitude from the POGI file

        Returns
        -------
        int:
            Current altitude of the plane
        """
        self.__read_from_pogi_file()
        altitude = self.pogiData["altitude"]

        if type(altitude) == int:
            return altitude
        else:
            if self.__is_null(altitude):
                raise ValueError("Altitude not found in the POGI json file. Exiting...")
            elif type(altitude != int):
                raise TypeError("Altitude in the POGI file was not an int. Exiting...")


    def get_current_airspeed(self) -> int:
        """
        Returns the airspeed from the POGI file

        Returns
        -------
        int:
            Current airspeed of the plane
        """
        self.__read_from_pogi_file()
        airspeed = self.pogiData["airspeed"]
        if type(airspeed) == int:
            return airspeed
        else:
            if self.__is_null(airspeed):
                raise ValueError("Airspeed not found in the POGI json file. Exiting...")
            elif type(airspeed != int):
                raise TypeError("Airspeed in the POGI file was not an int. Exiting...")


    def get_is_landed(self) -> bool:
        """
        Returns if the plane has landed from the POGI file

        Returns
        -------
        bool:
            True if plane landed, else False
        """
        self.__read_from_pogi_file()
        is_landed = self.pogiData["is_landed"]
        if type(is_landed) == bool:
            return is_landed
        else:
            if self.__is_null(is_landed):
                raise ValueError("Is_landed not found in the POGI json file. Exiting...")
            elif type(is_landed != bool):
                raise TypeError("Is_landed in the POGI file was not an int. Exiting...")


    def get_euler_camera(self) -> dict:
        """
        Returns the euler coordinates of the camera on the plane from the POGI file

        Returns
        -------
        dict:
            Returns a dictionary that contains a set of three euler coordinates with names alpha, beta and gamma
        """
        self.__read_from_pogi_file()
        euler = self.pogiData["euler_camera"]
        if (type(euler) != dict or (
                type(euler['alpha']) != float or type(euler['beta']) != float or type(euler['gamma']) != float)):
            if self.__is_null(euler):
                raise ValueError("Euler camera not found in the POGI json file. Exiting...")
            elif self.__is_null(euler['alpha']):
                raise ValueError("Alpha not found in euler camera json file. Exiting...")
            elif self.__is_null(euler['beta']):
                raise ValueError("Beta not found in euler camera json file. Exiting...")
            elif self.__is_null(euler['gamma']):
                raise ValueError("Gamma not found in euler camera json file. Exiting...")

            elif type(euler) != dict:
                raise TypeError("Euler Camera in the POGI file was not a float. Exiting...")
            elif type(euler['alpha']) != float:
                raise TypeError("Alpha in the POGI file was not a float. Exiting...")
            elif type(euler['beta']) != float:
                raise TypeError("Beta in the POGI file was not a float. Exiting...")
            elif type(euler['gamma']) != float:
                raise TypeError("Gamma in the POGI file was not a float. Exiting...")
        return euler

    def get_euler_plane(self) -> dict:
        """
        Returns the euler coordinates of the plane itself from the POGI file

        Returns
        -------
        dict:
            Returns a dictionary that contains a set of three euler coordinates with names alpha, beta and gamma
        """
        self.__read_from_pogi_file()
        euler = self.pogiData["euler_plane"]

        if (type(euler) != dict or (
                type(euler['alpha']) != float or type(euler['beta']) != float or type(euler['gamma']) != float)):
            if self.__is_null(euler):
                raise ValueError("Euler plane not found in the POGI json file. Exiting...")
            elif self.__is_null(euler['alpha']):
                raise ValueError("Alpha not found in euler plane json file. Exiting...")
            elif self.__is_null(euler['beta']):
                raise ValueError("Beta not found in euler plane json file. Exiting...")
            elif self.__is_null(euler['gamma']):
                raise ValueError("Gamma not found in euler plane json file. Exiting...")

            elif type(euler) != dict:
                raise TypeError("Euler Plane in the POGI file was not a float. Exiting...")
            elif type(euler['alpha']) != float:
                raise TypeError("Alpha in the POGI file was not a float. Exiting...")
            elif type(euler['beta']) != float:
                raise TypeError("Beta in the POGI file was not a float. Exiting...")
            elif type(euler['gamma']) != float:
                raise TypeError("Gamma in the POGI file was not a float. Exiting...")
        return euler



    def get_gps_coordinate(self) -> dict:
        """
        Returns the gps coordinates of the plane from the POGI file

        Returns
        -------
        dict:
            Returns a dictionary that contains a set of two coordinates, latitude and longitude denotes with "lat" and "lng"
        """
        self.__read_from_pogi_file()
        gps = self.pogiData["gps"]

        if (type(gps) != dict or (
                type(gps['lat']) != float or type(gps['lng']) != float)):
            if self.__is_null(gps):
                raise ValueError("GPS camera not found in the POGI json file. Exiting...")
            elif self.__is_null(gps['lat']):
                raise ValueError("Lat not found in gps coordinates json file. Exiting...")
            elif self.__is_null(gps['lng']):
                raise ValueError("Lng not found in gps coordinates json file. Exiting...")

            elif type(gps) != dict:
                raise TypeError("GPS in the POGI file was not a dict. Exiting...")
            elif type(gps['lat']) != float:
                raise TypeError("Lat in the POGI file was not a float. Exiting...")
            elif type(gps['lng']) != float:
                raise TypeError("Lng in the POGI file was not a float. Exiting...")
        return gps


    def set_gps_coordinates(self, gpsCoordinates: dict):
        """
        Write GPS coordinates to PIGO JSON file

        Paramaters
        ----------
        gpsCoordinates: dict
            Dictionary containing GPS coordinates to write
        """
        if gpsCoordinates is None:
            raise ValueError("GPS Coordinates must be a dict and not None.")
        if type(gpsCoordinates) is not dict:
            raise TypeError("GPS Coordinates must be a dict and not {}".format(type(gpsCoordinates)))
        for attribute in ("latitude", "longitude", "altitude"):
            if attribute not in gpsCoordinates.keys():
                raise KeyError("GPS Coordinates must contain {} key".format(attribute))
        for key in gpsCoordinates.keys():
            if type(gpsCoordinates[key]) is not float:
                raise TypeError("GPS Coordinates {} key must be a float".format(key))

        self.__pigoData.update({"gpsCoordinates" : gpsCoordinates})
        self.__write_to_pigo_file()

    def set_ground_commands(self, groundCommands: dict):
        """
        Write ground commands to PIGO JSON file

        Paramaters
        ----------
        groundCommands: dict
            Dictionary containing heading (float) and latestDistance (float) to write
        """
        if groundCommands is None:
            raise ValueError("Ground Commands must be a dict and not None.")
        if type(groundCommands) is not dict:
            raise TypeError("Ground Commands must be a dict and not {}".format(type(groundCommands)))
        for attribute in ("heading", "latestDistance"):
            if attribute not in groundCommands.keys():
                raise KeyError("Ground Commands must contain {} key".format(attribute))
        for key in groundCommands.keys():
            if type(groundCommands[key]) is not float:
                raise TypeError("Ground Commands {} key must be a float".format(key))

        self.__pigoData.update({"groundCommands" : groundCommands})
        self.__write_to_pigo_file()

    def set_gimbal_commands(self, gimbalCommands: dict):
        """
        Write gimbal commands to PIGO JSON file

        Paramaters
        ----------
        gimbalCommands: dict
            Dictionary containing gimbal commands to write
        """
        if gimbalCommands is None:
            raise ValueError("Gimbal Commands must be a dict and not None.")
        if type(gimbalCommands) is not dict:
            raise TypeError("Gimbal Commands must be a dict and not {}".format(type(gimbalCommands)))
        for attribute in ("pitch", "yaw"):
            if attribute not in gimbalCommands.keys():
                raise KeyError("Gimbal Commands must contain {} key".format(attribute))
        for key in gimbalCommands.keys():
            if type(gimbalCommands[key]) is not float:
                raise TypeError("Gimbal Commands {} key must be a float".format(key))

        self.__pigoData.update({"gimbalCommands" : gimbalCommands})
        self.__write_to_pigo_file()

    def set_begin_landing(self, beginLanding: bool):
        """
        Write begin landing command to PIGO JSON file

        Paramaters
        ----------
        beginLanding: bool
            Boolean containing whether or not to initiate landing sequence
        """
        if beginLanding is None:
            raise ValueError("Begin Landing must be a bool and not None.")
        if type(beginLanding) is not bool:
            raise TypeError("Begin Landing must be a bool and not {}".format(type(beginLanding)))

        self.__pigoData.update({"beginLanding" : beginLanding})
        self.__write_to_pigo_file()

    def set_begin_takeoff(self, beginTakeoff: bool):
        """
        Write begin takeoff command to PIGO JSON file

        Paramaters
        ----------
        beginTakeoff: bool
            Boolean containing whether or not to initiate takeoff sequence
        """
        if beginTakeoff is None:
            raise ValueError("Begin Takeoff must be a bool and not None.")
        if type(beginTakeoff) is not bool:
            raise TypeError("Begin Takeoff must be a bool and not {}".format(type(beginTakeoff)))

        self.__pigoData.update({"beginTakeoff" : beginTakeoff})
        self.__write_to_pigo_file()

    def set_disconnect_autopilot(self, disconnectAutoPilot: bool):
        """
        Write disconnect autopilot to PIGO JSON file

        Paramaters
        ----------
        disconnectAutoPilot: bool
            Boolean containing whether or not to disconnect auto pilot
        """
        if disconnectAutoPilot is None:
            raise ValueError("Disconnect Autopilot must be a bool and not None.")
        if type(disconnectAutoPilot) is not bool:
            raise TypeError("Disconnect Autopilot must be a bool and not {}".format(type(disconnectAutoPilot)))

        self.__pigoData.update({"disconnectAutoPilot" : disconnectAutoPilot})
        self.__write_to_pigo_file()

    @property
    def pigoFileDirectory(self):
        """
        Return PIGO JSON file directory

        Returns
        ----------
        pigoFileDirectory: str
            Contains directory to PIGO JSON file
        """
        return self._pigoFileDirectory

    @pigoFileDirectory.setter
    def pigoFileDirectory(self, pigoFileDirectory: str):
        """
        Sets PIGO JSON file directory

        Parameters
        ----------
        pigoFileDirectory: str
            Contains directory to PIGO JSON file
        """
        if pigoFileDirectory is None:
            raise ValueError("PIGO File Directory must be a str and not None.")
        if type(pigoFileDirectory) is not str:
            raise TypeError("PIGO File Directory must be a str and not {}".format(type(pigoFileDirectory)))
        if not os.path.isfile(pigoFileDirectory):
            raise FileNotFoundError("The PIGO file directory must be a valid file")
        if not pigoFileDirectory.endswith(".json"):
            raise ValueError("The PIGO file directory must have a '.json' file extension")
        self._pigoFileDirectory = pigoFileDirectory

    @property
    def pogiFileDirectory(self):
        """
        Return POGI JSON file directory

        Returns
        ----------
        pogiFileDirectory: str
            Contains directory to POGI JSON file
        """
        return self._pogiFileDirectory

    @pogiFileDirectory.setter
    def pogiFileDirectory(self, pogiFileDirectory: str):
        """
        Sets POGI JSON file directory

        Parameters
        ----------
        pogiFileDirectory: str
            Contains directory to POGI JSON file
        """
        if pogiFileDirectory is None:
            raise ValueError("POGI File Directory must be a str and not None.")
        if type(pogiFileDirectory) is not str:
            raise TypeError("POGI File Directory must be a str and not {}".format(type(pogiFileDirectory)))
        if not os.path.isfile(pogiFileDirectory):
            raise FileNotFoundError("The POGI file directory must be a valid file")
        if not pogiFileDirectory.endswith(".json"):
            raise ValueError("The POGI file directory must have a '.json' file extension")
        self._pogiFileDirectory = pogiFileDirectory