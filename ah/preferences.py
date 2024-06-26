import json
import logging
from typing import List, Dict, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)

async def load_provider_data(provider_data_file_path: str = 'data/providers.json') -> Optional[Dict]:
    try:
        with open(provider_data_file_path, 'r') as provider_data_file:
            provider_data = json.load(provider_data_file)
    except Exception as e:
        logging.error(f'Error reading provider data file: {e}')
        return None
    return provider_data


async def find_preferred_models(service_or_command_name: str, flags: List[str], settings_file_path: str = 'data/preferred_models.json') -> Optional[List[Dict]]:
    if not isinstance(service_or_command_name, str) or not service_or_command_name:
        logging.error('Invalid service_or_command_name')
        return None
    if not isinstance(flags, list) or not all(isinstance(flag, str) for flag in flags):
        logging.error('Invalid flags')
        return None

    try:
        with open(settings_file_path, 'r') as settings_file:
            pass
    except FileNotFoundError:
        with open(settings_file_path, 'w') as settings_file:
            json.dump([], settings_file)

    try:
        with open(settings_file_path, 'r') as settings_file:
            settings = json.load(settings_file)
    except Exception as e:
        logging.error(f'Error reading settings file: {e}')
        return None

    matching_models = []
    # filter by service_or_command_name
    settings = [setting for setting in settings if setting['service_or_command_name'] == service_or_command_name]

    # example settings
    for setting in settings:
        print("setting: ", setting)

        #if setting['flag'] is in flags
        if setting['flag'] in flags:
            matching_models.append(setting)

    if not matching_models:
        logging.debug('No matching models found')
        return None

    providers = await load_provider_data()
    # loop over all matching_models
    # find provider data where provider.model.name == model.name
    # set provider name = provider.plugin
    for model in matching_models:
        for provider in providers:
            for provider_model in provider['model']:
                if provider_model['name'] == model['name']:
                    model['provider'] = provider['plugin']
    logging.debug(f'Matching models found: {matching_models}')
    return matching_models



