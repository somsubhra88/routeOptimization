ECHO "*******************************************************************************">>"D:\SomSubhra\Route Optimization\RO.log"
ECHO "*******************************************************************************">>"D:\SomSubhra\Route Optimization\RO.log"


ECHO "Route Optimization started >>> "  %DATE% %TIME%>>"D:\SomSubhra\Route Optimization\RO.log"
CALL "C:\Windows\py.exe" "D:\SomSubhra\Route Optimization\Ant.py"
TIMEOUT /T 10 /NOBREAK
ECHO "Route Optimization Ended >>> "  %DATE% %TIME%>>"D:\SomSubhra\Route Optimization\RO.log"

ECHO "Mailing Started >>> "  %DATE% %TIME%>>"D:\SomSubhra\Route Optimization\RO.log"
CALL "C:\Windows\py.exe" "D:\SomSubhra\Route Optimization\gmail_cron.py"
TIMEOUT /T 10 /NOBREAK
ECHO "Mailing Done>>> "  %DATE% %TIME%>>"D:\SomSubhra\Route Optimization\RO.log"

ECHO "*******************************************************************************">>"D:\SomSubhra\Route Optimization\RO.log"
ECHO "*******************************************************************************">>"D:\SomSubhra\Route Optimization\RO.log"