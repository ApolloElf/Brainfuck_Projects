import base64
import ctypes
import hashlib
import json
import posixpath
from pathlib import Path

from webdav3.client import Client


LOCAL = Path(r"C:\Users\skoeh\Brainfuck_Projects\Brainfuck")
REMOTE = "/Files/Brainfuck/"
STATE_FILE = Path.home() / ".brainfuck_iserv_sync.json"
CONFIG_FILE = Path.home() / ".brainfuck_iserv_credentials.json"

EXCLUDE = {
    ".git",
    "sync.py",
}


class DATA_BLOB(ctypes.Structure):
    _fields_ = [
        ("cbData", ctypes.c_ulong),
        ("pbData", ctypes.POINTER(ctypes.c_char)),
    ]


def encrypt_password(password):
    data = password.encode("utf-8")

    blob_in = DATA_BLOB(
        len(data),
        ctypes.cast(
            ctypes.create_string_buffer(data),
            ctypes.POINTER(ctypes.c_char),
        ),
    )

    blob_out = DATA_BLOB()

    if not ctypes.windll.crypt32.CryptProtectData(
        ctypes.byref(blob_in),
        None,
        None,
        None,
        None,
        0,
        ctypes.byref(blob_out),
    ):
        raise RuntimeError("Passwort konnte nicht verschlüsselt werden.")

    encrypted = ctypes.string_at(
        blob_out.pbData,
        blob_out.cbData,
    )

    ctypes.windll.kernel32.LocalFree(blob_out.pbData)

    return base64.b64encode(encrypted).decode("ascii")


def decrypt_password(encrypted):
    data = base64.b64decode(encrypted)

    blob_in = DATA_BLOB(
        len(data),
        ctypes.cast(
            ctypes.create_string_buffer(data),
            ctypes.POINTER(ctypes.c_char),
        ),
    )

    blob_out = DATA_BLOB()

    if not ctypes.windll.crypt32.CryptUnprotectData(
        ctypes.byref(blob_in),
        None,
        None,
        None,
        None,
        0,
        ctypes.byref(blob_out),
    ):
        raise RuntimeError("Gespeichertes Passwort konnte nicht entschlüsselt werden.")

    password = ctypes.string_at(
        blob_out.pbData,
        blob_out.cbData,
    ).decode("utf-8")

    ctypes.windll.kernel32.LocalFree(blob_out.pbData)

    return password


def save_credentials(hostname, username, password):
    config = {
        "hostname": hostname,
        "username": username,
        "password": encrypt_password(password),
    }

    with CONFIG_FILE.open("w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)


def get_credentials():
    if CONFIG_FILE.exists():
        with CONFIG_FILE.open("r", encoding="utf-8") as f:
            config = json.load(f)

        password = decrypt_password(config["password"])

        return {
            "hostname": config["hostname"],
            "username": config["username"],
            "password": password,
        }

    print("Keine gespeicherten IServ-Anmeldedaten gefunden.")
    print()

    hostname = input("IServ-Adresse (z.B. schule.de): ").strip()
    username = input("IServ Benutzername: ").strip()

    import getpass
    password = getpass.getpass("IServ Passwort: ")

    save_credentials(
        hostname,
        username,
        password,
    )

    print()
    print("Anmeldedaten wurden gespeichert.")
    print()

    return {
        "hostname": hostname,
        "username": username,
        "password": password,
    }


def create_client(credentials):
    return Client({
        "webdav_hostname": f"https://webdav.{credentials['hostname']}",
        "webdav_login": credentials["username"],
        "webdav_password": credentials["password"],
    })


def hash_file(path):
    h = hashlib.sha256()

    with path.open("rb") as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)

    return h.hexdigest()


def local_files():
    result = {}

    for path in LOCAL.rglob("*"):
        if not path.is_file():
            continue

        relative = path.relative_to(LOCAL)

        if any(part in EXCLUDE for part in relative.parts):
            continue

        result[str(relative).replace("\\", "/")] = hash_file(path)

    return result


def remote_files(client, directory=REMOTE):
    result = {}

    for item in client.list(directory):
        name = item.rstrip("/").split("/")[-1]

        if name in (".", ".."):
            continue

        remote_path = posixpath.join(directory, name)

        if item.endswith("/"):
            result.update(
                remote_files(client, remote_path + "/")
            )
        else:
            temp = LOCAL / ".iserv_sync_temp" / name
            temp.parent.mkdir(parents=True, exist_ok=True)

            try:
                client.download_sync(
                    remote_path=remote_path,
                    local_path=str(temp),
                )

                relative = remote_path[len(REMOTE):]
                result[relative] = hash_file(temp)

            finally:
                if temp.exists():
                    temp.unlink()

    return result


def load_state():
    if not STATE_FILE.exists():
        return None

    with STATE_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_state(files):
    with STATE_FILE.open("w", encoding="utf-8") as f:
        json.dump(files, f, indent=2)


def upload(client, relative):
    local = LOCAL / Path(relative)
    remote = posixpath.join(REMOTE, relative)

    print(f"  lokal -> IServ: {relative}")

    client.upload_sync(
        remote_path=remote,
        local_path=str(local),
    )


def download(client, relative):
    local = LOCAL / Path(relative)
    remote = posixpath.join(REMOTE, relative)

    local.parent.mkdir(parents=True, exist_ok=True)

    print(f"  IServ -> lokal: {relative}")

    client.download_sync(
        remote_path=remote,
        local_path=str(local),
    )


def delete_local(relative):
    path = LOCAL / Path(relative)

    if path.exists():
        print(f"  lösche lokal: {relative}")
        path.unlink()


def delete_remote(client, relative):
    remote = posixpath.join(REMOTE, relative)

    print(f"  lösche auf IServ: {relative}")

    client.clean(remote)


def sync():
    print("=== Brainfuck IServ Sync ===")
    print()

    credentials = get_credentials()
    client = create_client(credentials)

    print("Lese lokalen Ordner...")
    local = local_files()

    print("Lese IServ...")
    remote = remote_files(client)

    state = load_state()

    if state is None:
        print()
        print("Keine Baseline gefunden.")
        print("Da beide Ordner bereits synchron sind,")
        print("wird jetzt die Baseline erstellt.")

        save_state(local)

        print("Baseline erstellt.")
        return

    print()
    print("Vergleiche Änderungen...")

    all_files = set(state) | set(local) | set(remote)

    actions = []
    conflicts = []

    for file in sorted(all_files):
        old = state.get(file)
        local_hash = local.get(file)
        remote_hash = remote.get(file)

        local_changed = local_hash != old
        remote_changed = remote_hash != old

        if local_changed and remote_changed:
            if local_hash == remote_hash:
                continue

            conflicts.append(file)

        elif local_changed:
            if local_hash is None:
                actions.append(("delete_remote", file))
            else:
                actions.append(("upload", file))

        elif remote_changed:
            if remote_hash is None:
                actions.append(("delete_local", file))
            else:
                actions.append(("download", file))

    if conflicts:
        print()
        print("!!! KONFLIKT !!!")
        print()

        for file in conflicts:
            print(f"  {file}")

        print()
        print("Nichts wurde übertragen.")
        return

    if not actions:
        print("Alles ist synchron.")
        return

    print()
    print(f"{len(actions)} Änderung(en) gefunden:")
    print()

    for action, file in actions:
        print(f"  {action:15} {file}")

    print()
    answer = input("Änderungen ausführen? [j/N]: ").strip().lower()

    if answer != "j":
        print("Abgebrochen.")
        return

    print()

    for action, file in actions:
        if action == "upload":
            upload(client, file)

        elif action == "download":
            download(client, file)

        elif action == "delete_local":
            delete_local(file)

        elif action == "delete_remote":
            delete_remote(client, file)

    new_local = local_files()
    save_state(new_local)

    print()
    print("Synchronisation abgeschlossen.")


if __name__ == "__main__":
    sync()
