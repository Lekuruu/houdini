database = {
    "Address": "localhost",
    "Username": "postgres",
    "Password": "password",
    "Name": "houdini",
}

redis = {
    "Address": "127.0.0.1",
    "Port": 6379
}

servers = {
    "Login": {
        "Address": "0.0.0.0",
        "Port": 6112,
        "World": False,
        "Plugins": [
            "Example"
        ],
        "Logging": {
            "General": "logs/login.log",
            "Errors": "logs/login-errors.log",
            "Level": "DEBUG"
        },
        "LoginFailureLimit": 5,
        "LoginFailureTimer": 3600
    },
    "Wind": {
        "Id": "100",
        "Address": "0.0.0.0",
        "Port": 9875,
        "World": True,
        "Capacity": 200,
        "CacheExpiry": 3600,
        "Plugins": [
            "Commands",
            "Bot",
            "Rank"
        ],
        "Logging": {
            "General": "logs/wind.log",
            "Errors": "logs/wind-errors.log",
            "Level": "INFO"
        }
    }
}