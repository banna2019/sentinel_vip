sentinel_vip

说明：

  通过访问sentinel 端口获取master IP 并与 redis 集群主机各个对比。

对失效的master 原主机删除VIP地址

对新master 主机添加VIP地址

在Sentinel_vip_conf.py 文件中配置redis 的主从的IP和root 及root密码
脚本三秒检测一次sentinel Redis master IP并与Redis IP比较，如果主
Redis服务器IP与sentinel Redis master IP不一致，自动将主Redis
的VIP切换至sentinel Redis master IP所子的Redis

运行：

nohup python Sentinel_vip_conf.py &
将脚本防止后台运行
