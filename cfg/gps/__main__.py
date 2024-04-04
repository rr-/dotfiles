from libdotfiles.packages import try_install
from libdotfiles.util import HOME_DIR, PKG_DIR

try_install("gpsd")

dests = [
    HOME_DIR / ".config/google-chrome/NativeMessagingHosts",
    HOME_DIR / ".config/chromium/NativeMessagingHosts",
    HOME_DIR / ".config/BraveSoftware/Brave-Browser/NativeMessagingHosts",
]
config_path = PKG_DIR / "au.id.micolous.gpspipe.json"
config = config_path.read_text().replace(
    "{PATH}", str(PKG_DIR / "gpspipew.py")
)

for dest in dests:
    dest.mkdir(parents=True, exist_ok=True)
    (dest / config_path.name).write_text(config)

print("To finish, install this extension:")
print(
    "https://chrome.google.com/webstore/detail/gpsd-chrome-polyfill/dmfdcjlppdohhegplckcbohgbbfcdfjd"
)
