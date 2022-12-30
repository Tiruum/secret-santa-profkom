var PythonShell = require('python-shell');
const express = require('express')
const app = express()
const port = 3000

app.get('/', (req, res) => {
    //you can use error handling to see if there are any errors
    PythonShell.run('index.py', options, function (err, results) {
        console.log(rusults);
        console.log(err);
    })
    res.send('Hello World!')
})

app.listen(port, () => {
  console.log(`Example app listening on port ${port}`)
})