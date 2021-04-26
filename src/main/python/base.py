from fbs_runtime.application_context.PyQt5 import ApplicationContext as context
import os
import json

app_data = os.getenv('APPDATA')
settings_dir = os.path.join(app_data, "Bangla Voice Calculator\Settings")
settings_file = settings_dir+r"/settings.json"
if not os.path.exists(settings_dir+r"/settings.json"):
    try:
        os.makedirs(settings_dir)
    except:
        pass
    with open(settings_file,'w') as f:
        settings = {'limit': None, 'bangla': True}
        json.dump(settings,f)

appContext = context()

