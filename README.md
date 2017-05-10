# zfscheck
The purpose of this script is to check your zpool status and email you via your own Gmail account if something is wrong.

First, you'll need client credentials in order to set up emailing.
1. To do so, set up a new project in Google Cloud Platform here: https://console.developers.google.com/start/api?id=gmail
2. Click **Continue**, then **Go to credentials**.
3. On the **Add credentials to your project** page, click the **Cancel** button.
4. At the top of the page, select the **OAuth consent screen** tab. Select an **Email address**, enter a **Product name** if not already set, and click the **Save** button.
5. Select the **Credentials** tab, click the **Create credentials** button and select **OAuth client ID**.
6. Select the application type **Other**, enter the name "ZFS Check Client", and click the **Create** button.
7. Click **OK** to dismiss the resulting dialog.
8. Click the (Download JSON) button to the right of the client ID.
9. Move this file to your zfscheck.py directory and rename it `client_secret.json`

Second, you'll need the Google Client Library

`pip install --upgrade google-api-python-client`

Lastly, run once to authorize the script to send email as you, and then add a cron job to run daily

`python zfscheck.py --noauth_local_webserver`

`(crontab -l ; echo "0 * * * * cd /path/to/zfscheck && python zfscheck.py") | crontab`
