from libdotfiles.packages import try_install
from libdotfiles.util import HOME_DIR, PKG_DIR

try_install("gpsd")

dest1 = HOME_DIR / ".config/google-chrome/NativeMessagingHosts"
dest2 = HOME_DIR / ".config/chromium/NativeMessagingHosts"
config_path = PKG_DIR / "au.id.micolous.gpspipe.json"
config = config_path.read_text().replace(
    "{PATH}", str(PKG_DIR / "gpspipew.py")
)

dest1.mkdir(parents=True, exist_ok=True)
dest2.mkdir(parents=True, exist_ok=True)
(dest1 / config_path.name).write_text(config)
(dest2 / config_path.name).write_text(config)

print("To finish, install this extension:")
print(
    "https://chrome.google.com/webstore/detail/gpsd-chrome-polyfill/dmfdcjlppdohhegplckcbohgbbfcdfjd"
)
