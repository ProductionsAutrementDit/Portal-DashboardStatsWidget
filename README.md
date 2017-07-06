# Portal-DashboardStatsWidget
Add a widget for Cantemo Portal dashboard showing stats from Saved Searches

![Sample image](https://github.com/ProductionsAutrementDit/Portal-DashboardStatsWidget/blob/master/samples/sample.png)

### Installation
Copy this folder to your Portal plugins folder (`/opt/cantemo/portal/portal/plugins`).

Then launch these commands:
```
cd /opt/cantemo/portal
./manage.py schemamigration dashboardstats --initial
./manage.py migrate
supervisorctl restart portal
```
### How-to use
On Dashboard page, add a new "Sats widget" block.

Choose a saved search and a refresh interval.

Be carefull as setting a too low refresh interval can lead to unecessary high CPU usage.
