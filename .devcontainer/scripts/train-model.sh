#!/bin/bash

(cd /app && rasa train -vv > /app/train_logs.txt)
