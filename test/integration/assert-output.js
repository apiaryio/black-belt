const {spawn} = require('child_process')
const assert = require('chai').assert

const PROGRAM_NAME = `${__dirname}/../../index.js`

function assert_cmd_output_equals (expected_stdout, command) {
    return new Promise((resolve, reject) => {
        const proc = spawn(PROGRAM_NAME, command)

        let stdout = ""

        proc.stdout.on('data', (data) => {
            stdout += data.toString()
        })

        proc.on('close', (exitCode) => {
            if (exitCode !== 0)
                reject(new Error(`Exited with non-zero exit code: ${exitCode}`))
            else
                resolve(stdout)
        })
    }).then((stdout) => {
        assert.equal(expected_stdout, stdout)
    })
}

module.exports = {
    assert_cmd_output_equals: assert_cmd_output_equals
}