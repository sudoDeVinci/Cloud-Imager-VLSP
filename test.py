import tomllib as toml

def load_toml(file_path:str) -> dict | None:
    toml_data = None
    try:
        with open(file_path, 'rb') as file:
            toml_data = toml.load(file)
            if not toml_data: return None
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None
    except toml.TOMLDecodeError as e:
        print(f"Error decoding TOML file: {e}")
        return None

    return toml_data

out = load_toml("firmware_cfg.toml")
conf = out["firmware"]

if conf is not None:
    for key in conf:
        print(f"{key} : {conf[key]}")