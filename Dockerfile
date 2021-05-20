# (c) 2021 Copyright, Real-Time Innovations, Inc.  All rights reserved.
# No duplications, whole or partial, manual or electronic, may be made
# without express written permission.  Any such copies, or revisions thereof,
# must display this notice unaltered.
# This code contains trade secrets of Real-Time Innovations, Inc.
FROM ubuntu:20.04

ENV DEBIAN_FRONTEND="noninteractive"

RUN apt update && apt install -y \
    gcc \
    g++ \
    clang \
    libssl-dev \
    make \
    cmake \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

USER jenkins

RUN pip3 install scan-build --user
