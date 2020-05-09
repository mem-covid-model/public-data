# Powershell wrapper for Python script

# Make sure we're in the right directory
Set-Location C:\Users\jesse\OneDrive\epicurve\public-data\mobility_data\code

# Run python script
python scrape.py

# Move back to mobility_data folder
Set-Location ../

# Add-commit-push updates
git add *
git commit -m "Updated mobility metrics"
git push