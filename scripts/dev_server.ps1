cd $PSScriptRoot\..

$env:FLASK_APP='app.py'
$env:FLASK_ENV='development'
flask run --host=0.0.0.0
