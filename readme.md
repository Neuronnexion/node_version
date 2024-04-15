# NODE(NVM) VERSION CHECKER PLUGIN FOR CHECKMK

## USAGE

This plugin uses the newreleases.io API to verify a host is using the latest node version for all major node versions.

It only works with node versions installed with nvm.

If an outdated version has CVEs, the CVE numbers will be listed in the summary along with an helpful link to cve.mitre.org.

## INSTALLATION

### Pre-installation

* Create an account on newreleases.io
* Add the node repo to your list of tracked projects
  * "Chose project provider": GitHub
  * "Enter project name or URL": nodejs/node
* Create a newreleases.io API key
  * Open the menu by hovering over your username in the top right corner, then click on "API keys"
  * Click on "New Key"
  * Name the key "CheckMK" and add network restrictions if needed
  * Copy the key

### Installation

* Install the MKP on your site
* Search "Node version parameters" in the setup menu
* Create a rule and enter your newreleases.io API key
* Do this on each host to monitor:
  * Install the agent
  * In the folder `/usr/lib/check_mk_agent/local` , create a text file named `node_version.cfg`
  * This file should contain the absolute path to where the NVM node versions are (should be `$USER/.nvm/versions/node`)
* Run service discovery on host

The plugin's first execution will take some time as it is building the cache. The cache will be refreshed every 6 hours.
