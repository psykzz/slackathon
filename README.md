# slackathon
A simple decorator-based Slack bot framework, inspired by [slackbot](https://github.com/lins05/slackbot) and [errbot](https://github.com/errbotio/errbot)

## Installation

    git clone https://github.com/MasterCheese/slackathon.git
    pip install slackathon
  
## Usage

TBC

## Configuration

TBC

## Creating plugins
Plugins are subclasses of the included BotPlugin class, which provides a bunch of useful helper functions (Or at least it will)

Commands are specified using one of the included decorators @listen_to and @respond_to. These accept a regex pattern and an [event type](https://api.slack.com/events). Both of these are optional, defaulting to ".*" and "message" respectfully

**respond_to** - Triggered on DMs and messages that begin with the bot's username, or one of the defined aliases  
**listen_to** - Triggered on any message that the bot can see

Only one of these can be specified per command, any more will produce unexpected results.

### Example

    TBC

There is also the capacity to create an event filter, which will receive all events passed to the bot. These functions will be passed both the event, and the name of the command about to be run. This allows for modification of the event, to allow handling of ACLs, muting etc.
