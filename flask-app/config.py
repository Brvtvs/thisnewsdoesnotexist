port = 5000

# False to disable article generation, such as for testing.
generate_new_articles = False

google_search_api_key = ""
google_custom_search_engine_id = ""

# True to enabling launching EC2 instances (which cost money so keep false unless you need it)
launch_ec2_instances = False
# How often to launch an EC2 instance that can generate grover articles.
launch_ec2_instance_every_X_hours = 2

# telegram bot API token for sending notifications from "contact-us" page
telegram_bot_token = ""
# telegram bot's chat id to send messages to
telegram_bot_chatid = ""