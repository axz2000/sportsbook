# sportsbook

Some useful git commands

git clone https://github.com/axz2000/sportsbook.git -- Use this to download the git repo (only need this for initial setup). Make sure you are in the desired directory, and it will create a folder named "sportsbook" with the repo.

git pull -- run this command before editing files always. Since for now we will be working together in the main branch, this will make sure you get the latest changes updated locally (will download all changes to the repo since last edit). 

git status -- run this to check check which files you have edited and not committed / staged for commit. Make sure all edited files are staged and committed before pushing.

git add [filename] -- Stages edited file or new file for commit. To change file in repo for everyone else to see must first be staged, then commited, then pushed.

git add --all -- Stages all edited / new files for commit (a good shortcut)

git commit -m "[some message here]" -- This is the unit of change (if there is a problem we can roll it back to the previous commit). Type a message to indicate what changes have been made. Even between pushes you can commit multiple times.

git push -- uploads all commits (changes) to the repo on github for all to see