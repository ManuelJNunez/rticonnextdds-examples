<!-- markdownlint-disable MD033 MD041 MD013 -->
This build is being executed on an internal Jenkins, only RTI employees can access the build logs. To give information to external users, we have configured the status checks.

# Pipeline description

The pipeline is defined [here](https://github.com/rticommunity/rticonnextdds-examples/blob/develop/Jenkinsfile) and the purpose of this pipeline is to build the examples using the last staging packages of RTI Connext® DDS and to analyze the build using `analyze-build` from `clang-tools`.

# Environment details

| Option                   | Setting               |
| ------------------------ | --------------------- |
| RTI Connext® DDS Version | 6.1.0 |
| System                   | Linux    |
| Machine type             | x86_64        |
| OS release               | 5.4.0-74-generic          |
| CLANG Version | 10.0.0 |


<details><summary>Dockerfile</summary>
<p>

```Dockerfile
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
    clang-tools-10 \
    && rm -rf /var/lib/apt/lists/*

ENV PATH=/usr/share/clang/scan-build-py-10/bin:${PATH}

USER jenkins

```

</p>
</details>

<details><summary>Jenkinsfile</summary>
<p>

```Groovy
def DETAILS_URL="https://www.rti.com"
def detailsText
def detailsTextBuild
def detailstextStatic

pipeline {
    agent {
        dockerfile {
            filename 'Dockerfile'
            label 'docker'
        }
    }

    environment {
        RTI_INSTALLATION_PATH = "${WORKSPACE}/unlicensed"
        RTI_LOGS_FILE = "${WORKSPACE}/output_logs.txt"
    }

    stages {
        stage('Download Packages') {
            steps {
                sh 'python3 resources/ci_cd/jenkins_output.py'

                script {
                    detailsText = readFile("jenkins_output.md")
                }

                publishChecks detailsURL: DETAILS_URL, name: STAGE_NAME,
                    status: 'IN_PROGRESS', title: 'Downloading', text: detailsText,
                    summary: ':arrow_down: Downloading RTI Connext DDS libraries...'

                rtDownload (
                    serverId: 'rti-artifactory',
                    spec: '''{
                        "files": [
                        {
                            "pattern": "connext-ci/pro/weekly/",
                            "props": "rti.artifact.architecture=x64Linux4gcc7.3.0;rti.artifact.kind=staging",
                            "sortBy": ["created"],
                            "sortOrder": "desc",
                            "limit": 1,
                            "flat": true
                        }]
                    }''',
                )

                sh 'tar zxvf connextdds-staging-x64Linux4gcc7.3.0.tgz unlicensed/'
                
                sh 'python3 resources/ci_cd/jenkins_output.py'

                script {
                    detailsText = readFile("jenkins_output.md")
                }
            }

            post {
                success {
                    publishChecks detailsURL: DETAILS_URL, name: STAGE_NAME,
                        summary: ':white_check_mark: RTI Connext DDS libraries downloaded.',
                        title: 'Passed', text: detailsText
                }
                failure {
                    publishChecks conclusion: 'FAILURE', detailsURL: DETAILS_URL,
                        name: STAGE_NAME, title: 'Failed', text: detailsText,
                        summary: ':warning: Failed downloading RTI Connext DDS libraries.'
                }
                aborted {
                    publishChecks conclusion: 'CANCELED', detailsURL: DETAILS_URL,
                        name: STAGE_NAME, title: 'Aborted', text: detailsText,
                        summary: ':no_entry: The download of RTI Connext DDS libraries was aborted.'
                }
            }
        }

        stage('Build') {
            steps {
                publishChecks detailsURL: DETAILS_URL, name: STAGE_NAME, 
                    status: 'IN_PROGRESS', summary: ':wrench: Building all the examples...', 
                    title: 'Building', text: detailsText

                sh 'python3 resources/ci_cd/linux_build.py | tee $RTI_LOGS_FILE'
            }

            post {
                always{
                    sh 'python3 resources/ci_cd/jenkins_output.py'
                    script {
                        detailsTextBuild = readFile("jenkins_output.md")
                    }
                }
                success {
                    publishChecks detailsURL: DETAILS_URL, name: STAGE_NAME,
                        summary: ':white_check_mark: All the examples were built succesfully.',
                        title: 'Passed', text: detailsTextBuild
                }
                failure {
                    publishChecks conclusion: 'FAILURE', detailsURL: DETAILS_URL,
                        name: STAGE_NAME, title: 'Failed', text: detailsTextBuild,
                        summary: ':warning: There was an error building the examples.'
                }
                aborted {
                    publishChecks conclusion: 'CANCELED', detailsURL: DETAILS_URL,
                        name: STAGE_NAME, title: 'Aborted', text: detailsTextBuild,
                        summary: ':no_entry: The examples build was aborted'
                }
            }
        }

        stage('Static Analysis') {
            steps {
                sh 'python3 resources/ci_cd/jenkins_output.py'

                script {
                    detailsText = readFile("jenkins_output.md")
                }

                publishChecks detailsURL: DETAILS_URL, name: STAGE_NAME, 
                    status: 'IN_PROGRESS', title: 'In progress', text: detailsText,
                    summary: ':mag: Analysing all the examples...'

                sh 'python3 resources/ci_cd/linux_static_analysis.py | tee $RTI_LOGS_FILE'
            }

            post {
                always {
                    sh 'python3 resources/ci_cd/jenkins_output.py'

                    script {
                        detailsTextStatic = readFile("jenkins_output.md")
                    }
                }
                success {
                    publishChecks detailsURL: DETAILS_URL, name: STAGE_NAME,
                        summary: ':white_check_mark: Succesfully analysed',
                        title: 'Passed', text: detailsTextStatic
                }
                failure {
                    publishChecks conclusion: 'FAILURE', detailsURL: DETAILS_URL,
                        name: STAGE_NAME, title: 'Failed', text: detailsTextStatic,
                        summary: ':warning: The static analysis failed'
                }
                aborted {
                    publishChecks conclusion: 'CANCELED', detailsURL: DETAILS_URL,
                        name: STAGE_NAME, title: 'Aborted', text: detailsTextStatic,
                        summary: ':no_entry: The static analysis was aborted'
                }
            }
        }
    }
}

```

</p>
</details>

<details><summary>Logs</summary>
<p>

```plaintext
There are no logs for this job
```

</p>
</details>
