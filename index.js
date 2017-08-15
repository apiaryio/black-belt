#!/usr/bin/env node
require('yargs') // eslint-disable-line
.command('config', 'configure the environment', (yargs) => {
    console.log("Initial configuration!")
}, (argv) => {
  if (argv.verbose) console.info(`start server on :${argv.port}`)
})
.option('verbose', {
  alias: 'v',
  default: false
})
.argv
