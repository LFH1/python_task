# python_task

#### 介绍
给定一个某系统运行的实际日志文件(trace_analysis.log)，该文件是一个文本文件，每一行记录了一条系统运行时打印的日志，用python编写一个程序对该日志文件内特定的内容进行分析，评估该流式调度系统的如下三项指标，并以json格式输出到result.json文件中。
1. 各工序的耗时
ProcessA和ProcessB的平均耗时/P99耗时/P90耗时 （注意：以帧号为主key来汇集信息）
2. 系统平均吞吐量
系统每秒可处理多少相机帧，单位frames/second；可从整体上统计出有效处理的相机帧数和系统运行时间（注意：因为存在丢帧现象，帧号并不保障严格+1递增）。
3. 平均帧
  每帧的耗时定义为：从ProcessA开始时间到ProcessB工序结束的时间（注意：不能简单将ProcessA耗时 + ProcessB耗时，原因为ProcessA工序结束时间和ProcessB工序开始时间，可能会被其它任务抢占资源）。

进阶练习（选做）
基于plot库绘制ProcessA和ProcessB的调度时序图（下图仅供参考），评估流式调度效率和性能热点。