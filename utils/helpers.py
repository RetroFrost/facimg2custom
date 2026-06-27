import os

def get_bin_path():
    """Returns the path to the bin directory."""
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'bin')

def find_unified_models(device_tree_path):
    """Searches for subdirectories containing BoardConfig.mk."""
    models = []
    if not device_tree_path or not os.path.exists(device_tree_path):
        return models

    for entry in os.scandir(device_tree_path):
        if entry.is_dir():
            if os.path.exists(os.path.join(entry.path, 'BoardConfig.mk')):
                models.append(entry.name)
    return models
