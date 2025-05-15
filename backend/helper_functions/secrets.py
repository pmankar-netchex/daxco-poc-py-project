import os

def get_api_config(environment="tequila"):
    configs = {
        "tequila": {
            "base_endpoint": "https://tequila-employee-api-primary.azurewebsites.net",
            "api_key": "ajZoalNWbVghZ3RtNFAlbUhEcVB5M0I2XlEyWG1YJF4"
        },
        # Add more environments here as needed
        # "staging": { ... },
        # "production": { ... },
    }
    env = environment or os.getenv("ENVIRONMENT", "tequila")
    if env not in configs:
        raise ValueError(f"Unknown environment: {env}")
    return configs[env] 