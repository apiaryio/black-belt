const assert = require('chai').assert
const {assert_cmd_output_equals} = require('./assert-output.js')

describe('Init', () => {
    it('returns text', () => {
        return assert_cmd_output_equals("Initial configuration!\n", ["init"])
    })
})