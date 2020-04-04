cd $PSScriptRoot\..

$env:FLASK_APP='pilot\app.py'
$env:FLASK_ENV='development'
flask run --host=0.0.0.0
