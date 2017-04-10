#!/usr/bin/env bash

ps aux | grep [f]acetrack  | grep -v vim | awk '{print $2}' | xargs kill -9
