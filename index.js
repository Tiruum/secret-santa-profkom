var PythonShell = require('python-shell');
//you can use error handling to see if there are any errors
PythonShell.run('index.py', options, function (err, results) {
    console.log(rusults);
    console.log(err);
})