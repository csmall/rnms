#!/bin/sh
sudo -u postgres sh -c "psql -c 'DROP DATABASE \"rnms-devel\"'; psql -c 'CREATE DATABASE \"rnms-devel\"'"
