# 384_wellplate_automation

##Pre-requisite
If GitHub CLI is not installed or the operator is unaware of it, please do the following steps:
- For windows:
  1. Open powershell
  2. Copy and paste the following: winget list --id GitHub.cli
  3. If step 2 has no output, then proceed with step 4 else proceed with step 5
  4. Copy and paste the following: winget install --id GitHub.cli
  5. Lastly, copy and paste the following: winget upgrade --id GitHub.cli

# Installation
## Windows
1. Open the powershell and create a new folder by copy and pasting: New-Item -Path . -ItemType DragonFlyAutomator
5. Create python environment via: python -m venv DragonFlyAutomator  # Afterwards sys.prefix and sys.exec_prefix point to this
5. Copy and paste: DragonFlyAutomator\Scripts\Activate.ps1
6. 
4. Copy and paste, then answer "yes" if you have a Github account, if not type "no": gh auth login
## Ubuntu
(type -p wget >/dev/null || (sudo apt update && sudo apt-get install wget -y)) \
&& sudo mkdir -p -m 755 /etc/apt/keyrings \
&& wget -qO- https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null \
&& sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg \
&& echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
&& sudo apt update \
&& sudo apt install gh -y


1. Open the powershell and create a new folder by copy and pasting: mkdir  DragonFlyAutomator
5. Create python environment via: python -m venv DragonFlyAutomator  # Afterwards sys.prefix and sys.exec_prefix point to this
5. Copy and paste: source DragonFlyAutomator/bin/activate

4. Create python environment via: python -m venv 348_wellplate_automation  # Afterwards sys.prefix and sys.exec_prefix point to this
5. 
