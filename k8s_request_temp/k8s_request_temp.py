dc_temp='{"kind":"DeploymentConfig","apiVersion":"v1","metadata":{"name":"docker-2048","labels":{"run":"docker-2048"}},"spec":{"strategy":{"type":"Rolling","rollingParams":{"updatePeriodSeconds":1,"intervalSeconds":1,"timeoutSeconds":600,"maxUnavailable":"25%","maxSurge":"25%"},"resources":{}},"triggers":[{"type":"ConfigChange"}],"replicas":1,"selector":{"run":"docker-2048"},"template":{"metadata":{"labels":{"run":"docker-2048"}},"spec":{"containers":[{"name":"docker-2048","image":"index.alauda.cn/asiainfoldp/docker-2048","resources":{},"terminationMessagePath":"/dev/termination-log","imagePullPolicy":"Always"}],"restartPolicy":"Always","terminationGracePeriodSeconds":30,"dnsPolicy":"ClusterFirst","securityContext":{}}}},"status":{}}'