Sentinel_vip

  这是一款补足Redis sentinel 服务能自动切换redis 主从状态，做VIP切换的功能脚本。可以很好监测sentinel做VIP漂移，方便应用配置Redis VIP地址，
应用不用因为主从Redis因主漂移至从需要修改IP,仅要配置VIP即可。

说明：

  通过访问sentinel 端口获取master IP 并与 redis 集群主机各个对比。对失效的master 原主机删除VIP地址

  对新master 主机添加VIP地址，主从Redis切换由sentinel服务负责，本脚本自动监测sentinel服务内Redis状态进行切换

  在Sentinel_vip_conf.py 文件中配置redis 的主从的IP和root 及root密码脚本三秒检测一次sentinel Redis master IP并与Redis IP比较，如果主Redis服务器IP与sentinel Redis master IP不一致，自动将主Redis的VIP切换至sentinel Redis master IP所在的Redis

准备：
   
   首先配好两台Redis主从服务器，然后在各个主从服务器配置好Sentinel的服务，在两台Redis 主从服务器启动Sentinel的服务。
   配置Sentinel_vip_conf.py文件，将主从IP地址和系统用户密码写入该文件。

运行：

  nohup python Sentinel_vip.py &   #将脚本放后台运行
