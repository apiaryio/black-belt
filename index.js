#!/usr/bin/env node

const initModule = require('./lib/cmds/init.js')

require('yargs') // eslint-disable-line
.usage('$0 <cmd> [args]')
.command('init', 'Initialize application for usage.', (yargs) => {
    console.log("Initial configuration!")
    initModule.run(yargs)
}, (argv) => {
  if (argv.verbose) console.info(`start server on :${argv.port}`)
})
.option('verbose', {
  alias: 'v',
  default: false
})
.help()
.argv
