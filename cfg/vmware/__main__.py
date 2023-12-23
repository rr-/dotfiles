from libdotfiles.packages import try_install
from libdotfiles.util import get_distro_name, run

if get_distro_name() != "arch":
    raise NotImplementedError("not implemented")

try_install("vmware-workstation")
try_install("cdrtools")  # for creating .iso - mkisofs -o image.iso source/

run(["sudo", "modprobe", "-a", "vmw_vmci", "vmmon"], check=False)
run(["sudo", "systemctl", "enable", "vmware-networks"], check=False)
run(["sudo", "systemctl", "start", "vmware-networks"], check=False)

# windows 7 needs the following updates before installing vmware tools:
# http://download.windowsupdate.com/c/msdownload/update/software/secu/2019/03/windows6.1-kb4490628-x86_3cdb3df55b9cd7ef7fcb24fc4e237ea287ad0992.msu
# http://download.windowsupdate.com/c/msdownload/update/software/secu/2019/09/windows6.1-kb4474419-v3-x86_0f687d50402790f340087c576886501b3223bec6.msu
