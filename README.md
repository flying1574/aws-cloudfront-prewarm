# aws-cloudfront-prewarm
This repository is based anothers cloudfront-repositories, provide 2 different ways for you to prewarm
Local方案:[描述](https://github.com/flying1574/aws-cloudfront-prewarm/tree/main#prewarm-local%E6%8F%8F%E8%BF%B0)|[实施](https://github.com/flying1574/aws-cloudfront-prewarm/tree/main/prewarm-local)
Lambda方案:[描述](https://github.com/flying1574/aws-cloudfront-prewarm/tree/main#prewarm-lambda-%E4%BB%8B%E7%BB%8D)|[代码](https://github.com/flying1574/aws-cloudfront-prewarm/tree/main/prewarm-lambda)
1. **个人更推荐使用local的方式运行，无法正常请求的节点较少,lambda版本可能会有一点资源请求问题**
2. **该代码库的两个方案均来自网上的公开代码库，对其进行修改，重新上传，如有侵权，请联系我删库**
3. **local方案：先修改file.txt，然后运行python prewarm.py**
4. **lambda方案：同上，先修改file.txt，然后sh prewarm.sh**

# Prewarm-local描述

[CloudFront](https://aws.amazon.com/cloudfront) 为 AWS 的 CDN 服务。此脚本用于做 CloudFront 的预热。

CDN 已经为一项成熟且广泛应用的技术，其原理为 CDN POP 节点会缓存用户的请求，当下次附近的终端用户访问时，通过 PoP 点中的缓存直接返回内容，从而提高网站响应速度。
但当文件第一次被请求时，PoP 点是肯定没有缓存这个文件的，仍然需要到源站去请求。因此，首批请求此文件的用户可能会有比较慢的体验，不排除他们选择因此离开页面的可能性。对于一些视频网站来讲，这种痛点往往会更强烈。

此文提出针对解决这个问题的办法，即通过脚本把文件提前缓存到各个PoP点上。它的原理为向您需要的每个Pop点发起请求并做本地下载，请求成功后，此文件就缓存到您选择的这些 Pop 点上了。
对于一些流媒体的视频网站，文件量非常大，通常不需要预热所有的文件，只需要预热新影片片头的一些分片文件即可。

## 前提条件        
1. 请先保证您的 CloudFront 配置正确，如源，权限等，确保 CloudFront 首先能够正常的对外提供 web 服务的加载。
1. 如果是普通静态缓存，请务必注意在 **行为** 这一tab中，配置对象缓存为自定义标头，否则如果在 request 当中没有添加 Cache-Control 的情况下，**CloudFront每次都会重新回源拿object**，预热是无效的。详细信息请参考[此官方文档的解释](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/Expiration.html)     
   ![](img/customized-header.png)
1. 中国区的 CloudFront，务必要添加备案过的 CNAME 才可以正常创建 distribution。
1. **此脚本无法保证 100% 的对象可以缓存成功**。   
   
## 原理    
普通的 CloudFront 请求会始终被路由到离用户最近的 PoP 点，因此您在本地的请求，只会预热到一个单一的 PoP 点上。
此脚本通过像指定的 POP 点发起请求的方式，直接将请求 request 到对应的PoP点上，因此您只需要一台 PC，就可以实现多节点的预热。
为了确保 cloudfront 可以成功的cache对象文件，此脚本会完整的下载您的对象文件并且在完成后自动删除掉。

## 适用场景    
1. 新上线的视频文件的开头分片文件
1. 新上线网站的一些图片/css文件等
1. 其他希望提前缓存住特定对象的场景。

## 使用方法     
**1. 根据需求选择 PoP点**           
根据自己的需求，选择 PoP 点。CloudFront 在中国有4个节点（北京，宁夏中卫，深圳，上海），但在海外有 200+ 个节点，当我们做预热时，其实不需要将每个节点都预热到，只需要预热我们需要针对的终端用户所在位置即可。
比如如果您的 target user 为东南亚，只需要预热东南亚部分；同理，如果 target 在美国，只需要预热美国节点。
AWS 官方虽然没有对应的页面列出所有的 PoP 点的 code，但从一些第三方网站如[此网站](https://www.feitsui.com/zh-hans/article/3) 可以找到。
**该脚本已经修改，无需额外定义pops的信息，默认请求所有区域的pop**
> 注：中国区 Cloudfront 请用中国区的 POP Code，海外区 Cloudfront 请用海外的 PoP Code 

**2. 定义所需要预热的路径**     
   在 file.txt 中列出文件路径，或者是完整的访问连接。如：

   ```
   /abc.mp4
   /abc.jpg
   ```
   或
   ```
   /btt1/2020/03/20200303/QoQQjVr1/2000kb/hls/XoLJyjuz.ts
   /btt1/2020/03/20200303/QoQQjVr1/2000kb/hls/1P5WgkfH.ts
   ```

或者是
   ```
   https://example.com/btt1/2020/03/20200303/QoQQjVr1/2000kb/hls/XoLJyjuz.ts
   https://example.com/btt1/2020/03/20200303/QoQQjVr1/2000kb/hls/1P5WgkfH.ts
   ```

**3. 参数定义**     
在 ``__prewarm_update.py`` 中修改以下参数为您自己的参数。
```
# 您的实际的自定义域名。如果您有CNAME,则填写您的实际CNAME(xxx.example.com)，如无，则domain是xxx.cloudfront.net
# 另外，中国区的Cloudfront，只能填写备案过的CNAME名称，否则无法正常创建distribution
domain = "example.com"  or 'xxxxxx.cloudfront.net'
cdn_name = 'xxxxxx.cloudfront.net'
```

另外还有一处 ``f1=open("test.jpg", "wb")``，此处如果您的对象文件尾缀固定，可以相应的修改您的对象文件为正确的尾缀内容。如果不固定则忽略。

**4.运行脚本**    
通过 ```python3 prewarm.py``` 运行此脚本。

**5.检查日志**     
脚本会产生两个日志，一个是result.csv，完整记录每个请求的response；另一个是no_ip_file.csv，记录没有被成功解析的请求。
如果在请求当中出现了'miss from cloudfront', 则此 object 没有成功预热，可以重新运行脚本单独重新请求这些文件。

## 说明
1. **此脚本无法保证 100% 的对象可以缓存成功**。
1. 请勿滥用资源，合理的将需要集中访问的文件打到 PoP 点即可，不需要的资源，不必预热。


## 自定义
如果您的 list 文件不同于样例中所示的格式，或者您有其它自定义要求，可以根据此脚本加以自定制。


# Prewarm-lambda 介绍
# 利用Lambda进行Amazon CloudFront预热

## Amazon CloudFront介绍
Amazon CloudFront 是一项快速内容分发网络 (CDN) 服务，可以安全地以低延迟和高传输速度向全球客户分发数据、视频、应用程序和 API，全部都在开发人员友好的环境中完成。Amazon CloudFront 可以大幅扩容，并在全球范围内分布。CloudFront 网络拥有 225 个以上的存在点 (PoP)，这些存在点通过 AWS 主干网相互连接，为最终用户提供超低延迟性能和高可用性。

## 为什么需要预热
通过预热功能，您可以强制CDN节点回源并获取最新文件。通过预热功能您可以在业务高峰前预热热门资源，提高资源访问效率。通过本文您可以了解预热功能的配置方法。

## 功能简介
通过Lambda可以帮助您分批进行预热任务，对比本地脚本的方式，可以异步、高并发执行预热任务，也可以很容易的结合CI/CD平台提交预热作业。当您指定预热URL列表文件后，本地shell脚本读取文件列表中需要预热的文件，并发提交到Lambda进行预热，对于有需要大批量文件的预热任务可以更高效的完成。

•	预热的文件过多，本地提交效率低。

•	本地部署脚本提交预热任务，运维成本高。

## 使用说明
### 1、	创建预热资源列表
在文件列表中，加入需要预热的文件URL，假设你有三个文件需要预热，则在file.txt里面填入如下内容
```Bash
/www/a.txt

/www/b.txt

/www/c.txt
```

### 2、	在Lambda中部署预热脚本

2.1 默认函数名称：cloudfront_prewarm

2.2 默认运行时：python3.11

2.3 在基本设置中，默认给出1024MB内存以及15分钟超时时间

### 3、	执行本地脚本开始预热并查看日志
**填入函数执行角色的arn以及cloudfront的域名**
```Bash
sh cf_prewarm.sh 
```
预热的日志可以在cloudwatch log中查看，当看到

```Bash
SUCCESS: POP:EWR50-C1 FILE:http://d1zi40b7x5dwgb.EWR50-C1.cloudfront.net/www/a.txt
```

代表在EWR50-C1的PoP点上已经预热成功

### 5、	备注
第三方CloudFront pop点列表 https://www.feitsui.com/zh-hans/article/3


# 引用来源
1. prewarm-lambda: https://github.com/xiangqua/cloudfront-lambda-prewarm/tree/main
2. prewarm-local: https://github.com/nwcdheap/cloudfront-prewarm


