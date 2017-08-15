const fs = require('fs')
const assert = require('chai').assert
const {PROGRAM_NAME} = require('./assert-output.js')

describe('Sanity Test', () => {
    it('Main Executable Program Exists', () => {
        assert.isTrue(fs.existsSync(PROGRAM_NAME))
    })
    it('Main Executable Program is executable', () => {
        assert.isUndefined(fs.accessSync(PROGRAM_NAME, fs.constants.X_OK))
    })
})