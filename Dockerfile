# ------------------------------------------------------------------------------
# (c) 2021 Copyright, Real-Time Innovations, Inc.  All rights reserved.
# RTI grants Licensee a license to use, modify, compile, and create derivative
# works of the Software.  Licensee has the right to distribute object form only
# for use with RTI products.  The Software is provided "as is", with no warranty
# of any type, including any warranty for fitness for any purpose. RTI is under
# no obligation to maintain or support the Software.  RTI shall not be liable 
# for any incidental or consequential damages arising out of the use or
# inability to use the software.
# ------------------------------------------------------------------------------

FROM ubuntu:22.04

ENV DEBIAN_FRONTEND="noninteractive"

RUN apt update && apt install -y \
    gcc \
    g++ \
    clang \
    libssl-dev \
    make \
    cmake \
    python3 \
    clang-tools-13 \
    && rm -rf /var/lib/apt/lists/*

ENV PATH=/usr/share/clang/scan-build-13/bin:${PATH}

USER jenkins
