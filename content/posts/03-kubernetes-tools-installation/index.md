---
title: kubelet, kubeadm, kubectl 설치
linkTitle: 03. kubelet, kubeadm, kubectl 설치
date: '2024-03-26T01:04:00+09:00'
tags:
- k8s
- kubernetes
- kubelet
- kubeadm
- kubectl
sourceStatus: needs-review
draft: false
collection: series
seriesId: kubernetes-cluster
seriesOrder: 30
aliases:
- /series/kubernetes-cluster/03-kubernetes-tools-installation/
- /posts/kubernetes03/
- /study/kubernetes-cluster/03-kubernetes-tools-installation/
---
### 19. 쿠버네티스 설치

1. kubelet, kubeadm, kubectl 패키지 설치
![image](Kubernetes03_01.png)
![image](Kubernetes03_02.png)

    ```shell
    cat <<EOF | sudo tee /etc/apt/sources.list.d/kubernetes.list
    \>  deb https://apt.kubernetes.io/ kubernetes-xenial main
    \> EOF
     deb https://apt.kubernetes.io/
    ```

![image](Kubernetes03_03.png)
![image](Kubernetes03_04.png)

2. 자동으로 업데이트 되지 않도록 패키지의 현재 버전을 고정
![image](Kubernetes03_05.png)

3. kubelet 활성화
![image](Kubernetes03_06.png)

4. containerd 데몬 재실행
![image](Kubernetes03_07.png)
![image](Kubernetes03_08.png)

---

쿠버네티스는 공부할 준비도 빡세다....
