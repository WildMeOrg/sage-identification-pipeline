#!/usr/bin/env bash

wget https://dl.min.io/server/minio/release/linux-amd64/minio
chmod +x minio
./minio server /minio
