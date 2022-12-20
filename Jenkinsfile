pipeline {
    agent { label 'jenkinssis2' }
    stages {
        stage(test) {
            steps {
                echo 'Notify GitLab'
                updateGitlabCommitStatus name: 'test', state: 'pending'
	        sh '''ls -l .jenkins
	        sh -x .jenkins'''
                updateGitlabCommitStatus name: 'test', state: 'success'
            }
        }
    }
}
