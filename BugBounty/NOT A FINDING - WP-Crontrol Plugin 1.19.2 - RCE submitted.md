"WP Crontrol allows administrators to manage and schedule WordPress cron events from the admin dashboard. The plugin provides functionality to add cron events with custom PHP callbacks.

It is possible for an administrator to schedule a PHP callback that executes arbitrary PHP code, effectively allowing remote code execution from the WordPress interface. While this functionality requires administrator access to schedule PHP cron callbacks, it creates a high-risk scenario where arbitrary PHP code is executed under the web server user. This could be chained with other misconfigurations or network access, allowing lower-privileged users on the same host or network to intercept or interact with reverse shells initiated by cron events, potentially leading to unauthorized code execution or privilege escalation."

![[Pasted image 20250901145424.png]]

![[Pasted image 20250901145429.png]]

