# sentinel_vip

通过访问sentinel 端口获取master IP 并与 redis 集群主机各个对比。
对失效的master 原主机删除VIP地址，对新master 主机添加VIP地址。